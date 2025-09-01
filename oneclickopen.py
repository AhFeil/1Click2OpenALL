import io
import os
import re
import time
from typing import Annotated, Literal

import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from html2md import download_all, create_zip_from_markdown_data

# 自定义跟踪代码
track_js_codes_file = "templates/track.txt"
track_js_codes = ""
if os.path.exists(track_js_codes_file):
    with open(track_js_codes_file, 'r', encoding='utf-8') as f:
        track_js_codes = f.read()

ad_file = "templates/ad.html"
ad_html = ""
if os.path.exists(ad_file):
    with open(ad_file, 'r', encoding='utf-8') as f:
        ad_html = f.read()


def extract_urls_from_md(text):
    # 提取 md 中的网址
    md_url_pattern = r'\[.*?\]\((.*?)\)'  # 正则表达式模式，匹配 [任意字符](网址)
    urls = re.findall(md_url_pattern, text)  # 在文本中查找所有匹配的网址
    return urls

def extract_urls_by_pattern(input_string):
    # 用正则根据模式提取网址
    url_pattern = r'https?://(?:[^:@\s]+(?::[^:@\s]*)?@)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*(?::[0-9]+)?(?:/[^\s]*)?'
    urls = re.findall(url_pattern, input_string)
    return urls

extract_funcs = [extract_urls_from_md, extract_urls_by_pattern]

def is_chinese_char(char):
    # 汉字的 Unicode 范围
    return '\u4e00' <= char <= '\u9fff'

def contains_zh_colon_in_domain(url):
    domain = url.split("/")[0]
    return '：' in domain

def is_invalid_url(input_string):
    # 由汉字开头的都不要
    if is_chinese_char(input_string[0]):
        return True
    # 域名部分含有中文冒号 ：
    if contains_zh_colon_in_domain(input_string):
        return True
    return False

def extract_urls(content: str) -> tuple[list[str], list[str]]:
    str_list = filter(None, map(str.strip, content.split('\n')))  # 将多行文本拆分为列表并去除空行

    link_list = []   # 存放真正的网址
    lines_without_url = []   # 那些没有从中获得网址的一行
    # 提取网址
    for one_line in str_list:
        for extract_func in extract_funcs:
            # 按顺序，用不同模式寻找网址
            url_list = extract_func(one_line)
            # 如果找到就直接退出，没找到就换下一个模式去匹配
            if url_list:
                link_list.extend(url_list)
                break
        else:
            # 如果不是由 break 打断退出，说明上面都没匹配，此时认为一行就是一个纯网址
            # 如果可以肯定不是合法网址，那就保存一下
            if is_invalid_url(one_line):
                lines_without_url.append(one_line)
            else:
                link_list.append("http://" + one_line)
    return link_list, lines_without_url

app = FastAPI()
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
    # 获取会话中的网址列表
    # websites = session.get('websites', [])
    context = {"message_of_pop_up": message, "ad_html": ad_html, "track_js_codes": track_js_codes}
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@app.get('/acquire_pop_up', response_class=HTMLResponse)
async def acquire_pop_up(request: Request):
    """获取弹窗权限"""
    return templates.TemplateResponse(request=request, name='acquire_pop_up.html')

tmp_file: dict[int, io.BytesIO] = {}

# 清理超过 10 分钟的临时文件
def cleanup_old_files(now: int):
    expired = [fid for fid, _ in tmp_file.items() if now - fid > 10 * 60 * 1000]
    for fid in expired:
        del tmp_file[fid]

class WebsiteLines(BaseModel):
    content: str
    ask_for: Literal["open", "get_md"]

@app.post('/do_it')
async def do_it(request: Request, websites: Annotated[WebsiteLines, Form()]):
    user_lang = request.headers.get('Accept-Language', 'en').split(',')[0]
    link_list, lines_without_url = extract_urls(websites.content)
    match websites.ask_for:
        case "open":
            context = {
                "websites": link_list,
                "lines_without_url": lines_without_url,
                "valid_title": "上次输入里有效的网址：" if user_lang.startswith('zh') else "Last entered websites:",
                "invalid_title": "不包含网址的行：" if user_lang.startswith('zh') else "The lines that do not contain any URL:"
            }
        case "get_md":
            if len(link_list) > 3:
                return HTMLResponse("<script>alert('limitation: less than or equal to 3');</script>")
            res, finished_url, failed_url = await download_all(link_list)
            if finished_url:
                zip_buffer = create_zip_from_markdown_data(res)
                file_id = int(time.time() * 1000)
                # 检查删除旧的文件
                cleanup_old_files(file_id)
                tmp_file[file_id] = zip_buffer
            else:
                file_id = 0
            context = {
                "websites": finished_url,
                "lines_without_url": failed_url + lines_without_url,
                "valid_title": "获取到 md 的网址：",
                "invalid_title": "没有获取到 md 的网址和不包含网址的行：",
                "file_id": file_id,
            }
        case _:
            raise HTTPException(status_code=404)
    return templates.TemplateResponse(request=request, name='open_websites.html', context=context | {"ask_for": websites.ask_for}) # 返回打开网页的 js 代码


@app.get('/download/{id}', response_class=StreamingResponse)
async def download(id: int):
    zip_buffer = tmp_file.pop(id, None)
    if not zip_buffer:
        raise HTTPException(status_code=404)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=oneclick2getmd.zip"}
    )

from enum import StrEnum

class Additional_Page(StrEnum):
    robots = "robots.txt"
    sitemap = "sitemap.xml"

@app.get("/{file}", response_class=PlainTextResponse)
async def static_from_root(file: Additional_Page):
    with open(os.path.join("templates", file.value), 'r', encoding="utf-8") as f:
        content = f.read()
    return content


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7500)
