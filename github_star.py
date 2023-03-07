import httpx
import pandas as pd
from yutils.html import build_doc, xpath_one
from urllib.parse import urljoin
from loguru import logger


url = "https://github.com/yifeikong?tab=stars"


def parse_next_page(html: bytes) -> str:
    doc = build_doc(html)
    next_button = doc.xpath("//a[text()='Next']")
    if not next_button:
        return ""
    return next_button[0].get("href")


def get_is_listed(url: str) -> bool:
    html = wget_page(url + "/lists")
    if not html:
        return False
    doc = build_doc(html, fragment=True)
    listed_el = xpath_one(doc, "//input[@checked]")
    return listed_el is not None


def parse_star_items(html: bytes) -> list[dict]:
    doc = build_doc(html)
    if doc is None:
        logger.info("build page error")
        return []
    star_items = []
    star_els = doc.xpath("//div[contains(@class,'col-12 d-block')]")
    for star_el in star_els:
        url = xpath_one(star_el, ".//h3/a/@href")
        url = urljoin("https://github.com/", url)
        description = xpath_one(star_el, ".//p/text()")
        language = xpath_one(star_el, './/span[itemprop="programmingLanguage"]/text()')
        is_listed = get_is_listed(url)
        star_item = dict(
            url=url,
            description=description,
            language=language,
            is_listed=is_listed,
        )
        logger.info("star item is {}", star_item)
        star_items.append(star_item)
    return star_items


def wget_page(url: str) -> bytes:
    cookies = {
        "tz": "Asia%2FShanghai",
        "_gh_sess": "IU29xgVOcv7tuuHowpWCyctdTF72Vg%2BxOrZmLUYSLQdC2a3LQGgDybNqYk0AE6QZT6XZ7cWAzeU2h1TrNj7YIZH1h3izySEGeJaDrXZP7F4HfqmvMkU6EYEw5EoQ3RdXTj%2Bnsq2lUkkxZnexm%2BZpzmMjDqmSfWjijDJoXu6bGlK9e0kLyi0hMmhXPlT4kG22K7CZrttbSMmrAS9o2pMviVG8r8SmD183ipXmdk3CnzwRz8IatkkjwOG%2F9icC3B1lV5Db6OGNLKAdcFIJUDcij6FovDbpaZQMRMtZYhNr0wb33mnV%2BAPBaT81g80AtLfFhdTt60lZcpOifjlvi2ZoQJJxAIrghkWEo9kb12tJwzThK9EVGJWIXOvAnwZ%2B0xtGA9JzSxiabKeU8Tlvoe1qajJqqsbkwo6I8LOWM2Sq17%2FamkUYLvcK38b1wYKAsEjaIjqMNjEaLOZ8TXj%2FPn2r%2BMwnZMwU%2BBurOEuC4PljExNQpbXrt1mY9NZjS4AzyRlphAYaJ3cLcvPanQnnmDMB%2FnLuNoBcapTE0hrzXlLtvduhAdN9iFT30GePgqc6RP5JSvOzt%2FNlZqsxwd%2BMK%2FmQy6HH8aZlX%2Fz%2BwaxxsjiYpeOdQ94r15g7%2FtN9o2TiiTAuV5QDAbL1ogYoENxbXyn4GqN%2BE%2FGi21puFApE3jwHNpkaeZFO7IZx5aGXbe89X3dSFsTXU2VhtWxySfSiiEY08FFBYr3AuyIEN%2BhKCaS5qFrSUe9CHpKvbiifaxvO567aYoE9a9NvCRQrJ4cXvwllnXNN9M0PpGTwr8NZ7clNW0N5vz%2BTpbv%2Fg9dANWBHNHWV5pqbRjWbsOhTGNwKt%2BLD5JrnBGYL7hmRAOvBgDwitHwkC%2FCOx8%2FiyizN7K9Qqj7GD5%2BtVIlcIccGWappZPp7TNEf9vA5dItP9GFWoFxE3Eg%3D--xIyT9nazCSCtL2Vy--XtOVhEhQn1DiH1xtVn3V5Q%3D%3D",
        "has_recent_activity": "1",
        "__Host-user_session_same_site": "BIgosgpHuwJDwzPPvZa-Sr7408ikgW9xn2hJdl4ViUsV6RpF",
        "user_session": "BIgosgpHuwJDwzPPvZa-Sr7408ikgW9xn2hJdl4ViUsV6RpF",
        "color_mode": "%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D",
        "_octo": "GH1.1.225226397.1640154380",
        "logged_in": "yes",
        "dotcom_user": "yifeikong",
        "_device_id": "9cc862b23a938c8eccb682a0845c4af4",
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "github.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://github.com/",
        "Connection": "keep-alive",
    }
    logger.info("start to wget url {}", url)
    try:
        content = httpx.get(url, headers=headers, cookies=cookies).content
    except Exception:
        logger.error("http error")
        return b""
    logger.info("first 10 bytes of html is {}", content[:10])
    return content


def list_all_pages():
    current_url = url
    items = []
    while True:
        content = wget_page(current_url)
        if not content:
            continue
        next_page_link = parse_next_page(content)
        if not next_page_link:
            logger.info("no next page found, quit")
            break
        current_url = next_page_link
        star_items = parse_star_items(content)
        logger.info("got {} star items", len(star_items))
        items.extend(star_items)
    df = pd.DataFrame(items)
    df.to_csv("stars.csv")


if __name__ == "__main__":
    list_all_pages()
