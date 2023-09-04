from flask import Flask, render_template, request
from urllib.parse import urlparse

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/open_websites', methods=['POST'])
def open_websites():
    websites = request.form.get('websites')  # 获取表单中的网址
    website_list = websites.split('\n')  # 将多行网址拆分为列表

    # 处理网址，确保它们是完整的URL
    for i in range(len(website_list)):
        parsed_url = urlparse(website_list[i])
        if not parsed_url.scheme:
            website_list[i] = "http://" + website_list[i]

    return render_template('open_websites.html', websites=website_list)


if __name__ == '__main__':
    app.run()






# from flask import Flask, render_template, request
# import webbrowser
#
# app = Flask(__name__)
#
# @app.route('/')
# def index():
#     return render_template('index-system.html')
#
# @app.route('/open_websites', methods=['POST'])
# def open_websites():
#     websites = request.form.get('websites')  # 获取表单中的网址
#     website_list = websites.split('\n')  # 将多行网址拆分为列表
#     for website in website_list:
#         webbrowser.open_new_tab(website.strip())  # 打开每个网址
#     return 'Success'
#
# if __name__ == '__main__':
#     app.run()
