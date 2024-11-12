import re
from typing import Any, Optional

g_rank: "Optional[dict[Any, str]]" = None


def get_rank(event: Any) -> Optional[str]:
    global g_rank
    if g_rank is None:
        from bibscraper.scrapers.usenix import Usenix

        g_rank = {
            # TODO: Introduce (and fill) a new entry field for conference/journal rank
            Usenix.ATC: "A",  # source: http://portal.core.edu.au/conf-ranks/1838/
            Usenix.OSDI: "A*",  # source: http://portal.core.edu.au/conf-ranks/1842/
            Usenix.SECURITY: "A*",  # source: http://portal.core.edu.au/conf-ranks/1841/
        }
    return g_rank.get(event)


# Used to normalize track names as a list of keywords
IGNORED_WORDS = ["about", "and", "of", "on", "one", "the"]
IGNORED_PATTERNS = re.compile(
    r"|".join(
        [r"(^" + w + r"(?=\s))" for w in IGNORED_WORDS]
        + [r"(\s" + w + r"(?=\s))" for w in IGNORED_WORDS]
        + [r"(\s" + w + r"$)" for w in IGNORED_WORDS]
    )
)

NORMALIZED_KEYWORDS: "dict[str, list[str]]" = {
    "acceleration": ["Acceleration"],
    "aiml": ["Machine Learning"],
    "aimldatascience": ["Machine Learning", "Data science"],
    "bigdata": ["Big Data"],
    "buggy": ["Bugs"],
    "cloudy": ["Cloud"],
    "datacenter": ["Data Center"],
    "dataforensicsincidentresponsedfir": [
        "Forensics",
        "Incident Response",
        "DFIR",
    ],
    "dataforensicsincidentresponse": [
        "Forensics",
        "Incident Response",
        "DFIR",
    ],
    "edge": ["Edge"],
    "embeddediotsecurity": ["IoT", "Embedded"],
    "emergingsecurityissues": ["Emerging Topics"],
    "enterprise": ["CorpSec"],
    "enterprisesecurity": ["CorpSec"],
    "filesystems": ["Filesystems"],
    "guestpresentation": ["Keynote"],
    "hardwareembedded": ["Hardware", "Embedded"],
    "internetthings": ["IoT"],
    "invitedtalk": ["Keynote"],
    "invitedtalks": ["Keynote"],
    "iotsecurity": ["IoT", "Security"],
    "keynoteaddress": ["Keynote"],
    "keyvaluestore": ["Key-Value Stores"],
    "keyvaluestores": ["Key-Value Stores"],
    "keyvaluestorage": ["Key-Value Stores"],
    "machinelearning": ["Machine Learning"],
    "malware": ["Malware"],
    "malwareoffense": ["Malware"],
    "malwaredefense": ["Malware"],
    "memorable": ["Memory"],
    "ml": ["Machine Learning"],
    "mlishard": ["Machine Learning"],
    "mobilesecurity": ["Mobile", "Security"],
    "network": ["Network"],
    "networkdefense": ["Network Security"],
    "networksecurity": ["Network Security"],
    "nonvolatile": ["Non-Volatile", "Memory"],
    "osvirtualization": ["OS / Virtualization"],
    "platformsecurity": ["Platform Security"],
    "platformsecurityvmoshostcontainer": ["Platform Security"],
    "storage": ["Storage"],
    "wan": ["WAN"],
}
