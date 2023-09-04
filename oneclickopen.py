from flask import Flask, render_template, request, session
from urllib.parse import urlparse

app = Flask(__name__)

# 设置应用的密钥，用于会话数据加密，复杂随机即可，实际生产环境需要从外面引入，以防泄露
app.secret_key = 'dwSR3bXYXcL^G!NiGV'


@app.route('/')
def index():
    websites = session.get('websites', [])  # 获取会话中的网址列表
    return render_template('index.html', websites=websites)


@app.route('/open_websites', methods=['POST'])
def open_websites():
    websites = request.form.get('websites')  # 获取表单中的网址
    website_list = websites.split('\n')  # 将多行网址拆分为列表
    website_list = [url.strip() for url in website_list if url.strip()]  # 去除空行
    
    # 处理网址，确保它们是完整的URL
    for i in range(len(website_list)):
        parsed_url = urlparse(website_list[i])
        if not parsed_url.scheme:
            website_list[i] = "http://" + website_list[i]

    # 更新会话中的网址列表
    session['websites'] = website_list

    return render_template('open_websites.html', websites=website_list)


if __name__ == '__main__':
    app.run()
