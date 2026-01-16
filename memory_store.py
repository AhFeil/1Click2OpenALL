import io
import time
from urllib.parse import quote

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from fastapi import APIRouter


# 时间戳: (文件名，内容)
tmp_file: dict[int, tuple[str, io.BytesIO]] = {}

# 清理超过 10 分钟的临时文件
def cleanup_old_files():
    now = int(time.time() * 1000)
    expired = [fid for fid, _ in tmp_file.items() if now - fid > 10 * 60 * 1000]
    for fid in expired:
        del tmp_file[fid]


def store_item(name: str, item: io.BytesIO) -> int:
    file_id = int(time.time() * 1000)
    tmp_file[file_id] = (name, item)
    return file_id


def pop_item(file_id: int) -> tuple[str, io.BytesIO | None]:
    return tmp_file.pop(file_id, ("", None))


router = APIRouter()

@router.get('/download/{file_id}', response_class=StreamingResponse)
async def download(file_id: int):
    filename, buffer = pop_item(file_id)
    if not buffer:
        raise HTTPException(status_code=404)
    media_type = "text/markdown" if filename.endswith(".md") else "application/zip"
    content_disposition = f"attachment; filename*=UTF-8''{quote(filename)}"
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": content_disposition}
    )
