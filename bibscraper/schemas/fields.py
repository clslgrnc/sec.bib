# Entry fields as defined in biblatex documentation:
# https://raw.githubusercontent.com/plk/biblatex/dev/doc/latex/biblatex/biblatex.tex
# Before defining a custom entry field check if an existing one would be
# relevant.

# Prefer the ones recognized by jabref:
# src/main/java/org/jabref/model/entry/field/StandardField.java
# see also: https://docs.jabref.org/advanced/fields

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional

from dateutil.parser import parse as parse_date

from bibscraper.schemas.fieldtypes import (
    DateField,
    FileList,
    LiteralField,
    Name,
    NameList,
    SeparatedLiterals,
    UriField,
)


@dataclass
class EntryFields:
    @classmethod
    def from_dict(cls, bib: Dict[str, Any]) -> "EntryFields":
        dates: Dict[str, date] = {}
        for datefield in ["date", "eventdate", "urldate"]:
            try:
                dates[datefield] = parse_date(bib[datefield]).date()
            except Exception:
                pass
        author = bib.get("author", NameList())
        if author:
            author = author.replace(R"{\textquoteright}", "'")
        title = bib.get("title")
        if title:
            title = title.replace(R"{\textquoteright}", "'")
        return EntryFields(
            abstract=bib.get("abstract"),
            author=author,
            booktitle=bib.get("booktitle"),
            date=dates.get("date"),
            eventdate=dates.get("eventdate"),
            file=bib.get("file", FileList()),
            month=bib.get("month"),
            title=title,
            url=bib.get("url"),
            urldate=dates.get("urldate"),
            year=bib.get("year"),
            keywords=bib.get("keywords", SeparatedLiterals()),
        )

    def normalize(self):
        if not self.date and self.eventdate:
            self.date = self.eventdate
        if self.date:
            self.yearmonth.append(str(self.date)[:7])
        if self.eventdate:
            self.yearmonth.append(str(self.eventdate)[:7])

        # remove duplicates
        self.yearmonth = SeparatedLiterals(set(self.yearmonth))
        self.keywords = SeparatedLiterals(set(self.keywords))

    #################
    # JabRef Fields #
    #################
    # priority
    # ranking
    # readstatus

    ############################
    # BibScraper Custom Fields #
    ############################

    # For urls associated to current entry (files, code, data...)
    urls: SeparatedLiterals = field(default_factory=SeparatedLiterals)

    # For awards the paper may have received
    awards: SeparatedLiterals = field(default_factory=SeparatedLiterals)

    # In order to search more easily for most recent articles
    # contains year-month for date and evendate (but not urldate)
    yearmonth: SeparatedLiterals = field(default_factory=SeparatedLiterals)

    ###############
    # Data Fields #
    ###############
    # The fields listed in this section are the regular ones holding printable
    # data in the default data model. The name on the left is the default data
    # model name of the field as used by \\biblatex and its backend. The
    # \\biblatex data type is given to the right of the name. See
    # \\secref{bib:fld:typ} for explanation of the various data types.

    # Some fields are marked as <label> fields which means that they are often
    # used as abbreviation labels when printing bibliography lists in the sense
    # of section \\secref{use:bib:biblist}. \\biblatex automatically creates
    # supporting macros for such fields. See \\secref{use:bib:biblist}.

    abstract: Optional[LiteralField] = None
    # This field is intended for recording abstracts in a \\file{bib} file, to
    # be printed by a special bibliography style. It is not used by all
    # standard bibliography styles.

    # addendum: Optional[LiteralField] = None
    # Miscellaneous bibliographic data to be printed at the end of the entry.
    # This is similar to the \\bibfield{note} field except that it is printed
    # at the end of the bibliography entry.

    # afterword: Optional[NameList] = None
    # The author(s) of an afterword to the work. If the author of the afterword
    # is identical to the \\bibfield{editor} and\\slash or
    # \\bibfield{translator}, the standard styles will automatically
    # concatenate these fields in the bibliography. See also
    # \\bibfield{introduction} and \\bibfield{foreword}.

    # annotation: Optional[LiteralField] = None
    # This field may be useful when implementing a style for annotated
    # bibliographies. It is not used by all standard bibliography styles. Note
    # that this field is completely unrelated to \\bibfield{annotator}. The
    # \\bibfield{annotator} is the author of annotations which
    # are part of the work cited.

    # annotator: Optional[NameList] = None
    # The author(s) of annotations to the work. If the annotator is identical
    # to the \\bibfield{editor} and\\slash or \\bibfield{translator}, the
    # standard styles will automatically concatenate these fields in the
    # bibliography. See also \\bibfield{commentator}.

    author: NameList = field(default_factory=NameList)
    # The author(s) of the \\bibfield{title}.

    # authortype: Optional[KeyField] = None
    # The type of author. This field will affect the string (if any) used to
    # introduce the author. Not used by the standard bibliography styles.

    # bookauthor: Optional[NameList] = None
    # The author(s) of the \\bibfield{booktitle}.

    # bookpagination: Optional[KeyField] = None
    # If the work is published as part of another one, this is the pagination
    # scheme of the enclosing work, \\ie \\bibfield{bookpagination} relates to
    # \\bibfield{pagination} like \\bibfield{booktitle} to \\bibfield{title}.
    # The value of this field will affect the formatting of the
    # \\bibfield{pages} and \\bibfield{pagetotal} fields. The key should be
    # given in the singular form. Possible keys are \\texttt{page},
    # \\texttt{column}, \\texttt{line}, \\texttt{verse}, \\texttt{section}, and
    # \\texttt{paragraph}. See also \\bibfield{pagination} as well
    # as \\secref{bib:use:pag}.

    # booksubtitle: Optional[LiteralField] = None
    # The subtitle related to the \\bibfield{booktitle}. If the
    # \\bibfield{subtitle} field refers to a work which is part of a larger
    # publication, a possible subtitle of the main work is given in this field.
    # See also \\bibfield{subtitle}.

    booktitle: Optional[LiteralField] = None
    # If the \\bibfield{title} field indicates the title of a work which is
    # part of a larger publication, the title of the main work is given in this
    # field. See also \\bibfield{title}.

    # booktitleaddon: Optional[LiteralField] = None
    # An annex to the \\bibfield{booktitle}, to be printed in a different font.

    # chapter: Optional[LiteralField] = None
    # A chapter or section or any other unit of a work.

    # commentator: Optional[NameList] = None
    # The author(s) of a commentary to the work. Note that this field is
    # intended for commented editions which have a commentator in addition to
    # the author. If the work is a stand"=alone commentary, the commentator
    # should be given in the \\bibfield{author} field. If the commentator is
    # identical to the \\bibfield{editor} and\\slash or \\bibfield{translator},
    # the standard styles will automatically concatenate these fields in the
    # bibliography. See also \\bibfield{annotator}.

    date: Optional[DateField] = None
    # The publication date. See also \\bibfield{month} and \\bibfield{year} as
    # well as \\secref{bib:use:dat,bib:use:yearordate}.

    # doi: Optional[VerbatimField] = None
    # The Digital Object Identifier of the work.

    # edition: Union[NoneType, IntegerField, LiteralField] = None
    # The edition of a printed publication. This must be an integer, not an
    # ordinal. Don't say |edition={First}| or |edition={1st}| but
    # |edition={1}|. The bibliography style converts this to a language
    # dependent ordinal. It is also possible to give the edition as a literal
    # string, for example «Third, revised and expanded edition».

    # editor: Optional[NameList] = None
    # The editor(s) of the \\bibfield{title}, \\bibfield{booktitle}, or
    # \\bibfield{maintitle}, depending on the entry type. Use the
    # \\bibfield{editortype} field to specify the role if it is different from
    # <\\texttt{editor}>. See \\secref{bib:use:edr} for further hints.

    # editora: Optional[NameList] = None
    # A secondary editor performing a different editorial role, such as
    # compiling, redacting, etc. Use the \\bibfield{editoratype} field to
    # specify the role. See \\secref{bib:use:edr} for further hints.

    # editorb: Optional[NameList] = None
    # Another secondary editor performing a different role. Use the
    # \\bibfield{editorbtype} field to specify the role. See
    # \\secref{bib:use:edr} for further hints.

    # editorc: Optional[NameList] = None
    # Another secondary editor performing a different role. Use the
    # \\bibfield{editorctype} field to specify the role. See
    # \\secref{bib:use:edr} for further hints.

    # editortype: Optional[KeyField] = None
    # The type of editorial role performed by the \\bibfield{editor}. Roles
    # supported by default are \\texttt{editor}, \\texttt{compiler},
    # \\texttt{founder}, \\texttt{continuator}, \\texttt{redactor},
    # \\texttt{reviser}, \\texttt{collaborator}, \\texttt{organizer}. The role
    # <\\texttt{editor}> is the default. In this case, the field is omissible.
    # See \\secref{bib:use:edr} for further hints.

    # editoratype: Optional[KeyField] = None
    # Similar to \\bibfield{editortype} but referring to the
    # \\bibfield{editora} field. See \\secref{bib:use:edr} for further hints.

    # editorbtype: Optional[KeyField] = None
    # Similar to \\bibfield{editortype} but referring to the
    # \\bibfield{editorb} field. See \\secref{bib:use:edr} for further hints.

    # editorctype: Optional[KeyField] = None
    # Similar to \\bibfield{editortype} but referring to the
    # \\bibfield{editorc} field. See \\secref{bib:use:edr} for further hints.

    # eid: Optional[LiteralField] = None
    # The electronic identifier of an \\bibtype{article} or chapter-like
    # section of a larger work. This field may replace the \\bibfield{pages}
    # field for journals deviating from the classic pagination scheme of
    # printed journals by only enumerating articles or papers and not pages.

    # entrysubtype: Optional[LiteralField] = None
    # This field, which is not used by the standard styles, may be used to
    # specify a subtype of an entry type. This may be useful for bibliography
    # styles which support a finer"=grained set of entry types.

    # eprint: Optional[VerbatimField] = None
    # The electronic identifier of an online publication. This is roughly
    # comparable to a \\acr{doi} but specific to a certain archive, repository,
    # service, or system. See \\secref{use:use:epr} for details. Also see
    # \\bibfield{eprinttype} and \\bibfield{eprintclass}.

    # eprintclass: Optional[LiteralField] = None
    # Additional information related to the resource indicated by the
    # \\bibfield{eprinttype} field. This could be a section of an archive, a
    # path indicating a service, a classification of some sort, etc. See
    # \\secref{use:use:epr} for details. Also see \\bibfield{eprint}
    # and \\bibfield{eprinttype}.

    # eprinttype: Optional[LiteralField] = None
    # The type of \\bibfield{eprint} identifier, \\eg the name of the archive,
    # repository, service, or system the \\bibfield{eprint} field refers to.
    # See \\secref{use:use:epr} for details. Also see \\bibfield{eprint}
    # and \\bibfield{eprintclass}.

    eventdate: Optional[DateField] = None
    # The date of a conference, a symposium, or some other event in
    # \\bibtype{proceedings} and \\bibtype{inproceedings} entries. This field
    # may also be useful for the custom types listed in \\secref{bib:typ:ctm}.
    # See also \\bibfield{eventtitle} and \\bibfield{venue} as well
    # as \\secref{bib:use:dat}.

    # eventtitle: Optional[LiteralField] = None
    # The title of a conference, a symposium, or some other event in
    # \\bibtype{proceedings} and \\bibtype{inproceedings} entries. This field
    # may also be useful for the custom types listed in \\secref{bib:typ:ctm}.
    # Note that this field holds the plain title of the event. Things like
    # «Proceedings of the Fifth XYZ Conference» go into the
    # \\bibfield{titleaddon} or \\bibfield{booktitleaddon} field, respectively.
    # See also \\bibfield{eventdate} and \\bibfield{venue}.

    # eventtitleaddon: Optional[LiteralField] = None
    # An annex to the \\bibfield{eventtitle} field. Can be used for known
    # event acronyms, for example.

    file: FileList = field(default_factory=FileList)
    # A local link to a \\acr{pdf} or other version of the work. Not used by
    # the standard bibliography styles.

    # foreword: Optional[NameList] = None
    # The author(s) of a foreword to the work. If the author of the foreword is
    # identical to the \\bibfield{editor} and\\slash or \\bibfield{translator},
    # the standard styles will automatically concatenate these fields in the
    # bibliography. See also \\bibfield{introduction} and
    # \\bibfield{afterword}.

    # holder: Optional[NameList] = None
    # The holder(s) of a \\bibtype{patent}, if different from the
    # \\bibfield{author}. Note that corporate holders need to be wrapped in an
    # additional set of braces, see \\secref{bib:use:inc} for details. This
    # list may also be useful for the custom types listed
    # in \\secref{bib:typ:ctm}.

    # howpublished: Optional[LiteralField] = None
    # A publication notice for unusual publications which do not fit into any
    # of the common categories.

    # indextitle: Optional[LiteralField] = None
    # A title to use for indexing instead of the regular \\bibfield{title}
    # field. This field may be useful if you have an entry with a title like
    # «An Introduction to \\dots» and want that indexed as «Introduction to
    # \\dots, An». Style authors should note that \\biblatex automatically
    # copies the value of the \\bibfield{title} field to \\bibfield{indextitle}
    # if the latter field is undefined.

    # institution: Optional[LiteralList] = None
    # The name of a university or some other institution, depending on the
    # entry type. Traditional \\bibtex uses the field name \\bibfield{school}
    # for theses, which is supported as an alias. See also
    # \\secref{bib:fld:als, bib:use:and}.

    # introduction: Optional[NameList] = None
    # The author(s) of an introduction to the work. If the author of the
    # introduction is identical to the \\bibfield{editor} and\\slash or
    # \\bibfield{translator}, the standard styles will automatically
    # concatenate these fields in the bibliography. See also
    # \\bibfield{foreword} and \\bibfield{afterword}.

    # isan: Optional[LiteralField] = None
    # The International Standard Audiovisual Number of an audiovisual work. Not
    # used by the standard bibliography styles.

    # isbn: Optional[LiteralField] = None
    # The International Standard Book Number of a book.

    # ismn: Optional[LiteralField] = None
    # The International Standard Music Number for printed music such as musical
    # scores. Not used by the standard bibliography styles.

    # isrn: Optional[LiteralField] = None
    # The International Standard Technical Report Number of a technical report.

    # issn: Optional[LiteralField] = None
    # The International Standard Serial Number of a periodical.

    # issue: Optional[LiteralField] = None
    # The issue of a journal. This field is intended for journals whose
    # individual issues are identified by a designation such as <Spring> or
    # <Summer> rather than the month or a number. The placement of
    # \\bibfield{issue} is similar to \\bibfield{month} and \\bibfield{number}.
    # Integer ranges and short designators are better written to the
    # \\bibfield{number} field. See also \\bibfield{month}, \\bibfield{number}
    # and \\secref{bib:use:iss, bib:use:issnum}.

    # issuesubtitle: Optional[LiteralField] = None
    # The subtitle of a specific issue of a journal or other periodical.

    # issuetitle: Optional[LiteralField] = None
    # The title of a specific issue of a journal or other periodical.

    # issuetitleaddon: Optional[LiteralField] = None
    # An annex to the \\bibfield{issuetitle}, to be printed in a different
    # font.

    # iswc: Optional[LiteralField] = None
    # The International Standard Work Code of a musical work. Not used by the
    # standard bibliography styles.

    # journalsubtitle: Optional[LiteralField] = None
    # The subtitle of a journal, a newspaper, or some other periodical.

    journaltitle: Optional[LiteralField] = None
    # The name of a journal, a newspaper, or some other periodical.

    # journaltitleaddon: Optional[LiteralField] = None
    # An annex to the \\bibfield{journaltitle}, to be printed in a different
    # font.

    # label: Optional[LiteralField] = None
    # A designation to be used by the citation style as a substitute for the
    # regular label if any data required to generate the regular label is
    # missing. For example, when an author"=year citation style is generating a
    # citation for an entry which is missing the author or the year, it may
    # fall back to \\bibfield{label}. See \\secref{bib:use:key} for details.
    # Note that, in contrast to \\bibfield{shorthand}, \\bibfield{label} is
    # only used as a fallback. See also \\bibfield{shorthand}.

    # language: Optional[KeyList] = None
    # The language(s) of the work. Languages may be specified literally or as
    # localisation keys. If localisation keys are used, the prefix
    # \\texttt{lang} is omissible. See also \\bibfield{origlanguage} and
    # compare \\bibfield{langid} in \\secref{bib:fld:spc}.

    # library: Optional[LiteralField] = None
    # This field may be useful to record information such as a library name and
    # a call number. This may be printed by a special bibliography style if
    # desired. Not used by the standard bibliography styles.

    # location: Optional[LiteralList] = None
    # The place(s) of publication, \\ie the location of the
    # \\bibfield{publisher} or \\bibfield{institution}, depending on the entry
    # type. Traditional \\bibtex uses the field name \\bibfield{address}, which
    # is supported as an alias. See also \\secref{bib:fld:als, bib:use:and}.
    # With \\bibtype{patent} entries, this list indicates the scope of a
    # patent. This list may also be useful for the custom types listed
    # in \\secref{bib:typ:ctm}.

    # mainsubtitle: Optional[LiteralField] = None
    # The subtitle related to the \\bibfield{maintitle}. See
    # also \\bibfield{subtitle}.

    # maintitle: Optional[LiteralField] = None
    # The main title of a multi"=volume book, such as \\emph{Collected Works}.
    # If the \\bibfield{title} or \\bibfield{booktitle} field indicates the
    # title of a single volume which is part of multi"=volume book, the title
    # of the complete work is given in this field.

    # maintitleaddon: Optional[LiteralField] = None
    # An annex to the \\bibfield{maintitle}, to be printed in a different font.

    month: Optional[LiteralField] = None
    # The publication month. This must be an integer, not an ordinal or a
    # string. Don't say |month={January}| but |month={1}|. The bibliography
    # style converts this to a language dependent string or ordinal where
    # required. This field is a literal field only when given explicitly in the
    # data (for plain \\bibtex compatibility for example). It is however better
    # to use the \\bibfield{date} field as this supports many more features.
    # See \\secref{bib:use:dat,bib:use:yearordate}.

    # nameaddon: Optional[LiteralField] = None
    # An addon to be printed immediately after the author name in the
    # bibliography. Not used by the standard bibliography styles. This field
    # may be useful to add an alias or pen name (or give the real name if the
    # pseudonym is commonly used to refer to that author).

    # note: Optional[LiteralField] = None
    # Miscellaneous bibliographic data which does not fit into any other field.
    # The \\bibfield{note} field may be used to record bibliographic data in a
    # free format. Publication facts such as «Reprint of the edition London
    # 1831» are typical candidates for the \\bibfield{note} field. See
    # also \\bibfield{addendum}.

    # number: Optional[LiteralField] = None
    # The number of a journal or the volume\\slash number of a book in a
    # \\bibfield{series}. See also \\bibfield{issue} as well as
    # \\secref{bib:use:ser, bib:use:iss, bib:use:issnum}. With
    # \\bibtype{patent} entries, this is the number or record token of a patent
    # or patent request. Normally this field will be an integer or an integer
    # range, but it may also be a short designator that is not entirely numeric
    # such as «S1», «Suppl.\\ 2», «3es». In these cases the output should
    # be scrutinised carefully.

    # Since \\bibfield{number} is---maybe counterintuitively given its name---a
    # literal field, sorting templates will not treat its contents as integers,
    # but as literal strings, which means that «11» may sort between «1» and
    # «2». If integer sorting is desired, the field can be declared an integer
    # field in a custom data model (see \\secref{aut:ctm:dm}). But then the
    # sorting of non-integer values is not well defined.

    # organization: Optional[LiteralList] = None
    # The organization(s) that published a \\bibtype{manual} or an
    # \\bibtype{online} resource, or sponsored a conference. See
    # also \\secref{bib:use:and}.

    # origdate: Optional[DateField] = None
    # If the work is a translation, a reprint, or something similar, the
    # publication date of the original edition. Not used by the standard
    # bibliography styles. See also \\bibfield{date}.

    # origlanguage: Optional[KeyList] = None
    # If the work is a translation, the language(s) of the original work. See
    # also \\bibfield{language}.

    # origlocation: Optional[LiteralList] = None
    # If the work is a translation, a reprint, or something similar, the
    # \\bibfield{location} of the original edition. Not used by the standard
    # bibliography styles. See also \\bibfield{location}
    # and \\secref{bib:use:and}.

    # origpublisher: Optional[LiteralList] = None
    # If the work is a translation, a reprint, or something similar, the
    # \\bibfield{publisher} of the original edition. Not used by the standard
    # bibliography styles. See also \\bibfield{publisher}
    # and \\secref{bib:use:and}.

    # origtitle: Optional[LiteralField] = None
    # If the work is a translation, the \\bibfield{title} of the original work.
    # Not used by the standard bibliography styles. See also \\bibfield{title}.

    # pages: Optional[RangeField] = None
    # One or more page numbers or page ranges. If the work is published as part
    # of another one, such as an article in a journal or a collection, this
    # field holds the relevant page range in that other work. It may also be
    # used to limit the reference to a specific part of a work (a chapter in a
    # book, for example). For papers in electronic journals with a
    # non-classical pagination setup the \\bibfield{eid}
    # field may be more suitable.

    # pagetotal: Optional[LiteralField] = None
    # The total number of pages of the work.

    # pagination: Optional[KeyField] = None
    # The pagination of the work. The value of this field will affect the
    # formatting the \\prm{postnote} argument to a citation command. The key
    # should be given in the singular form. Possible keys are \\texttt{page},
    # \\texttt{column}, \\texttt{line}, \\texttt{verse}, \\texttt{section}, and
    # \\texttt{paragraph}. See also \\bibfield{bookpagination} as well as
    # \\secref{bib:use:pag, use:cav:pag}.

    # part: Optional[LiteralField] = None
    # The number of a partial volume. This field applies to books only, not to
    # journals. It may be used when a logical volume consists of two or more
    # physical ones. In this case the number of the logical volume goes in the
    # \\bibfield{volume} field and the number of the part of that volume in the
    # \\bibfield{part} field. See also \\bibfield{volume}.

    # publisher: Optional[LiteralList] = None
    # The name(s) of the publisher(s). See also \\secref{bib:use:and}.

    # pubstate: Optional[KeyField] = None
    # The publication state of the work, \\eg\\ <in press>. See
    # \\secref{aut:lng:key:pst} for known publication states.

    # reprinttitle: Optional[LiteralField] = None
    # The title of a reprint of the work. Not used by the standard styles.

    # series: Optional[LiteralField] = None
    # The name of a publication series, such as «Studies in \\dots», or the
    # number of a journal series. Books in a publication series are usually
    # numbered. The number or volume of a book in a series is given in the
    # \\bibfield{number} field. Note that the \\bibtype{article} entry type
    # makes use of the \\bibfield{series} field as well, but handles it in a
    # special way. See \\secref{bib:use:ser} for details.

    # shortauthor: Optional[NameList] = None
    # The author(s) of the work, given in an abbreviated form. This field is
    # mainly intended for abbreviated forms of corporate authors, see
    # \\secref{bib:use:inc} for details.

    # shorteditor: Optional[NameList] = None
    # The editor(s) of the work, given in an abbreviated form. This field is
    # mainly intended for abbreviated forms of corporate editors, see
    # \\secref{bib:use:inc} for details.

    # shorthand: Optional[LiteralField] = None
    # A special designation to be used by the citation style instead of the
    # usual label. If defined, it overrides the default label.
    # See also \\bibfield{label}.

    # shorthandintro: Optional[LiteralField] = None
    # The verbose citation styles which comes with this package use a phrase
    # like «henceforth cited as [shorthand]» to introduce shorthands on the
    # first citation. If the \\bibfield{shorthandintro} field is defined, it
    # overrides the standard phrase. Note that the alternative phrase
    # must include the shorthand.

    # shortjournal: Optional[LiteralField] = None
    # A short version or an acronym of the \\bibfield{journaltitle}. Not used
    # by the standard bibliography styles.

    # shortseries: Optional[LiteralField] = None
    # A short version or an acronym of the \\bibfield{series} field. Not used
    # by the standard bibliography styles.

    # shorttitle: Optional[LiteralField] = None
    # The title in an abridged form. This field is usually not included in the
    # bibliography. It is intended for citations in author"=title format. If
    # present, the author"=title citation styles use this field
    # instead of \\bibfield{title}.

    # subtitle: Optional[LiteralField] = None
    # The subtitle of the work.

    title: Optional[LiteralField] = None
    # The title of the work.

    # titleaddon: Optional[LiteralField] = None
    # An annex to the \\bibfield{title}, to be printed in a different font.

    # translator: Optional[NameList] = None
    # The translator(s) of the \\bibfield{title} or \\bibfield{booktitle},
    # depending on the entry type. If the translator is identical to the
    # \\bibfield{editor}, the standard styles will automatically concatenate
    # these fields in the bibliography.

    # type: Optional[KeyField] = None
    # The type of a \\bibfield{manual}, \\bibfield{patent}, \\bibfield{report},
    # or \\bibfield{thesis}. This field may also be useful for the custom types
    # listed in \\secref{bib:typ:ctm}.

    url: Optional[UriField] = None
    # The \\acr{URL} of an online publication. If it is not URL-escaped (no
    # <\\%> chars) it will be URI-escaped according to RFC 3987, that is, even
    # Unicode chars will be correctly escaped.

    urldate: Optional[DateField] = None
    # The access date of the address specified in the \\bibfield{url} field.
    # See also \\secref{bib:use:dat}.

    # venue: Optional[LiteralField] = None
    # The location of a conference, a symposium, or some other event in
    # \\bibtype{proceedings} and \\bibtype{inproceedings} entries. This field
    # may also be useful for the custom types listed in \\secref{bib:typ:ctm}.
    # Note that the \\bibfield{location} list holds the place of publication.
    # It therefore corresponds to the \\bibfield{publisher} and
    # \\bibfield{institution} lists. The location of the event is given in the
    # \\bibfield{venue} field. See also \\bibfield{eventdate}
    # and \\bibfield{eventtitle}.

    # version: Optional[LiteralField] = None
    # The revision number of a piece of software, a manual, etc.

    # volume: Optional[IntegerField] = None
    # The volume of a multi"=volume book or a periodical. It is expected to be
    # an integer, not necessarily in arabic numerals since \\biber will
    # automatically convert from roman numerals or arabic letter to integers
    # internally for sorting purposes. See also \\bibfield{part}. See the
    # \\opt{noroman} option which can be used to suppress roman numeral
    # parsing. This can help in cases where there is an ambiguity between
    # parsing as roman numerals or alphanumeric (e.g. <C>), see
    # \\secref{use:opt:pre:int}.

    # volumes: Optional[IntegerField] = None
    # The total number of volumes of a multi"=volume work. Depending on the
    # entry type, this field refers to \\bibfield{title} or
    # \\bibfield{maintitle}. It is expected to be an integer, not necessarily
    # in arabic numerals since \\biber will automatically convert from roman
    # numerals or arabic letter to integers internally for sorting purposes.
    # See the \\opt{noroman} option which can be used to suppress roman numeral
    # parsing. This can help in cases where there is an ambiguity between
    # parsing as roman numerals or alphanumeric (e.g. <C>), see
    # \\secref{use:opt:pre:int}.

    year: Optional[LiteralField] = None
    # The year of publication. This field is a literal field only when given
    # explicitly in the data (for plain \\bibtex compatibility for example). It
    # is however better to use the \\bibfield{date} field as this is compatible
    # with plain years too and supports many more features. See
    # \\secref{bib:use:dat,bib:use:yearordate}.

    ##################
    # Special Fields #
    ##################
    # The fields listed in this section do not hold printable data but serve a
    # different purpose. They apply to all entry types in the default data
    # model.

    # \\fielditem{crossref}{entry key}
    # This field holds an entry key for the cross"=referencing feature. Child
    # entries with a \\bibfield{crossref} field inherit data from the parent
    # entry specified in the \\bibfield{crossref} field. If the number of child
    # entries referencing a specific parent entry hits a certain threshold, the
    # parent entry is automatically added to the bibliography even if it has
    # not been cited explicitly. The threshold is settable with the
    # \\opt{mincrossrefs} package option from \\secref{use:opt:pre:gen}. Style
    # authors should note that whether or not the \\bibfield{crossref} fields
    # of the child entries are defined on the \\biblatex level depends on the
    # availability of the parent entry. If the parent entry is available, the
    # \\bibfield{crossref} fields of the child entries will be defined. If not,
    # the child entries still inherit the data from the parent entry but their
    # \\bibfield{crossref} fields will be undefined. Whether the parent entry
    # is added to the bibliography implicitly because of the threshold or
    # explicitly because it has been cited does not matter. See also the
    # \\bibfield{xref} field in this section as well as \\secref{bib:cav:ref}.

    # \\fielditem{entryset}{separated values}
    # This field is specific to entry sets. See \\secref{use:use:set} for
    # details. This field is consumed by the backend processing and does not
    # appear in the \\path{.bbl}.

    # execute: Optional[CodeField] = None
    # A special field which holds arbitrary \\tex code to be executed whenever
    # the data of the respective entry is accessed. This may be useful to
    # handle special cases. Conceptually, this field is comparable to the hooks
    # \\cmd{AtEveryBibitem}, \\cmd{AtEveryLositem}, and \\cmd{AtEveryCitekey}
    # from \\secref{aut:fmt:hok}, except that it is definable on a per"=entry
    # basis in the \\file{bib} file. Any code in this field is executed
    # automatically immediately after these hooks.

    # \\fielditem{gender}{Pattern matching one of: \\opt{sf}, \\opt{sm},
    # \\opt{sn}, \\opt{pf}, \\opt{pm}, \\opt{pn}, \\opt{pp}}
    # The gender of the author or the gender of the editor, if there is no
    # author. The following identifiers are supported: \\opt{sf} (feminine
    # singular, a single female name), \\opt{sm} (masculine singular, a single
    # male name), \\opt{sn} (neuter singular, a single neuter name), \\opt{pf}
    # (feminine plural, a list of female names), \\opt{pm} (masculine plural, a
    # list of male names), \\opt{pn} (neuter plural, a list of neuter names),
    # \\opt{pp} (plural, a mixed gender list of names). This information is
    # only required by special bibliography and citation styles and only in
    # certain languages. For example, a citation style may replace recurrent
    # author names with a term such as <idem>. If the Latin word is used, as is
    # custom in English and French, there is no need to specify the gender. In
    # German publications, however, such key terms are usually given in German
    # and in this case they are gender"=sensitive.

    # langid: Optional[IdentifierField] = None
    # The language id of the bibliography entry. The alias
    # \\bibfield{hyphenation} is provided for backwards compatibility. The
    # identifier must be a language name known to the
    # \\sty{babel}/\\sty{polyglossia} packages. This information may be used to
    # switch hyphenation patterns and localise strings in the bibliography.
    # Note that the language names are case sensitive. The languages currently
    # supported by this package are given in \\tabref{bib:fld:tab1}. Note that
    # \\sty{babel} treats the identifier \\opt{english} as an alias for
    # \\opt{british} or \\opt{american}, depending on the \\sty{babel} version.
    # The \\biblatex package always treats it as an alias for \\opt{american}.
    # It is preferable to use the language identifiers \\opt{american} and
    # \\opt{british} (\\sty{babel}) or a language specific option to specify a
    # language variant (\\sty{polyglossia}, using the \\bibfield{langidopts}
    # field) to avoid any possible confusion. Compare \\bibfield{language}
    # in \\secref{bib:fld:dat}.

    # langidopts: Optional[LiteralField] = None
    # For \\sty{polyglossia} users, allows per-entry language specific options.
    # The literal value of this field is passed to \\sty{polyglossia}'s
    # language switching facility when using the package option
    # \\opt{autolang=langname}.

    # \\fielditem{ids}{separated list of entrykeys}
    # Citation key aliases for the main citation key. An entry may be cited by
    # any of its aliases and \\biblatex will treat the citation as if it had
    # used the primary citation key. This is to aid users who change their
    # citation keys but have legacy documents which use older keys for the same
    # entry. This field is consumed by the backend processing and does not
    # appear in the \\path{.bbl}.

    # indexsorttitle: Optional[LiteralField] = None
    # The title used when sorting the index. In contrast to
    # \\bibfield{indextitle}, this field is used for sorting only. The printed
    # title in the index is the \\bibfield{indextitle} or the \\bibfield{title}
    # field. This field may be useful if the title contains special characters
    # or commands which interfere with the sorting of the
    # index.

    keywords: SeparatedLiterals = field(default_factory=SeparatedLiterals)
    # A separated list of keywords. These keywords are intended for the
    # bibliography filters (see \\secref{use:bib:bib, use:use:div}), they are
    # usually not printed. Note that with the default separator (comma), spaces
    # around the separator are ignored.

    # \\fielditem{options}{separated \\keyval options}
    # A separated list of entry options in \\keyval notation. This field is
    # used to set options on a per"=entry basis. See \\secref{use:opt:bib} for
    # details. Note that citation and bibliography styles may define
    # additional entry options.

    # presort: Optional[StringField] = None
    # A special field used to modify the sorting order of the bibliography.
    # This field is the first item the sorting routine considers when sorting
    # the bibliography, hence it may be used to arrange the entries in groups.
    # This may be useful when creating subdivided bibliographies with the
    # bibliography filters. Please refer to \\secref{use:srt} for further
    # details. Also see \\secref{aut:ctm:srt}. This field is consumed by the
    # backend processing and does not appear in the \\path{.bbl}.

    # \\fielditem{related}{separated values}
    # Citation keys of other entries which have a relationship to this entry.
    # The relationship is specified by the \\bibfield{relatedtype} field.
    # Please refer to \\secref{use:rel} for further details.

    # \\fielditem{relatedoptions}{separated values}
    # Per"=type options to set for a related entry. Note that this does not set
    # the options on the related entry itself, only the \\opt{dataonly} clone
    # which is used as a datasource for the parent entry.

    # relatedtype: Optional[IdentifierField] = None
    # An identifier which specified the type of relationship for the keys
    # listed in the \\bibfield{related} field. The identifier is a localised
    # bibliography string printed
    # before the data from the related entry list. It is also used
    # to identify type-specific
    # formatting directives and bibliography macros for the related entries.
    # Please refer to \\secref{use:rel} for further details.

    # relatedstring: Optional[LiteralField] = None
    # A field used to override the bibliography string specified by
    # \\bibfield{relatedtype}. Please refer to \\secref{use:rel} for further
    # details.

    # sortkey: Optional[LiteralField] = None
    # A field used to modify the sorting order of the bibliography. Think of
    # this field as the master sort key. If present, \\biblatex uses this field
    # during sorting and ignores everything else, except for the
    # \\bibfield{presort} field. Please refer to \\secref{use:srt} for further
    # details. This field is consumed by the backend processing and does not
    # appear in the \\path{.bbl}.

    # sortname: Optional[NameList] = None
    # A name or a list of names used to modify the sorting order of the
    # bibliography. If present, this list is used instead of \\bibfield{author}
    # or \\bibfield{editor} when sorting the bibliography. Please refer to
    # \\secref{use:srt} for further details. This field is consumed by the
    # backend processing and does not appear in the \\path{.bbl}.

    # sortshorthand: Optional[LiteralField] = None
    # Similar to \\bibfield{sortkey} but used in the list of shorthands. If
    # present, \\biblatex uses this field instead of \\bibfield{shorthand} when
    # sorting the list of shorthands. This is useful if the
    # \\bibfield{shorthand} field holds shorthands with formatting commands
    # such as \\cmd{emph} or \\cmd{textbf}. This field is consumed by the
    # backend processing and does not appear in the \\path{.bbl}.

    # sorttitle: Optional[LiteralField] = None
    # A field used to modify the sorting order of the bibliography. If present,
    # this field is used instead of the \\bibfield{title} field when sorting
    # the bibliography. The \\bibfield{sorttitle} field may come in handy if
    # you have an entry with a title like «An Introduction to\\dots» and want
    # that alphabetized under <I> rather than <A>. In this case, you could put
    # «Introduction to\\dots» in the \\bibfield{sorttitle} field. Please refer
    # to \\secref{use:srt} for further details. This field is consumed by the
    # backend processing and does not appear in the \\path{.bbl}.

    # sortyear: Optional[IntegerField] = None
    # A field used to modify the sorting order of the bibliography. In the
    # default sorting templates, if this field is present, it is used instead
    # of the \\bibfield{year} field when sorting the bibliography. Please refer
    # to \\secref{use:srt} for further details. This field is consumed by the
    # backend processing and does not appear in the \\path{.bbl}.

    # \\fielditem{xdata}{separated list of entrykeys}
    # This field inherits data from one or more \\bibtype{xdata} entries.
    # Conceptually, the \\bibfield{xdata} field is related to
    # \\bibfield{crossref} and \\bibfield{xref}: \\bibfield{crossref}
    # establishes a logical parent/child relation and inherits data;
    # \\bibfield{xref} establishes as logical parent/child relation without
    # inheriting data; \\bibfield{xdata} inherits data without establishing a
    # relation. The value of the \\bibfield{xdata} may be a single entry key or
    # a separated list of keys. See \\secref{use:use:xdat} for further details.
    # This field is consumed by the backend processing and does not
    # appear in the \\path{.bbl}.

    # \\fielditem{xref}{entry key}
    # This field is an alternative cross"=referencing mechanism. It differs
    # from \\bibfield{crossref} in that the child entry will not inherit any
    # data from the parent entry specified in the \\bibfield{xref} field. If
    # the number of child entries referencing a specific parent entry hits a
    # certain threshold, the parent entry is automatically added to the
    # bibliography even if it has not been cited explicitly. The threshold is
    # settable with the \\opt{minxrefs} package option from
    # \\secref{use:opt:pre:gen}. Style authors should note that whether or not
    # the \\bibfield{xref} fields of the child entries are defined on the
    # \\biblatex level depends on the availability of the parent entry. If the
    # parent entry is available, the \\bibfield{xref} fields of the child
    # entries will be defined. If not, their \\bibfield{xref} fields will be
    # undefined. Whether the parent entry is added to the bibliography
    # implicitly because of the threshold or explicitly because it has been
    # cited does not matter. See also the \\bibfield{crossref} field in this
    # section as well as \\secref{bib:cav:ref}.

    #################
    # Custom Fields #
    #################
    # The fields listed in this section are intended for special bibliography
    # styles. They are not used by the standard bibliography styles.

    # \\listitem{name{[a--c]}}{name}
    # Custom lists for special bibliography styles. Not used by the
    # standard bibliography styles.

    # \\fielditem{name{[a--c]}type}{key}
    # Similar to \\bibfield{authortype} and \\bibfield{editortype} but
    # referring to the fields \\bibfield{name{[a--c]}}. Not used by the
    # standard bibliography styles.

    # \\listitem{list{[a--f]}}{literal}
    # Custom lists for special bibliography styles. Not used by the
    # standard bibliography styles.

    # \\fielditem{user{[a--f]}}{literal}
    # Custom fields for special bibliography styles. Not used by the
    # standard bibliography styles.

    # \\fielditem{verb{[a--c]}}{literal}
    # Similar to the custom fields above except that these are verbatim fields.
    # Not used by the standard bibliography styles.

    #################
    # Field Aliases #
    #################
    # The aliases listed in this section are provided for backwards
    # compatibility with traditional \\bibtex and other applications based on
    # traditional \\bibtex styles. Note that these aliases are immediately
    # resolved as the \\file{bib} file is processed. All bibliography and
    # citation styles must use the names of the fields they point to, not the
    # alias. In \\file{bib} files, you may use either the alias or the field
    # name but not both at the same time.

    # address: Optional[LiteralList] = None
    # An alias for \\bibfield{location}, provided for \\bibtex compatibility.
    # Traditional \\bibtex uses the slightly misleading field name
    # \\bibfield{address} for the place of publication, \\ie the location of
    # the publisher, while \\biblatex uses the generic field name
    # \\bibfield{location}. See \\secref{bib:fld:dat,bib:use:and}.

    # annote: Optional[LiteralField] = None
    # An alias for \\bibfield{annotation}, provided for \\sty{jurabib}
    # compatibility. See \\secref{bib:fld:dat}.

    # archiveprefix: Optional[LiteralField] = None
    # An alias for \\bibfield{eprinttype}, provided for arXiv compatibility.
    # See \\secref{bib:fld:dat,use:use:epr}.

    # journal: Optional[LiteralField] = None
    # An alias for \\bibfield{journaltitle}, provided for \\bibtex
    # compatibility. See \\secref{bib:fld:dat}.

    # key: Optional[LiteralField] = None
    # An alias for \\bibfield{sortkey}, provided for \\bibtex compatibility.
    # See \\secref{bib:fld:spc}.

    # pdf: Optional[VerbatimField] = None
    # An alias for \\bibfield{file}, provided for JabRef compatibility.
    # See \\secref{bib:fld:dat}.

    # primaryclass: Optional[LiteralField] = None
    # An alias for \\bibfield{eprintclass}, provided for arXiv compatibility.
    # See \\secref{bib:fld:dat,use:use:epr}.

    # school: Optional[LiteralList] = None
    # An alias for \\bibfield{institution}, provided for \\bibtex
    # compatibility. The \\bibfield{institution} field is used by traditional
    # \\bibtex for technical reports whereas the \\bibfield{school} field holds
    # the institution associated with theses. The \\biblatex package employs
    # the generic field name \\bibfield{institution} in both cases. See
    # \\secref{bib:fld:dat,bib:use:and}.
