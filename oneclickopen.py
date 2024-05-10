import os
import re

from typing import Annotated

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

# 自定义跟踪代码
track_js_codes_file = "templates/track.txt"
if os.path.exists(track_js_codes_file):
    with open(track_js_codes_file, 'r', encoding='utf-8') as f:
        track_js_codes = f.read()
else:
    track_js_codes = ""


def extract_urls_from_md(text):
    # 提取 md 中的网址
    md_url_pattern = r'\[.*?\]\((.*?)\)'  # 正则表达式模式，匹配 [任意字符](网址)
    urls = re.findall(md_url_pattern, text)  # 在文本中查找所有匹配的网址
    return urls

def extract_urls_by_pattern(input_string):
    # 用正则根据模式提取网址
    url_pattern = r'https?://[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*(?:/[^\s]+)?'
    urls = re.findall(url_pattern, input_string)
    return urls

extract_funcs = [extract_urls_from_md, extract_urls_by_pattern]

def is_valid_url(input_string):
    pass

def is_chinese_char(char):
    # 汉字的Unicode范围
    return '\u4e00' <= char <= '\u9fff'


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
    context = {"message_of_pop_up": message, "track_js_codes": track_js_codes}
    return templates.TemplateResponse(request=request, name="index.html", context=context)


@app.get('/acquire_pop_up', response_class=HTMLResponse)
async def acquire_pop_up(request: Request):
    """获取弹窗权限"""
    return templates.TemplateResponse(request=request, name='acquire_pop_up.html')


@app.post('/open_websites', response_class=HTMLResponse)
async def open_websites(request: Request):
    """返回打开网页的 js 代码"""
    forms = await request.form()
    try:
        content = forms['websites']  # 获取表单中的文本
        if not content:
            return 
    except ValueError:
        content = ""
        return {"state": False}

    str_list = content.split('\n')  # 将多行文本拆分为列表
    str_list = (stripped for line in str_list if (stripped := line.strip()))  # 去除空行
    
    link_list = []   # 存放真正的网址
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
            if not is_chinese_char(one_line[0]):
                # 汉字的都不要
                link_list.append("http://" + one_line)

    # for link in link_list:
    #     is_valid_url(link)

    return templates.TemplateResponse(request=request, name='open_websites.html', context={"websites": link_list})


from enum import Enum

class Additional_Page(Enum):
    robots = "robots.txt"
    sitemap = "sitemap.xml"

@app.get("/{file}", response_class=PlainTextResponse)
async def static_from_root(file: Additional_Page):
    with open(os.path.join("templates", file.value), 'r', encoding="utf-8") as f:
        content = f.read()
    return content



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7500)

