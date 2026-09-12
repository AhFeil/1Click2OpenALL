import re
from collections.abc import Iterator

# 域名：标签只允许 ASCII 字母数字和连字符，顶级域至少两个字母
# 因此中文域名、没有点号的地址都不会被匹配
DOMAIN = (
    r"[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9\-]*[A-Za-z0-9])?)*"
    r"\.[A-Za-z]{2,}"
)
DOMAIN_PATTERN = re.compile(DOMAIN)
EMAIL_PATTERN = re.compile(rf"[A-Za-z0-9._%+\-]+@{DOMAIN}")

# 以 - 开头的一行表示一项已有数据，后面整体作为一个邮箱或域名
LIST_ITEM_PATTERN = re.compile(r"\s*-\s+(?P<value>.*)")


def _classify(token: str) -> tuple[str, str] | None:
    """把单个字符串识别为邮箱或域名，识别不了返回 None"""
    if EMAIL_PATTERN.fullmatch(token):
        return "email", token
    if DOMAIN_PATTERN.fullmatch(token):
        return "domain", token.lower()
    return None


def _iter_tokens(content: str) -> Iterator[tuple[str, str]]:
    """扫描主文本框，产出 (kind, value)，kind 为 email 或 domain。

    普通行只从中提取邮箱；以 - 开头的行取后面的整体，按邮箱或域名解释，
    这样可以把上次的结果和新数据放一起，直接得到去重后的结果。
    """
    for one_line in content.splitlines():
        item = LIST_ITEM_PATTERN.match(one_line)
        if item:
            classified = _classify(item.group("value").strip())
            if classified:
                yield classified
            continue
        for email in EMAIL_PATTERN.findall(one_line):
            yield "email", email


def _iter_exclusions(content: str) -> Iterator[tuple[str, str]]:
    """扫描排除框，每行一项，可以是域名或邮箱（允许带 - 前缀）"""
    for one_line in content.splitlines():
        token = one_line.strip()
        item = LIST_ITEM_PATTERN.match(token)
        if item:
            token = item.group("value").strip()
        classified = _classify(token)
        if classified:
            yield classified


def extract_emails(content: str, exclude: str = "") -> list[str]:
    """提取邮箱，去重、排除后排序。

    大小写不同视为同一个邮箱，保留首次出现的写法。
    """
    exclusions = list(_iter_exclusions(exclude))
    excluded_emails = {value.lower() for kind, value in exclusions if kind == "email"}
    excluded_domains = {value for kind, value in exclusions if kind == "domain"}
    emails = {}
    for kind, value in _iter_tokens(content):
        if kind == "email":
            emails.setdefault(value.lower(), value)
    kept = (
        email for email in emails.values()
        if email.lower() not in excluded_emails
        and email.rpartition('@')[2].lower() not in excluded_domains
    )
    return sorted(kept, key=str.lower)


def extract_email_domains(content: str, exclude: str = "") -> list[str]:
    """提取邮箱域名，去重、排除后排序"""
    # 排除框里的邮箱按其域名整体排除
    excluded_domains = {
        value.rpartition('@')[2].lower() if kind == "email" else value
        for kind, value in _iter_exclusions(exclude)
    }
    domains = {
        value.rpartition('@')[2].lower() if kind == "email" else value
        for kind, value in _iter_tokens(content)
    }
    return sorted(domains - excluded_domains, key=str.lower)
