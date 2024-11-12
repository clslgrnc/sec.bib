from dataclasses import fields

import requests

from bibscraper.schemas import Scrap


def are_curly_brackets_matched(s: str) -> bool:
    if not s:
        return True

    depth: int = 0
    escaped: bool = False
    for c in s:
        if escaped:
            escaped = False
        elif c == "\\":
            escaped = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def bibtex_str(scrap: Scrap, download: bool = False):
    if scrap.content is None:
        return ""
    txt = ""
    for resource in scrap.content:
        txt += f"@{resource.type.value}{{{resource.id},\n"
        resource.fields.normalize()
        for field in fields(resource.fields):
            key = field.name
            value = getattr(resource.fields, key)
            if not value:
                continue

            value = str(value)
            if not are_curly_brackets_matched(value):
                value = value.replace("{", "").replace("}", "")

            txt += f"  {key}{(' '*12)[:-len(key)]} = {{{value.strip()}}},\n"
        txt += "}\n\n"

        if download:
            for file in resource.fields.file:
                if file.local.exists():
                    continue
                file.local.parent.mkdir(parents=True, exist_ok=True)
                print(f"Saving {file.remote} to {file.local}", flush=True)
                response = requests.get(file.remote)
                file.local.write_bytes(response.content)

    return txt
