import hashlib
import re
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Generator, Iterable, List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from dateutil.parser import parse as parse_date

from bibscraper.schemas import EntryFields, Resource, Venue
from bibscraper.schemas.entry import EntryType
from bibscraper.schemas.fieldtypes import File, Name, NameList
from bibscraper.scraper import Scraper


class ProjectZeroScraper(Scraper):
    def __init__(self, year) -> None:
        super().__init__(year)
        self.year = year
        self.venue = Venue(
            id=f"Project Zero {year}",
            name=f"Project Zero {year}",
            url=self.get_url(year),
        )
        self.session = requests.Session()

    @classmethod
    def gen_scrapers(cls, year_range: Iterable[int]) -> Generator[Scraper, None, None]:
        return (cls(year) for year in year_range)

    def get_url(self, year: int) -> str:
        """
        actual content is javascript:
        try {
        _WidgetManager._HandleControllerResult('BlogArchive1', 'getTitles',{'path': 'https://googleprojectzero.blogspot.com/2017',
        'posts': [
          {'title': 'aPAColypse now: Exploiting Windows 10 in a Local N...',
           'url': 'https://googleprojectzero.blogspot.com/2017/12/apacolypse-now-exploiting-windows-10-in_18.html'},
          {'title': 'Over The Air - Vol. 2, Pt. 3: Exploiting The Wi-Fi...',
           'url': 'https://googleprojectzero.blogspot.com/2017/10/over-air-vol-2-pt-3-exploiting-wi-fi.html'}, ...
        """

        return (
            f"https://googleprojectzero.blogspot.com/?action=getTitles&widgetId=BlogArchive1&widgetType=BlogArchive&responseType=js"
            + f"&path=https%3A%2F%2Fgoogleprojectzero.blogspot.com%2F{year}"
        )

    def get_title(self, soup: Tag) -> Optional[str]:
        """
        <meta content='Zooming in on Zero-click Exploits' property='og:title'/>
        """
        title = soup.find("meta", property="og:title")
        assert isinstance(title, Tag)
        return title["content"]

    def get_date(self, soup: Tag) -> Optional[date]:
        """
        <h2 class='date-header'><span>Wednesday, December 14, 2016</span></h2>
        """
        date_tag = soup.find(class_="date-header")
        assert isinstance(date_tag, Tag)
        return parse_date(date_tag.get_text(separator=" ", strip=True)).date()

    def get_author_abstract(self, soup: Tag) -> "tuple[Optional[str], Optional[str]]":
        post_body = soup.find(class_="post-body")
        assert isinstance(post_body, Tag)
        post_body = self.clean_up_soup(post_body)
        author = None
        abstract = ""
        for tag in post_body.children:
            if not tag.name:
                continue
            tag_text = tag.get_text(separator="#|#", strip=True)
            if not tag_text:
                continue
            if not author and tag_text.lower().startswith("posted by"):
                author = tag_text[len("posted by ") :]
                author = author.split(" of ")[0]
                author = author.split(",")[0]
                author = author.split(".")[0]
                author = author.split("#|#")[0]
                author = author.strip()
                if "#|#" not in tag_text:
                    continue
                tag_text = tag_text.split("#|#", maxsplit=1)[1]
            if tag.name != "div" and len(abstract) > 300:
                break
            tag_text = tag_text.replace("#|#", " ").strip()
            if tag_text:
                abstract += " " + tag_text
                if len(abstract) > 900:
                    break
        return author, abstract[:1000].strip()

    def parse_data(self, data: bytes) -> List[Resource]:
        # no json here, but javascript !

        output: List[Resource] = []

        for urlval in re.finditer(b"'url': '(.*?)'", data):
            url = urlval.group(1)
            print("found a link %r" % url, flush=True)

            response = self.session.get(url)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    err404 = e
                else:
                    raise

            content = response.content
            soup = BeautifulSoup(content, "html.parser")

            fields = EntryFields()
            fields.title = self.get_title(soup)
            fields.url = url.decode()
            fields.date = self.get_date(soup)
            author, abstact = self.get_author_abstract(soup)
            if author:
                fields.author.append(Name(full_name=author))
            fields.abstract = abstact
            fields.journaltitle = "Google Project Zero Blog"

            _hash = hashlib.md5(url).hexdigest()

            output.append(
                Resource(
                    id=f"projectzero:{self.year}:{_hash}",
                    fields=fields,
                    type=EntryType.ONLINE,
                )
            )

        return output
