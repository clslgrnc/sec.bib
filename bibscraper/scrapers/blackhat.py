import json
import re
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Generator, Iterable, List, Optional

from bibscraper.schemas import EntryFields, Resource, Venue
from bibscraper.schemas.entry import EntryType
from bibscraper.schemas.fieldtypes import File, Name, NameList
from bibscraper.scraper import Scraper


class BlackHat(Enum):
    USA = "us"
    EU = "eu"
    ASIA = "asia"


def anchor(title: str) -> str:
    return re.sub(r"[^-a-z ]+", "", title.lower()).replace(" ", "-")


def date_fromisoformat(date_str: str) -> Optional[date]:
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


class BlackHatScraper(Scraper):
    def __init__(self, event: BlackHat, year: int) -> None:
        super().__init__(year)
        self.venue = Venue(
            id=f"Black Hat {event.name} {year}",
            name=f"Black Hat {event.name}",
            year=year,
            url=self.get_url(event, year),
        )

    @classmethod
    def gen_scrapers(cls, year_range: Iterable[int]) -> Generator[Scraper, None, None]:
        return (
            cls(event, year)
            for event in [BlackHat.USA, BlackHat.EU, BlackHat.ASIA]
            for year in year_range
        )

    def get_url(self, event: BlackHat, year: int) -> str:
        return (
            f"https://www.blackhat.com/{event.value}-{str(year)[-2:]}"
            "/briefings/schedule/sessions.json"
        )

    def is_break(self, resource: dict[str, str]) -> bool:
        # returns true iff resource is a break (i.e. not a talk)
        if resource.get("format_id") == "454":
            return True
        title = resource.get("title", "").lower()
        alpha_title = "".join(filter(str.isalpha, title))
        return alpha_title in {
            "afternoonbreak",
            "afternoonrefreshmentbreakbriefings",
            "amcoffeeservice",
            "breakfast",
            "briefingsafternoonrefreshmentbreak",
            "briefingsbreakfast",
            "briefingslunch",
            "briefingsmorningrefreshmentbreak",
            "lunchbreak",
            "lunchbriefings",
            "morningbeveragebreakbriefings",
            "morningbreak",
            "morningrefreshmentbreakbriefings",
            "pmcoffeeservice",
            "thursdaybriefingsbreakfast",
            "thursdaybriefingslunch",
            "wednesdaybriefingsbreakfast",
            "wednesdaybriefingslunch",
        }

    def parse_data(self, data: bytes) -> List[Resource]:
        content = json.loads(data)
        output: List[Resource] = []
        for _, resource in content.get("sessions", {}).items():
            if (
                "source_session_id" in resource
                and resource.get("id") != resource["source_session_id"]
            ):
                # duplicate entry
                continue
            if self.is_break(resource):
                # Meals
                continue

            fields = EntryFields()

            fields.abstract = self.get_text(resource.get("description"))

            fields.author = NameList(
                Name(
                    id=author.get("person_id"),
                    first_name=author.get("first_name"),
                    last_name=author.get("last_name"),
                    company=author.get("company"),
                    bio=author.get("bio"),
                )
                for author in [
                    content.get("speakers", {}).get(spkr["person_id"], {})
                    for spkr in resource.get("speakers", [])
                ]
            )

            if time_start := resource.get("time_start"):
                fields.eventdate = date_fromisoformat(time_start[:10])
            elif self.venue.year is not None:
                fields.eventdate = date(self.venue.year, 1, 1)
            if published_date := resource.get("published_date"):
                fields.date = date_fromisoformat(published_date)
            else:
                fields.date = fields.eventdate
            if fields.date is None:
                fields.year = str(self.venue.year)

            fields.title = self.get_text(resource.get("title"))
            fields.booktitle = f"{self.venue.name} {self.venue.year}"

            # Keywords
            for track_key in [
                "track_1",
                "track_2",
                "discipline_1",
                "discipline_2",
            ]:
                track = resource.get(track_key)
                if track:
                    fields.keywords.extend(self.normalize_keyword(track))

            if fields.title and "id" in resource:
                fields.url = (
                    self.venue.url[: -len("sessions.json")]
                    + f"index.html#{anchor(fields.title)}-{resource['id']}"
                )
                fields.urldate = date.today()

            if isinstance(resource.get("bh_files"), dict):
                for file in resource["bh_files"].values():
                    url = file.get("url")
                    if not url or url.find("http") < 0:
                        continue
                    url = url[url.find("http") :]
                    fields.urls.append(url)
                    label: str = file.get("label", "")
                    label_words = set(label.lower().split(" "))
                    if label_words & {
                        "presentation",
                        "slides",
                        "whitepaper",
                        "paper",
                    } and not label_words & {"unavailable", "tool"}:
                        local_path = (
                            Path("files")
                            / self.venue.name.replace(" ", "")
                            / str(self.venue.year)
                        )
                        local_path /= url.rsplit("/", maxsplit=1)[-1]
                        fields.file.append(File(remote=url, local=local_path))
            output.append(
                Resource(
                    id=f"{self.venue.name.replace(' ', '')}:{self.venue.year}:"
                    f"{resource.get('id')}",
                    fields=fields,
                    type=EntryType.INPROCEEDINGS,
                    # venue=self.venue,
                )
            )
        return output
