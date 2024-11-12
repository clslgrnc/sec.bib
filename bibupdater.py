#!/usr/bin/env python

import re
import sys
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from operator import le
from pathlib import Path
from typing import DefaultDict, List, Optional, Tuple

from pybtex.database.input.bibtex import LowLevelParser, SkipEntry
from pybtex.scanner import PybtexSyntaxError


@dataclass
class Field:
    key: str
    value: str
    raw: str


EmptyField = Field("", "", "")


@dataclass
class Entry:
    type: str
    raw: str
    id: Optional[str] = None
    # header: Optional[str] = None
    fields: "Optional[OrderedDict[str, Field]]" = None
    # footer: Optional[str] = None
    updated: bool = False
    updated_abstract: bool = False
    updated_files: bool = False
    updated_title: bool = False
    new: bool = True

    def __str__(self) -> str:
        if not self.updated:
            return self.raw

        assert self.fields is not None

        output = f"@{self.type}{{{self.id},"
        for field in self.fields.values():
            output += field.raw
        if output[-1] != "\n":
            output += "\n"
        output += "}"
        return output

    def remove_trailing_spaces(self):
        clean_raw = re.sub(r"\s+\n", "\n", self.raw)
        self.raw = clean_raw

        if self.fields is None:
            return

        for field in self.fields.values():
            field.raw = re.sub(r"\s+\n", "\n", field.raw)
            clean_value = re.sub(r"\s+(\n|$)", r"\1", field.value)
            if clean_value == field.value:
                continue
            self.updated = True
            field.value = clean_value
            field.raw = re.sub(r"\s+(\"|\})(\s*,?\s*)$", r"\1\2", field.raw)


class MyParser(LowLevelParser):
    def parse_bibliography(self):
        while True:
            pos = self.pos
            if not self.skip_to([self.AT]):
                yield Entry("BLANK", self.text[pos : self.end_pos])
                return
            yield Entry("BLANK", self.text[pos : self.pos - 1])
            self.command_start = self.pos - 1
            try:
                yield self.parse_command()
            except PybtexSyntaxError as error:
                self.handle_error(error)
            except SkipEntry:
                pass

    def parse_command(self):
        self.current_entry_key = None
        self.current_fields = []
        self.current_field_name = None
        self.current_value = []

        name = self.required([self.NAME])
        command = name.value
        body_start = self.required([self.LPAREN, self.LBRACE])
        body_end = self.RBRACE if body_start.pattern == self.LBRACE else self.RPAREN

        command_lower = command.lower()
        if command_lower == "string":
            raise NotImplementedError
            parse_body = self.parse_string_body
            make_result = lambda: (
                command,
                (self.current_field_name, self.current_value),
            )
        elif command_lower == "preamble":
            raise NotImplementedError
            parse_body = self.parse_meta_body
            make_result = lambda: (command, (self.current_value,))
        elif command_lower == "comment":
            parse_body = self.parse_meta_body
            make_result = lambda: Entry(
                command, self.text[self.command_start : self.pos]
            )
        else:
            parse_body = self.parse_entry_body
            make_result = lambda: Entry(
                type=command,
                raw=self.text[self.command_start : self.pos],
                id=self.current_entry_key,
                fields=OrderedDict(self.current_fields),
            )
        try:
            parse_body(body_end)
            self.required([body_end])
        except PybtexSyntaxError as error:
            self.handle_error(error)
        return make_result()

    def parse_meta_body(self, body_end):
        self.current_value = self.flatten_string(self.parse_string(string_end=body_end))
        self.pos -= 1

    def parse_entry_fields(self):
        while True:
            self.current_field_name = None
            self.current_value = []
            pos = self.pos
            self.parse_field()
            comma = self.optional([self.COMMA])
            if self.current_field_name and self.current_value:
                self.current_fields.append(
                    (
                        self.current_field_name.lower(),
                        Field(
                            self.current_field_name,
                            "#".join(self.current_value),
                            self.text[pos : self.pos],
                        ),
                    )
                )
            if not comma:
                return


def parse_bib(
    path: Path, ignore_blanks: bool = False, new: bool = True
) -> "OrderedDict[str, Entry]":
    text = path.read_text(encoding="UTF-8")
    entries = MyParser(text)
    ordered_entries = OrderedDict()
    for i, entry in enumerate(entries):
        entry.new = new
        if entry.type == "BLANK":
            if ignore_blanks:
                continue
            key = f"blank#{i}"
        elif entry.type.lower() in ["comment"]:
            key = f"raw#{entry.raw}"
        else:
            key = f"id#{entry.id}"
        ordered_entries[key] = entry

    return ordered_entries


def update_entry(target: Entry, update: Entry, ignore: Optional[set] = None) -> None:
    target.new = False

    if target.raw == update.raw:
        return

    assert update.fields is not None
    assert target.fields is not None

    old_abstract = target.fields.get("abstract", EmptyField).value
    old_files = target.fields.get("file", EmptyField).value
    old_title = target.fields.get("title", EmptyField).value

    # collect new and updated fields
    new_fields, updated_fields = collect_new_and_updated_fields(
        target.fields, update.fields
    )

    # check if new and updates are legitimate
    if (
        ignore is not None
        and new_fields.keys() <= ignore
        and updated_fields.keys() <= ignore
    ):
        # do not update if changes are all in ignore list
        return

    apply_entry_update(target, new_fields, updated_fields)

    log_entry_update(target, old_abstract, old_files, old_title)


def collect_new_and_updated_fields(
    target_fields: "OrderedDict[str, Field]", update_fields: "OrderedDict[str, Field]"
) -> Tuple["OrderedDict[str, Field]", "OrderedDict[str, Field]"]:
    new_fields = OrderedDict()
    updated_fields = OrderedDict()

    # collect new and updated fields
    for key, field in update_fields.items():
        old_field = target_fields.get(key)

        if old_field is None:
            new_fields[key] = field
            continue

        if old_field.value == field.value:
            # no need to update
            continue

        # updated field
        updated_fields[key] = field

    return new_fields, updated_fields


def apply_entry_update(
    target: Entry,
    new_fields: "OrderedDict[str, Field]",
    updated_fields: "OrderedDict[str, Field]",
) -> None:

    assert target.fields is not None

    # update everything including ignore list
    target.updated = True
    for key, field in updated_fields.items():
        target.fields[key].raw = field.raw
        target.fields[key].value = field.value

    # Ensure last field ends with `,`
    if target:
        last_key, last_field = target.fields.popitem()
        match = re.search(r"([^,])([\s\n\r]*)$", last_field.raw)
        if match:
            last_field.raw = last_field.raw[: -len(match[0])]
            last_field.raw += match[1]
            last_field.raw += ","
        target.fields[last_key] = last_field

    for key, field in new_fields.items():
        target.fields[key] = field


def log_entry_update(
    target: Entry, old_abstract: str, old_files: str, old_title: str
) -> None:

    assert target.fields is not None

    new_abstract = target.fields.get("abstract")
    new_files = target.fields.get("file")
    new_title = target.fields.get("title")

    if (
        new_abstract is not None
        and SequenceMatcher(
            lambda x: x in " \t\n,.:;!?", new_abstract.value, old_abstract
        ).ratio()
        < 0.5
    ):
        target.updated_abstract = True

    if new_files is not None and set(new_files.value.split(";")) != set(
        old_files.split(";")
    ):
        target.updated_files = True

    if (
        new_title is not None
        and SequenceMatcher(
            lambda x: x in " \t\n,.:;!?", new_title.value, old_title
        ).ratio()
        < 0.8
    ):
        target.updated_title = True


def update_bib(
    main: "OrderedDict[str, Entry]", update: "OrderedDict[str, Entry]"
) -> List[Entry]:

    result: List[Entry] = []

    # filter out unhandled updates
    update_keys = list(update.keys())
    for key in update_keys:
        if key.startswith("id#"):
            update[key].remove_trailing_spaces()
            continue
        del update[key]

    # Update common entries
    common_keys = main.keys() & update.keys()
    for key in common_keys:
        update_entry(main[key], update[key], {"date", "urldate", "year", "yearmonth"})

    # sort new entries and identify longest increasing subseq of main
    new_keys = list(update.keys() - main.keys())
    new_keys.sort(key=lambda x: x.lower())  # JabRef sorts in a case insensitive way
    old_keys = [key for key in main if key.startswith("id#")]
    main_lis = longest_increasing_subsequence(
        old_keys,
        [key.lower() for key in old_keys],
    )

    new_keys_index = 0
    main_lis_index = 0
    for key, value in main.items():
        if not key.startswith("id#"):
            result.append(value)
            continue

        # key.startswith("id#")

        if main_lis_index == len(main_lis):
            # all remaining keys are out of order
            result.append(value)
            continue

        if key != main_lis[main_lis_index]:
            # out of order key
            result.append(value)
            continue

        # key == main_lis[main_lis_index]
        # - insert all new keys smaller than key
        while (
            new_keys_index < len(new_keys)
            and (nkey := new_keys[new_keys_index]).lower() < key.lower()
        ):
            result.append(update[nkey])
            # add blank after entries
            # previous entry was probably blank
            result.append(Entry("NEW_BLANK", "\n\n"))
            new_keys_index += 1

        # - insert key
        result.append(value)
        main_lis_index += 1

        if main_lis_index == len(main_lis):
            # consume all remaining new keys
            while new_keys_index < len(new_keys):
                # add blank before entries
                # previous entry was id#
                result.append(Entry("NEW_BLANK", "\n\n"))
                result.append(update[new_keys[new_keys_index]])
                new_keys_index += 1

    # consume all remaining new keys
    # executed only when main is empty
    while new_keys_index < len(new_keys):
        result.append(update[new_keys[new_keys_index]])
        # add blank between entries
        result.append(Entry("NEW_BLANK", "\n\n"))
        new_keys_index += 1

    if result and result[-1].type == "NEW_BLANK":
        result[-1].raw = "\n"

    return result


def longest_increasing_subsequence(X, KEYS=None):
    if KEYS is None:
        KEYS = X
    # https://en.wikipedia.org/wiki/Longest_increasing_subsequence#Efficient_algorithms
    # used to ensure that resulting bib is more or less sorted by id
    N = len(KEYS)
    P = [None] * N
    M = [None] * (N + 1)
    M[0] = None  # undefined so can be set to any value

    L = 0
    for i in range(N):
        # Binary search for the smallest positive l ≤ L
        # such that KEYS[M[l]] > KEYS[i]
        lo = 1
        hi = L + 1
        while lo < hi:
            mid = lo + (hi - lo) // 2  # lo <= mid < hi
            if KEYS[M[mid]] > KEYS[i]:
                hi = mid
            else:  # if KEYS[M[mid]] <= KEYS[i]
                lo = mid + 1

        # After searching, lo == hi is 1 greater than the
        # length of the longest prefix of KEYS[i]
        newL = lo

        # The predecessor of KEYS[i] is the last index of
        # the subsequence of length newL-1
        P[i] = M[newL - 1]
        M[newL] = i

        if newL > L:
            # If we found a subsequence longer than any we've
            # found yet, update L
            L = newL

    # Reconstruct the longest increasing subsequence
    # It consists of the values of X at the L indices:
    # ...,  P[P[M[L]]], P[M[L]], M[L]
    S = [None] * L
    k = M[L]
    for j in range(L - 1, -1, -1):
        S[j] = X[k]
        k = P[k]

    return S


def log_entry(log: defaultdict, entry: Entry):
    if entry.fields is None:
        return
    if entry.fields.get("booktitle") is not None:
        source = entry.fields["booktitle"].value
    elif entry.fields.get("journaltitle") is not None:
        source = entry.fields["journaltitle"].value
    else:
        source = "Unknown"

    title = entry.fields["title"].value if "title" in entry.fields else "No Title"

    url = entry.fields.get("url")
    if url and url.value:
        title = f"[{title}]({url.value})"

    if entry.new:
        log[source].append(f"- {title}  \n  _New entry_\n")
        return

    if not entry.updated:
        return

    updated_fields = []

    if entry.updated_abstract:
        updated_fields.append("abstract")

    if entry.updated_files:
        updated_fields.append("files")

    if entry.updated_title:
        updated_fields.append("title")

    if not updated_fields:
        return

    if len(updated_fields) > 1:
        updated_fields[-1] = f"and {updated_fields[-1]}"

    if len(updated_fields) == 2:
        log[source].append(f"- {title}  \n  _Updated {' '.join(updated_fields)}_\n")
    else:
        log[source].append(f"- {title}  \n  _Updated {', '.join(updated_fields)}_\n")
    return


def fix_duplicate_id(
    main: "OrderedDict[str, Entry]", update: "OrderedDict[str, Entry]"
) -> "OrderedDict[str, Entry]":
    # as heuristic fix duplicate ids by changing the id of update to the id
    # of an entry in main with the same url (if applicable)
    url_to_id = {}
    duplicate_urls = set()

    for entry in main.values():
        if entry.fields is None or "url" not in entry.fields:
            continue
        url = entry.fields["url"].value
        if url in duplicate_urls:
            continue
        if url in url_to_id:
            # duplicate url, can not do much
            del url_to_id[url]
            duplicate_urls.add(url)
            continue

        url_to_id[url] = entry

    print(f"{duplicate_urls=}", flush=True)

    output = OrderedDict()

    for key, entry in update.items():
        if entry.fields is None or "url" not in entry.fields:
            output[key] = entry
            continue
        url = entry.fields["url"].value
        if url not in url_to_id:
            output[key] = entry
            continue
        original_entry = url_to_id[url]
        if entry.id == original_entry.id:
            output[key] = entry
            continue

        print(f"fixing entry {entry.id} to {original_entry.id}", flush=True)
        entry.id = original_entry.id
        new_key: str = entry.id
        if not new_key.startswith("id#"):
            new_key = f"id#{new_key}"
        output[new_key] = entry

    return output


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage:\n\t{sys.argv[0]} <dst.bib> <main.bib> <update.bib>", flush=True)
        sys.exit(0)

    dst_bib = Path(sys.argv[1])
    main_bib = Path(sys.argv[2])
    up_bib = Path(sys.argv[3])

    main_entries = parse_bib(main_bib, new=False)
    up_entries = parse_bib(up_bib)

    fixed_up_entries = fix_duplicate_id(main_entries, up_entries)

    entries = update_bib(main_entries, fixed_up_entries)
    raw = ""
    log: DefaultDict[str, List[str]] = defaultdict(list)
    for entry in entries:
        log_entry(log, entry)
        raw += str(entry)

    dst_bib.write_text(raw, encoding="UTF-8")

    for src, log_lines in log.items():
        print(f"\n# {src}\n", flush=True)
        print(f"**{len(log_lines)}** new or updated entries\n", flush=True)
        details = len(log_lines) > 8
        if details:
            print("<details>\n", flush=True)
        print(f"{''.join(log_lines)}", flush=True)
        if details:
            print("</details>", flush=True)
        print("", flush=True)
