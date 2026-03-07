from io import BytesIO

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import genanki

from config_handle import config
from captcha import verify_captcha
from memory_store import cleanup_old_files, store_item


router = APIRouter(prefix="/word2anki")

templates = Jinja2Templates(directory='templates')


def generate_anki_cards(words: list[str]) -> list[dict]:
    """
    将单词列表转换为 Anki Card 列表

    Args:
        words: 单词列表

    Returns:
        包含各字段的 Anki Card 列表
    """
    cards = []
    for word in words:
        # TODO: 补充获取音标、基本释义、图片、例句翻译的逻辑
        cards.append({
            "单词": word,
            "音标": "",
            "基本释义": "",
            "图片": "",
            "例句1": "",
            "例句翻译1": "",
            "例句2": "",
            "例句翻译2": "",
            "例句3": "",
            "例句翻译3": "",
        })
    return cards


def create_anki_deck(cards: list[dict], deck_name: str = "Word Deck") -> genanki.Deck:
    """
    创建 Anki 卡组

    Args:
        cards: Anki Card 列表
        deck_name: 卡组名称

    Returns:
        genanki.Deck 对象
    """
    deck_id = hash(deck_name) % (2 ** 31 - 1)
    deck = genanki.Deck(deck_id, deck_name)

    model_id = hash("Word Model") % (2 ** 31 - 1)
    model = genanki.Model(
        model_id,
        "Word Model",
        fields=[
            {"name": "单词"},
            {"name": "音标"},
            {"name": "基本释义"},
            {"name": "图片"},
            {"name": "例句1"},
            {"name": "例句翻译1"},
            {"name": "例句2"},
            {"name": "例句翻译2"},
            {"name": "例句3"},
            {"name": "例句翻译3"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": """<div style="font-size:50px;font-family:arial black">{{单词}}</div>
<div style="font-size:15px; color: blue;">{{音标}}</div>""",
                "afmt": """{{FrontSide}}
<hr id=answer>
<br>
<div style="color:purple;">{{基本释义}}</div>
<br>
<br>
{{图片}}
<br>
<br>
<div style="color:#00ffaa">{{例句1}}</div>
<br>
<div style="color:#666">{{例句翻译1}}</div>
<br>
<br>
<div style="color:#00ffaa">{{例句2}}</div>
<br>
<div style="color:#666">{{例句翻译2}}</div>
<br>
<br>
<div style="color:#00ffaa">{{例句3}}</div>
<br>
<div style="color:#666">{{例句翻译3}}</div>""",
            },
        ],
    )

    for card in cards:
        note = genanki.Note(
            model=model,
            fields=[
                card["单词"],
                card["音标"],
                card["基本释义"],
                card["图片"],
                card["例句1"],
                card["例句翻译1"],
                card["例句2"],
                card["例句翻译2"],
                card["例句3"],
                card["例句翻译3"],
            ]
        )
        deck.add_note(note)

    return deck


def export_anki_package(deck: genanki.Deck) -> BytesIO:
    """
    导出 Anki 卡组为 BytesIO

    Args:
        deck: genanki.Deck 对象

    Returns:
        包含 .apkg 数据的 BytesIO 对象
    """
    package = genanki.Package(deck)
    apkg_data = BytesIO()
    package.write_to_file(apkg_data)
    apkg_data.seek(0)
    return apkg_data


@router.get('/', response_class=HTMLResponse)
async def index(request: Request, amount: int = 3):
    context = {"message_of_pop_up": "", "cap_api_endpoint": f"{config.cap_instance_url}/{config.site_key}/"}
    return templates.TemplateResponse(request=request, name="word2anki_index.html", context=context)

async def do_convert(lang: str, words: list[str], cap_token: str | None) -> dict | HTMLResponse:
    if config.cap_instance_url:  # TODO 重复
        if not cap_token:
            return HTMLResponse("<h3>你必须先验证才能使用</h3>")
        result = await verify_captcha(config.cap_instance_url, config.site_key, config.key_secret, cap_token)
        if not result:
            return HTMLResponse("<h3>验证出错</h3>")
    if len(words) > 10:
        return HTMLResponse("<script>alert('limitation: less than or equal to 10');</script>")

    # 生成 Anki 卡组
    cards = generate_anki_cards(words)
    deck = create_anki_deck(cards, f"Word Deck - {lang}")
    apkg_buffer = export_anki_package(deck)
    if cards:
        file_id = store_item("words.apkg", apkg_buffer)
        # 检查删除旧的文件
        cleanup_old_files()
    else:
        file_id = 0

    context = {
        "websites": words,
        "lines_without_url": [],
        "valid_title": "成功制作为卡片的单词：",
        "invalid_title": "没有制作为卡片的单词：",
        "file_id": file_id,
    }
    return context
