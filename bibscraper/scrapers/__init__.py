from typing import Iterable

from bibscraper.scrapers.blackhat import BlackHatScraper
from bibscraper.scrapers.projectzero import ProjectZeroScraper
from bibscraper.scrapers.usenix import UsenixScraper

ALL_SCRAPERS_CLS = [
    BlackHatScraper,
    UsenixScraper,
    ProjectZeroScraper,
]


def gen_scrapers(year_range: Iterable[int]):
    return (
        scraper
        for scraper_cls in ALL_SCRAPERS_CLS
        for scraper in scraper_cls.gen_scrapers(year_range)
    )
