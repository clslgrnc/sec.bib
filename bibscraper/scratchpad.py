import json
import logging
import re
from pprint import pprint as print
from typing import Iterable, Optional

import requests


def get_url(year: int = 2021, event: str = "us") -> str:
    return f"https://www.blackhat.com/{event}-{year % 100}/briefings/schedule/sessions.json"


def dumb_parser(content: bytes, keywords: Iterable[bytes]):
    for keyword in keywords:
        occurrences = re.findall(keyword, content)
        print(f"{len(occurrences)} occurrences of {keyword}", flush=True)


def custom_parser(content: bytes, keywords: Iterable[bytes]):
    content = json.loads(content)
    print(content.keys(), flush=True)


def scrap(keywords: Optional[Iterable[bytes]] = None):
    logger = logging.getLogger(__name__)
    url = get_url()
    print(url, flush=True)
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"{url} returned {response.status_code}")

    try:
        custom_parser(response.content, keywords or [])
    except:
        dumb_parser(response.content, keywords or [])
