import os
import re

from flask import Flask, send_from_directory, render_template, request, session

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

def extract_urls(input_string):
    # 提取网址
    url_pattern = r'https?://[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*(?:/[^\s]+)?'
    urls = re.findall(url_pattern, input_string)
    return urls

def is_valid_url(input_string):
    pass

def is_chinese_char(char):
    # 汉字的Unicode范围
    return '\u4e00' <= char <= '\u9fff'


app = Flask(__name__)

# 设置应用的密钥，用于会话数据加密，复杂随机即可，实际生产环境需要从外面引入
app.secret_key = os.environ.get('oneClick2OpenALL_SECRET', 'dwSR3bXYXcL^G!NiGV')


@app.route('/')
def index():
    # 获取浏览器的语言偏好
    user_language = request.headers.get('Accept-Language', 'en').split(',')[0]
    # 简单判断是否以中文开头，决定显示的文本
    if user_language.startswith('zh'):
        message = "如果是第一次使用，点击我以授权弹窗权限"
    else:
        message = "IF First use, then click me to Acquire Pop Up"
    # 获取会话中的网址列表
    websites = session.get('websites', [])
    return render_template('index.html', websites=websites, message_of_pop_up=message, track_js_codes=track_js_codes)


@app.route('/acquire_pop_up')
def acquire_pop_up():
    """获取弹窗权限"""
    return render_template('acquire_pop_up.html', track_js_codes=track_js_codes)


@app.route('/open_websites', methods=['POST'])
def open_websites():
    content = request.form.get('websites')  # 获取表单中的文本
    str_list = content.split('\n')  # 将多行文本拆分为列表
    str_list = [stripped  for line in str_list if (stripped := line.strip())]  # 去除空行
    
    link_list = []   # 存放真正的网址
    extract_funcs = [extract_urls_from_md, extract_urls]
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

    # 更新会话中的网址列表
    session['websites'] = link_list

    return render_template('open_websites.html', websites=link_list)


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory("./templates", request.path[1:])



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7500)

