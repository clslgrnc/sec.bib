import logging
import re
from datetime import datetime, timezone
from hashlib import md5
from typing import Any, Iterable, List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from bibscraper.meta import IGNORED_PATTERNS, NORMALIZED_KEYWORDS
from bibscraper.schemas import Resource, Scrap, Venue


class Scraper:
    logger: logging.Logger
    venue: Venue

    def __init__(self, year: int, **kwargs: Any) -> None:
        klass = self.__class__
        self.logger = logging.getLogger(f"{klass.__module__}.{klass.__qualname__}")

    @classmethod
    def gen_scrapers(cls, year_range: Iterable[int]):
        return (cls(year=year) for year in year_range)

    def get_text(self, html: Optional[str]) -> Optional[str]:
        if html is None:
            return None
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def get_data(self) -> List[Resource]:
        return self.parse_data(self.get_raw_data())

    def get_raw_data(self) -> bytes:
        response = requests.get(self.venue.url)
        response.raise_for_status()
        return response.content

    def strip(self, string: str) -> str:
        return re.sub(r"\s+", " ", string.strip())

    def normalize_keyword(
        self,
        keyword: str,
        split: bool = False,
        remove_number: bool = True,
    ) -> "list[str]":
        keyword = self.strip(keyword)
        if remove_number:
            keyword = self.strip(re.sub(r"\s#?[1-9]$", "", keyword))
        if not keyword:
            return []

        kw = re.sub(IGNORED_PATTERNS, "", keyword.lower())
        kw = re.sub(r"[^a-z]+", "", kw)
        normalized_keywords = NORMALIZED_KEYWORDS.get(kw)
        if normalized_keywords:
            return normalized_keywords
        if not split:
            return [keyword.replace(";", "")]

        # Try to guess keywords
        separated_keywords = re.sub(
            r"(?:(?<=[^,])\sand\s)"
            r"|(?::\s)"
            r"|(?:;\s)"
            r"|(?:(?<=[a-z0-9])\s*/\s*(?=[A-Z]))",
            "###",
            self.strip(keyword),
        ).split("###")
        normalized_keywords = [kw.strip() for kw in separated_keywords]
        # Remove track number
        if remove_number:
            normalized_keywords = [
                re.sub(r"\s#?[1-9]$", "", kw) for kw in normalized_keywords
            ]
        normalized_keywords = [kw.strip() for kw in normalized_keywords]
        return [kw for kw in normalized_keywords if kw]

    def clean_up_html(self, content: bytes) -> bytes:
        # remove some useless parts
        soup = BeautifulSoup(content, "html.parser")
        return self.clean_up_soup(soup).encode()

    def clean_up_soup(self, soup: Tag) -> Tag:
        # remove some useless parts
        for script in soup.find_all("script"):
            script.decompose()
        for style in soup.find_all("style"):
            style.decompose()
        return soup

    def hash_data(self, data: bytes) -> bytes:
        return md5(data).digest()

    def parse_data(self, data: bytes) -> List[Resource]:
        # update self.venue and return list of ressources
        raise NotImplementedError

    def scrap(self, old_scrap: Optional[Scrap]) -> Scrap:
        print(
            f"\U0001f50d Scraping {self.venue.name} {self.venue.number or '-'} {self.venue.year or ''}",
            flush=True,
        )

        if old_scrap is None:
            old_scrap = Scrap(self.venue, datetime.fromtimestamp(0), -1)

        new_scrap = Scrap(
            venue=self.venue,
            date=datetime.now(timezone.utc),
            status_code=0,
        )

        # Get RAW data
        raw_data = b""
        try:
            raw_data = self.get_raw_data()
        except requests.exceptions.HTTPError as e:
            self.logger.warning(f"{self.venue.url} returned {e.response.status_code}")
            new_scrap.status_code = e.response.status_code
        except Exception as e:
            self.logger.error(f"{self.venue.url} raised unexpected exception {repr(e)}")
            new_scrap.status_code = -1
        else:
            new_scrap.status_code = 200

        if new_scrap.status_code != 200:
            if old_scrap.status_code == 200:
                return old_scrap
            return new_scrap

        if old_scrap.status_code not in {-1, 200}:
            print(
                f"\t\U0001f4a1 {self.venue.number or '-'} {self.venue.year or ''} is now live (previously {old_scrap.status_code})",
                flush=True,
            )

        # Check Hash
        new_scrap.witness = self.hash_data(raw_data)
        if new_scrap.witness == old_scrap.witness:
            print("\t\U0001f4a2 No new data", flush=True)
            return old_scrap

        # Parse data
        try:
            new_scrap.content = self.parse_data(raw_data)
        except Exception as e:
            self.logger.error(f"Unable to parse content {repr(e)}")
            new_scrap.status_code = -1
        else:
            print(f"\t\U0001f4d1 Parsed {len(new_scrap.content)} resources", flush=True)

        if new_scrap.status_code != 200 and old_scrap.status_code == 200:
            return old_scrap
        return new_scrap
