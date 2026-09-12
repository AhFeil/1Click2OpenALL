from enum import StrEnum
from typing import Annotated, Literal, Optional
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

import hanota
import memory_store
import html2md
import word2anki
from config_handle import config
from oneclickopen import extract_urls, extract_lines, do_open
from email_extract import extract_emails, extract_email_domains

app = FastAPI()
app.include_router(memory_store.router)
app.include_router(hanota.router)
app.include_router(word2anki.router)

templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    client_ip = request.headers.get("x-real-ip")
    # 如果 X-Real-IP 不存在，回退到直接连接的客户端地址
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"

    # 获取浏览器的语言偏好
    user_language = request.headers.get('Accept-Language', 'en').split(',')[0]
    # 简单判断是否以中文开头，决定显示的文本
    if user_language.startswith('zh'):
        message = "如果是第一次使用，点击我以授权弹窗权限"
    else:
        message = "IF First use, then click me to Acquire Pop Up"
    context = {"message_of_pop_up": message, "cap_api_endpoint": f"{config.cap_instance_url}/{config.site_key}/", "client_ip": client_ip}
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@app.get('/acquire_pop_up', response_class=HTMLResponse)
async def acquire_pop_up(request: Request):
    """获取弹窗权限"""
    return templates.TemplateResponse(request=request, name='acquire_pop_up.html')

@app.get('/email/', response_class=HTMLResponse)
async def email_page(request: Request):
    """提取邮箱页面"""
    return templates.TemplateResponse(request=request, name='email_extract.html')

class EmailLines(BaseModel):
    content: str
    mode: Literal["email", "domain"] = "email"
    exclude: str = ""

@app.post('/email/', response_class=HTMLResponse)
async def email_extract(request: Request, form: Annotated[EmailLines, Form()]):
    """提取邮箱或邮箱域名"""
    if form.mode == "domain":
        result = extract_email_domains(form.content, form.exclude)
    else:
        result = extract_emails(form.content, form.exclude)
    context = {"result": result, "mode": form.mode, "content": form.content, "exclude": form.exclude}
    return templates.TemplateResponse(request=request, name='email_extract.html', context=context)


class WebsiteLines(BaseModel):
    content: str
    ask_for: Literal["open", "get_md", "make_card"]
    cap_token: Optional[str]= Field(default=None, alias='cap-token')

@app.post('/do_it')
async def do_it(request: Request, websites: Annotated[WebsiteLines, Form()]):
    lang = request.headers.get('Accept-Language', 'en').split(',')[0]
    link_list, lines_without_url = extract_urls(websites.content)
    match websites.ask_for:
        case "open":
            context = do_open(lang, link_list, lines_without_url)
        case "get_md":
            context = await html2md.do_convert(lang, link_list, lines_without_url, websites.cap_token)
            if isinstance(context, HTMLResponse):
                return context
        case "make_card":
            context = await word2anki.do_convert(lang, list(extract_lines(websites.content)), websites.cap_token)
            if isinstance(context, HTMLResponse):
                return context
        case _:
            raise HTTPException(status_code=404)
    return templates.TemplateResponse(request=request, name='open_websites.html', context=context | {"ask_for": websites.ask_for})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(path="templates/favicon.ico", filename="favicon.ico")

class AdditionalPage(StrEnum):
    robots = "robots.txt"
    sitemap = "sitemap.xml"

additional_pages = {
    item.value: Path(f"templates/{item.value}").read_text(encoding="utf-8")
    for item in AdditionalPage
}

@app.get("/{file}", response_class=PlainTextResponse)
async def static_from_root(file: AdditionalPage):
    return additional_pages[file.value]


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=7500)
