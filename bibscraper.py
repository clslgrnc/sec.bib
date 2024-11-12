#!/usr/bin/env python3

import pickle
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, Hashable, Iterable, List

from bibscraper.exporter import bibtex_str
from bibscraper.schemas import Scrap
from bibscraper.scrapers import gen_scrapers

SCRAP_FILE = Path(__file__).parent / "scraped" / "scraps.pickle"


def dump_scraps(scraps: Iterable[Scrap], file: Path) -> None:
    with file.open("wb") as f:
        pickle.dump({scrap.venue.id: scrap for scrap in scraps if scrap.venue.id}, f)


def load_scraps(file: Path) -> Dict[Hashable, Scrap]:
    if not file.exists():
        return {}
    with file.open("rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    download: bool = len(sys.argv) > 1 and sys.argv[1] == "-d"

    Path("scraped").mkdir(parents=True, exist_ok=True)

    old_scraps = load_scraps(SCRAP_FILE)
    new_scraps: List[Scrap] = []

    current_year = datetime.now().year
    for scraper in gen_scrapers(range(current_year - 1, current_year + 2)):
        scrap = scraper.scrap(old_scraps.get(scraper.venue.id))
        new_scraps.append(scrap)

    with ThreadPoolExecutor() as executor:
        all_bibs = executor.map(
            lambda scrap: bibtex_str(scrap, download=download), new_scraps
        )

    bibs = "".join(all_bibs)
    if bibs:
        bibs += R"""

@Comment{jabref-meta: databaseType:biblatex;}

@Comment{jabref-meta: grouping:
0 AllEntriesGroup:;
1 AutomaticKeywordGroup:Keywords\;2\;keywords\;\\\;\;>\;0\;0x8a8a8aff\;\;\;;
1 AutomaticKeywordGroup:Awards\;2\;awards\;\\\;\;>\;0\;0x8a8a8aff\;\;\;;
1 AutomaticKeywordGroup:Date\;2\;yearmonth\;\\\;\;>\;0\;0x8a8a8aff\;\;\;;
}

@Comment{jabref-meta: saveOrderConfig:specified;date;true;citationkey;false;title;false;}
"""

        Path("scraped/bibscraped.bib").write_text(bibs)

    dump_scraps(new_scraps, SCRAP_FILE)
