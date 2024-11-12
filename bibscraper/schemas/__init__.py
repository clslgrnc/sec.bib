from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, Hashable, Iterator, List, Optional

from bibtexparser.bparser import BibTexParser

from bibscraper.schemas.entry import EntryType
from bibscraper.schemas.fields import EntryFields


@dataclass
class Venue:
    id: Hashable
    url: str
    name: str
    number: Optional[int] = None
    year: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@dataclass
class Resource:
    id: Hashable
    type: EntryType
    fields: EntryFields = field(default_factory=EntryFields)

    @classmethod
    def from_dict(cls, bib: Dict[str, Any], default_type: str = "misc") -> "Resource":
        return Resource(
            id=bib.get("ID"),
            type=EntryType.from_str(bib.get("ENTRYTYPE", default_type)),
            fields=EntryFields.from_dict(bib),
        )

    @classmethod
    def parse(cls, bib: str) -> Iterator["Resource"]:
        bib_parser = BibTexParser(common_strings=True)
        bib_entries: List[Dict[str, Any]] = bib_parser.parse(bib).entries
        return (cls.from_dict(bib) for bib in bib_entries)


@dataclass
class Scrap:
    venue: Venue
    date: datetime  # date of the scraping
    status_code: int
    witness: Optional[bytes] = (
        None  # used to check if content should be fully parsed and updated
    )
    content: Optional[List[Resource]] = None
