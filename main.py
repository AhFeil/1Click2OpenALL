from enum import StrEnum
from typing import Annotated, Literal, Optional
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

import hanota
import html2md
from config_handle import config
from oneclickopen import extract_urls, do_open

app = FastAPI()
app.include_router(html2md.router)
app.include_router(hanota.router)

templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    # 获取浏览器的语言偏好
    user_language = request.headers.get('Accept-Language', 'en').split(',')[0]
    # 简单判断是否以中文开头，决定显示的文本
    if user_language.startswith('zh'):
        message = "如果是第一次使用，点击我以授权弹窗权限"
    else:
        message = "IF First use, then click me to Acquire Pop Up"
    context = {"message_of_pop_up": message, "cap_api_endpoint": f"{config.cap_instance_url}/{config.site_key}/"}
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@app.get('/acquire_pop_up', response_class=HTMLResponse)
async def acquire_pop_up(request: Request):
    """获取弹窗权限"""
    return templates.TemplateResponse(request=request, name='acquire_pop_up.html')

class WebsiteLines(BaseModel):
    content: str
    ask_for: Literal["open", "get_md"]
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
        case _:
            raise HTTPException(status_code=404)
    return templates.TemplateResponse(request=request, name='open_websites.html', context=context | {"ask_for": websites.ask_for})


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
