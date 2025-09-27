import asyncio
import io
import zipfile
import time
from pathlib import Path
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import APIRouter

from captcha import verify_captcha
from config_handle import config


headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'cache-control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-platform': '"Windows"',
}

async def download_and_convert(url) -> tuple[str, str]:
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml') # TODO
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "默认标题"

        markdown = convert_to_markdown(response.text)

        return title, markdown

async def download_all(urls) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    urls = tuple(urls)

    finished_url, failed_url = [], []
    data: list[tuple[str,str]] = []
    # todo 对同一域名下的网站，不并发访问，避免对网站造成压力
    for i, url in enumerate(urls, start=1):
        try:
            title, markdown = await download_and_convert(url)
            data.append((title, markdown))
        except Exception as e:
            print(e)
        else:
            print("finish to download and convert", title)
            finished_url.append(url)
            if i < len(urls):
                await asyncio.sleep(20)
    if failed_url:
        print("failed to finish url:", failed_url)
    return data, finished_url, failed_url

def create_zip_or_md(data: list[tuple[str, str]]) -> tuple[str, io.BytesIO]:
    """将标题+内容这种列表转为多个 .md 文件，并压缩为 zip 包（在内存中完成）"""
    buffer = io.BytesIO()
    if len(data) == 1:
        filename = data[0][0] + ".md"
        buffer.write(data[0][1].encode('utf-8'))
    else:
        filename = "oneclick2getmd.zip"
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_STORED) as zip_file:
            for title, content in data:
                # 清理文件名：移除不合法字符，避免文件系统问题
                # safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
                # if not safe_title:
                    # safe_title = "untitled"
                zip_file.writestr(title + ".md", content.encode('utf-8'))

    buffer.seek(0)
    return filename, buffer

async def download_and_save_all(urls, out_dir):
    out_dir = Path(out_dir)
    if not out_dir.exists():
        raise RuntimeError(f"{out_dir} doesn't exist")
    res, _, _ = await download_all(urls)
    for title, markdown in res:
        output_file = out_dir / (title + ".md")
        output_file.write_text(markdown)

# 索引: (文件名, 内容)
tmp_file: dict[int, tuple[str, io.BytesIO]] = {}

# 清理超过 10 分钟的临时文件
def cleanup_old_files(now: int):
    expired = [fid for fid, _ in tmp_file.items() if now - fid > 10 * 60 * 1000]
    for fid in expired:
        del tmp_file[fid]


async def do_convert(lang: str, link_list: list[str], lines_without_url: list[str], cap_token: str | None) -> dict | HTMLResponse:
    if config.cap_instance_url:
        if not cap_token:
            return HTMLResponse("<h3>你必须先验证才能使用</h3>")
        result = await verify_captcha(config.cap_instance_url, config.site_key, config.key_secret, cap_token)
        if not result:
            return HTMLResponse("<h3>验证出错</h3>")
    if len(link_list) > 3:
        return HTMLResponse("<script>alert('limitation: less than or equal to 3');</script>")

    res, finished_url, failed_url = await download_all(link_list)
    if finished_url:
        filename, buffer = create_zip_or_md(res)
        file_id = int(time.time() * 1000)
        # 检查删除旧的文件
        cleanup_old_files(file_id)
        tmp_file[file_id] = (filename, buffer)
    else:
        file_id = 0
    context = {
        "websites": finished_url,
        "lines_without_url": failed_url + lines_without_url,
        "valid_title": "获取到 md 的网址：",
        "invalid_title": "没有获取到 md 的网址和不包含网址的行：",
        "file_id": file_id,
    }
    return context

router = APIRouter()

@router.get('/download/{id}', response_class=StreamingResponse)
async def download(id: int):
    filename, buffer = tmp_file.pop(id, ("", None))
    if not buffer:
        raise HTTPException(status_code=404)
    media_type = "text/markdown" if filename.endswith(".md") else "application/zip"
    content_disposition = f"attachment; filename*=UTF-8''{quote(filename)}"
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": content_disposition}
    )


if __name__ == "__main__":
    import os
    import argparse
    parser = argparse.ArgumentParser(description="Your script description")
    parser.add_argument('--urls_file', required=False, default='urls.txt', help='File contains urls')
    parser.add_argument('--out_dir', required=False, default='./', help='where to save file')
    parser.add_argument('--proxy', required=False, default='', help='input like 127.0.0.1:10808')
    args = parser.parse_args()
    if args.proxy:
        os.environ["http_proxy"] = f"http://{args.proxy}"
        os.environ["https_proxy"] = f"http://{args.proxy}"
    with open(args.urls_file, 'r', encoding="utf-8") as f:
        urls = f.readlines()
    task = download_and_save_all((url for url_line in urls if (url := url_line.strip())), args.out_dir)
    asyncio.run(task)

    # uv run html2md.py --urls_file ./dl_md.txt --out_dir ./md
