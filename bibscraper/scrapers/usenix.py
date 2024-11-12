import hashlib
import re
import struct
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Generator, Iterable, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from dateutil.parser import parse as parse_date

from bibscraper.schemas import Resource, Venue
from bibscraper.schemas.fieldtypes import (
    DateField,
    File,
    Name,
    NameList,
    SeparatedLiterals,
)
from bibscraper.scraper import Scraper

# full bibtex available at https://www.usenix.org/biblio/export/bibtex
# not sur if it should be used as it probably contains conferences we are not
# interested in, and abstract, files, and dates would have to be retrieved
# separately.

# Retrieved
PROGRAM = b"P"
ACCEPTED = b"A"


class Usenix(Enum):
    ATC = "atc"  # Annual Technical Conference
    # CSET = "cset"  # Cyber Security Experimentation and Test
    ENIGMA = "enigma20"
    # FAST = "fast"  # File and Storage Technologies
    # FOCI = "foci"  # Free and Open Communications on the Internet
    # HOTCLOUD = "hotcloud"  # Hot Topics in Cloud Computing
    # HOTEDGE = "hotedge"  # Hot Topics in Edge Computing
    # HOTSTORAGE = "hotstorage"  # Hot Topics in Storage and File Systems
    # LASER = "laser20"  # Learning from Authoritative Security Experiment Results
    # LISA = "lisa"  # Large Installation System Administration
    # NSDI = "nsdi"  # Networked Systems Design and Implementation
    # OPML = "opml"  # Operational Machine Learning
    OSDI = "osdi"  # Operating Systems Design and Implementation
    # PEPR = "pepr"  # Privacy Engineering Practice and Respect
    # RAID = "raid"  # Research in Attacks, Intrusions and Defenses, needs it own class: @raid20XX.org since 2020
    # SCAINET = "scainet"  # Security and AI Networking
    SECURITY = "usenixsecurity"
    # SOUPS = "soups20"  # Symposium on Usable Privacy and Security
    # SRECON = "srecon"  # Site Reliability Engineering, needs it own class for event by continent
    # TAPP = "tapp"  # Theory and Practice of Provenance
    # VAULT = "vault"  # Linux Storage and Filesystems
    WOOT = "woot"  # Workshop on Offensive Technologies
    # ...


PROGRAM_URI = {
    Usenix.ENIGMA: "program",
    Usenix.WOOT: "workshop-program",
}


@dataclass
class UsenixArticleRef:
    url: str
    date: Optional[DateField] = None
    eventdate: Optional[DateField] = None
    keywords: SeparatedLiterals = field(default_factory=SeparatedLiterals)


class UsenixScraper(Scraper):
    def __init__(self, event: Usenix, year: int) -> None:
        super().__init__(year)
        self.year = year
        self.event = event
        self.url_root = (
            f"https://www.usenix.org/conference/{event.value}{str(year)[-2:]}/"
        )
        self.venue = Venue(
            id=f"Usenix {event.name} {year}",
            name=f"Usenix {event.name}",
            year=year,
            url=urljoin(self.url_root, PROGRAM_URI.get(event, "technical-sessions")),
        )
        self.booktitle = None
        self.session = requests.Session()

    @classmethod
    def gen_scrapers(cls, year_range: Iterable[int]) -> Generator[Scraper, None, None]:
        return (
            cls(event, year)
            # for event in [Usenix.SECURITY]
            for event in Usenix
            for year in year_range
        )

    def get_event_date(self, homepage: bytes) -> None:
        soup = BeautifulSoup(homepage, "html.parser")
        date_tag = soup.find("div", class_="field-name-field-date-text")
        if not date_tag:
            return
        event_dates = date_tag.text
        if not event_dates:
            return
        start_date = re.sub(r"([0-9]{1,2})[^0-9]([0-9]{1,2})", r"\1", event_dates)
        end_date = re.sub(r"([0-9]{1,2})[^0-9]([0-9]{1,2})", r"\2", event_dates)
        self.venue.start_date = parse_date(start_date).date()
        self.venue.end_date = parse_date(end_date).date()

    def get_raw_data(self) -> bytes:
        # Result is PROGRAM + response.content
        # or concatenation of accepted paper waves encoded as
        # ACCEPTED:len(spring):len(summer):...:springsummerfallwinter
        response = self.session.get(self.venue.url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                err404 = e
            else:
                raise
        else:
            return PROGRAM + self.clean_up_html(response.content)

        # "technical-sessions" leads to 404, try accepted papers
        # first check if conf exists (and retrieve event date)
        response = self.session.get(self.url_root)
        response.raise_for_status()
        self.get_event_date(response.content)

        pages: list[bytes] = []
        for season in ["spring", "summer", "fall", "winter"]:
            response = self.session.get(
                urljoin(self.url_root, f"{season}-accepted-papers")
            )
            if response.status_code == 200:
                pages.append(self.clean_up_html(response.content))
            else:
                pages.append(b"")

        if not pages:
            raise err404

        # some accepted papers are available

        return (
            ACCEPTED
            + struct.pack("<IIII", *(len(page) for page in pages))
            + b"".join(pages)
        )

    def parse_authors(self, soup: Tag) -> NameList:
        authors_tag = soup.find(class_="field-name-field-paper-people-text")
        if not isinstance(authors_tag, Tag):
            authors_tag = soup.find(class_="field-name-field-presented-by")
        if not isinstance(authors_tag, Tag):
            return NameList()

        for em in authors_tag.find_all("em"):
            em.decompose()

        authors = authors_tag.text
        if authors.startswith("Author:"):
            authors = authors[len("Author:") :]
        elif authors.startswith("Authors:"):
            authors = authors[len("Authors:") :]
        authors = authors.strip()
        authors = authors.strip(",")
        authors = authors.replace(", and ", "###")
        authors = authors.replace(" and ", "###")
        authors = authors.replace(",", "###")
        authors_list: "list[str]" = []
        for name in authors.split("###"):
            name = name.strip()
            if ":" in name[:-3] and name[:5].lower() in ["panel", "moder"]:
                name = name[name.find(":") + 1 :]
                name = name.strip()
            if name:
                authors_list.append(name)
        return NameList(Name(full_name=name, id=name) for name in authors_list)

    def parse_open_access(self, output: Resource, open_access: Tag):
        for div in open_access.find_all(class_="field-type-file"):
            for anchor in div.find_all("a"):
                url = urljoin(self.url_root, anchor["href"])
                filename = url.rsplit("/", 1)[-1]
                output.fields.urls.append(url)
                output.fields.file.append(
                    File(
                        remote=url,
                        local=Path("files")
                        / str(self.venue.name).replace(" ", "")
                        / str(self.venue.year)
                        / filename,
                    )
                )
        for media in open_access.find_all(class_="usenix-schedule-media"):
            url = media["src"]
            if url:
                output.fields.urls.append(urljoin(self.url_root, url))

    def find_parse_bib(self, soup: Tag, article: UsenixArticleRef):
        # Retrieve embedded bibtex
        bibtex_tag = soup.find(class_=re.compile(r"bibtex(-accordion)?-text-entry"))
        if not bibtex_tag:
            self.logger.warning(
                f"failed to retrieve bibtex from ({article.url}), entry may miss some info."
            )
            return None
        parsed_bib = list(Resource.parse(bibtex_tag.get_text()))
        if len(parsed_bib) != 1:
            self.logger.warning(
                f"failed to parse bibtex from ({article.url}), entry may miss some info."
            )
            return None
        self.booktitle = parsed_bib[0].fields.booktitle
        return parsed_bib[0]

    def parse_article(self, article: UsenixArticleRef) -> Optional[Resource]:
        response = self.session.get(article.url)
        if response.status_code != 200:
            self.logger.warning(
                f"self.session.get({article.url}) failed with "
                f"{response.status_code}, skipping."
            )
            return

        soup = BeautifulSoup(response.content, "html.parser").find(
            "section", id="content"
        )
        if not isinstance(soup, Tag):
            self.logger.warning(
                f"failed to retrieve content from ({article.url}), skipping."
            )
            return

        # Retrieve embedded bibtex
        output = self.find_parse_bib(soup, article)
        if output is None:
            output = Resource.from_dict(
                {
                    "ID": hashlib.md5(article.url.encode("UTF8")).hexdigest(),
                    "ENTRYTYPE": "inproceedings",
                }
            )

        # update id
        output.id = f"{self.venue.id}:{output.id}".replace(" ", ":")

        # retrieve title
        if not output.fields.title:
            title = soup.find(id="page-title") or soup.title
            if title:
                output.fields.title = title.text

        # retrieve year
        if not output.fields.year:
            output.fields.year = str(self.year)

        # retrieve abstract
        if not output.fields.abstract:
            abstract = soup.find(class_="field-name-field-paper-description")
            if abstract:
                abstract_txt = abstract.text
                if abstract_txt.startswith("Abstract:"):
                    abstract_txt = abstract_txt[len("Abstract:") :]
                output.fields.abstract = abstract_txt.strip()

        # retrieve authors
        if not output.fields.author:
            output.fields.author = self.parse_authors(soup)

        # retrieve awards
        for award in soup.find_all(class_="field-name-taxonomy-vocabulary-8"):
            award_txt = award.text.strip()
            if award_txt.startswith("Award:"):
                award_txt = award_txt[len("Award:") :]

            output.fields.awards.append(award_txt.strip())

        # TODO: Retrieve artifact evaluation status?

        # retrieve media
        open_access = soup.find(id="node-paper-full-group-open-access-content")
        if isinstance(open_access, Tag):
            self.parse_open_access(output, open_access)

        if article.date:
            output.fields.date = article.date
        if article.eventdate:
            output.fields.eventdate = article.eventdate
        if article.keywords:
            output.fields.keywords.extend(article.keywords)
        if not output.fields.url:
            output.fields.url = article.url
        if not output.fields.booktitle:
            output.fields.booktitle = str(self.booktitle or self.venue.id)

        output.fields.urldate = date.today()
        return output

    def get_date(self, soup: Tag) -> Optional[date]:
        page_date = None
        date_tag = soup.find("meta", property="article:modified_time")
        assert isinstance(date_tag, Tag)
        if not date_tag:
            date_tag = soup.find("meta", property="article:published_time")
        assert isinstance(date_tag, Tag)
        if not date_tag:
            date_tag = soup.find("meta", property="og:updated_time")
        assert isinstance(date_tag, Tag)
        if date_tag and date_tag.get("content"):
            page_date = parse_date(str(date_tag["content"])).date()

        return page_date

    def get_talks(self, soup: Tag) -> "set[str]":
        urls: set[str] = set()
        for anchor in soup.find_all("a"):
            href = anchor["href"]
            if not href or "presentation" not in href:
                continue
            url = urljoin(self.url_root, href)
            if len(url) <= len(urljoin(self.url_root, "presentation/")):
                # destination missing (bug in WOOT)
                continue
            if url.startswith(urljoin(self.url_root, "presentation")):
                urls.add(url)
        return urls

    def parse_accepted(self, content: bytes) -> "list[UsenixArticleRef]":
        if not content:
            return []

        soup = BeautifulSoup(content, "html.parser")

        page_date = self.get_date(soup)
        urls = self.get_talks(soup)

        return [
            UsenixArticleRef(
                url,
                date=page_date,
                eventdate=self.venue.end_date or self.venue.start_date,
            )
            for url in urls
        ]

    def parse_session(
        self, soup: Tag, date: Optional[date], eventdate: Optional[date]
    ) -> "list[UsenixArticleRef]":
        keywords = SeparatedLiterals()
        if soup.h2:
            session_title = soup.h2.text
            if self.event == Usenix.ATC and ":" in session_title[:-2]:
                # ATC (esp 2021) may have Session Titles like
                # "I'm Old But I Learned a New Trick: Machine Learning"
                session_title = session_title[session_title.find(":") + 1 :]
            for kw in session_title.split(";"):
                keywords.extend(self.normalize_keyword(self.strip(kw)))

        urls = self.get_talks(soup)

        return [
            UsenixArticleRef(
                url,
                date=date,
                eventdate=eventdate,
                keywords=keywords,
            )
            for url in urls
        ]

    def parse_program(self, content: bytes) -> "list[UsenixArticleRef]":
        if not content:
            return []

        output: "list[UsenixArticleRef]" = []
        soup = BeautifulSoup(content, "html.parser")
        page_date = self.get_date(soup)

        day = None
        for slot in soup.find_all(class_="paragraphs-item-conference-schedule-slot"):
            day_tag = slot.find(class_="field-name-field-date-text")
            if day_tag is not None:
                day = parse_date(f"{day_tag.text} {self.venue.year}").date()
            for session in slot.find_all(class_="node-session"):
                talks = self.parse_session(session, date=page_date, eventdate=day)
                if not talks:
                    continue

                output.extend(talks)

        return output

    def parse_data(self, data: bytes) -> "list[Resource]":
        # May raise an exception if data does not have the right format
        if data[0:1] == PROGRAM:
            articles = self.parse_program(data[1:])
        elif data[0:1] == ACCEPTED:
            (len_spring, len_summer, len_fall, _) = struct.unpack_from(
                "<IIII", buffer=data, offset=1
            )
            offset_spring = 1 + struct.calcsize("<IIII")
            offset_summer = offset_spring + len_spring
            offset_fall = offset_summer + len_summer
            offset_winter = offset_fall + len_fall
            articles = self.parse_accepted(data[offset_spring:offset_summer])
            articles.extend(self.parse_accepted(data[offset_summer:offset_fall]))
            articles.extend(self.parse_accepted(data[offset_fall:offset_winter]))
            articles.extend(self.parse_accepted(data[offset_winter:]))
        else:
            raise ValueError

        output = [self.parse_article(article) for article in articles]
        return [x for x in output if x]
