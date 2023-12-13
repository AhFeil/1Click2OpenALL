from flask import Flask, render_template, request, session
from urllib.parse import urlparse
import re


def extract_urls(text):
    pattern = r'\[.*?\]\((.*?)\)'  # 正则表达式模式，匹配 [任意字符](网址)
    urls = re.findall(pattern, text)  # 在文本中查找所有匹配的网址
    return urls


app = Flask(__name__)

# 设置应用的密钥，用于会话数据加密，复杂随机即可，实际生产环境需要从外面引入，以防泄露
app.secret_key = 'dwSR3bXYXcL^G!NiGV'


@app.route('/')
def index():
    websites = session.get('websites', [])  # 获取会话中的网址列表
    return render_template('index.html', websites=websites)


@app.route('/open_websites', methods=['POST'])
def open_websites():
    website_content = request.form.get('websites')  # 获取表单中的文本
    website_content_list = website_content.split('\n')  # 将多行文本拆分为列表
    website_content_list = [url.strip() for url in website_content_list if url.strip()]  # 去除空行
    website_list = []   # 存放真正的网址
    
    # 处理网址，
    for i in range(len(website_content_list)):
        # 如果是 md 格式，则可以提取出网址链接
        url_list = extract_urls(website_content_list[i])
        if url_list:
            website_list.extend(url_list)
        else:
            # 若不匹配 md，则认为是纯网址，确保它们是完整的URL
            parsed_url = urlparse(website_content_list[i])
            if not parsed_url.scheme:
                website_content_list[i] = "http://" + website_content_list[i]
            website_list.append(website_content_list[i])

    # 更新会话中的网址列表
    session['websites'] = website_list

    return render_template('open_websites.html', websites=website_list)


if __name__ == '__main__':
    app.run()
