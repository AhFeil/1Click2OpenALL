import re


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

def do_open(lang: str, link_list: list[str], lines_without_url: list[str]) -> dict:
    context = {
        "websites": link_list,
        "lines_without_url": lines_without_url,
        "valid_title": "上次输入里有效的网址：" if lang.startswith('zh') else "Last entered websites:",
        "invalid_title": "不包含网址的行：" if lang.startswith('zh') else "The lines that do not contain any URL:"
    }
    return context
