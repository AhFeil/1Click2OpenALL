from flask import Flask, render_template, request, session
from urllib.parse import urlparse
import re


def extract_urls(text):
    pattern = r'\[.*?\]\((.*?)\)'  # 正则表达式模式，匹配 [任意字符](网址)
    urls = re.findall(pattern, text)  # 在文本中查找所有匹配的网址
    return urls

# 定义一个函数，用于判断输入的字符串是否是合法的网址
def is_valid_url(input_string):
    url_pattern = r'^(https?:\/\/)?[^.\s]+(\.[^.\s]+)+[^\s]$'
    ip_address_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'

    if re.match(url_pattern, input_string) or re.match(ip_address_pattern, input_string):
        return True
    else:
        return False


app = Flask(__name__)

# 设置应用的密钥，用于会话数据加密，复杂随机即可，实际生产环境需要从外面引入，以防泄露
app.secret_key = 'dwSR3bXYXcL^G!NiGV'


@app.route('/')
def index():
    websites = session.get('websites', [])  # 获取会话中的网址列表
    return render_template('index.html', websites=websites)


@app.route('/acquire_pop_up')
def acquire_pop_up():
    """获取弹窗权限"""
    return render_template('acquire_pop_up.html')


@app.route('/open_websites', methods=['POST'])
def open_websites():
    website_content = request.form.get('websites')  # 获取表单中的文本
    website_content_list = website_content.split('\n')  # 将多行文本拆分为列表
    website_content_list = [url.strip() for url in website_content_list if url.strip()]  # 去除空行
    website_list = []   # 存放真正的网址
    
    # 处理网址，
    for i in range(len(website_content_list)):
        one_line = website_content_list[i]
        # 如果是 md 格式，则可以提取出网址链接
        url_list = extract_urls(one_line)
        if url_list:
            website_list.extend(url_list)
        elif is_valid_url(one_line):   # 若不匹配 md，检查是否是单个 URL
            parsed_url = urlparse(one_line)
            if not parsed_url.scheme:
                one_line = "http://" + one_line
            website_list.append(one_line)
        else:
            pass

    # 更新会话中的网址列表
    session['websites'] = website_list

    return render_template('open_websites.html', websites=website_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # 测试用
    # if is_valid_url("baidu.com"):
    #     print("URL 匹配成功!")
    # else:
    #     print("URL 不匹配")
