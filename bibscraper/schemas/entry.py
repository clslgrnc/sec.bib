# Entry types as defined in biblatex documentation:
# https://raw.githubusercontent.com/plk/biblatex/dev/doc/latex/biblatex/biblatex.tex
# Before defining a custom entry type check if an existing one would be
# relevant.

# Prefer the ones recognized by jabref:
# src/main/java/org/jabref/model/entry/types/StandardEntryType.java

from enum import Enum


class EntryType(Enum):
    """This section gives an overview of the entry types supported by the
    default biblatex data model along with the fields supported by each type.
    """

    @classmethod
    def from_str(cls, string: str) -> "EntryType":
        if string.strip().lower() == "conference":
            return EntryType.INPROCEEDINGS

        entry_type = EntryType.MISC
        try:
            entry_type = EntryType(string.lower())
        except ValueError:
            pass
        return entry_type

    ######################
    # Custom Entry Types #
    ######################
    # Check for existing types first

    #################
    # Regular Types #
    #################
    # Uncomment and format used types

    # The lists below indicate the fields supported by each entry type. Note
    # that the mapping of fields to an entry type is ultimately at the
    # discretion of the bibliography style. The lists below therefore serve
    # two purposes. They indicate the fields supported by the standard styles
    # which come with this package and they also serve as a model for custom
    # styles. Note that the <required> fields are not strictly required in all
    # cases, see \\secref{bib:use:key} for details. The fields marked as
    # <optional> are optional in a technical sense. Bibliographical formatting
    # rules usually require more than just the <required> fields. The default
    # data model defined a few constraints for the format of date fields,
    # ISBNs and some special fields like \\bibfield{gender} but the
    # constraints are only used if validating against the data model with
    # \\biber's \\opt{--validate-datamodel} option. Generic fields like
    # \\bibfield{abstract} and \\bibfield{annotation} or \\bibfield{label} and
    # \\bibfield{shorthand} are not included in the lists below because they
    # are independent of the entry type. The special fields discussed in
    # \\secref{bib:fld:spc}, which are also independent of the entry type, are
    # not included in the lists either. See the default data model
    # specification in the file \\file{blx-dm.def} which comes with \\biblatex
    # for a complete specification.

    # The <alias> relation referred to in this subsection is the <soft alias>
    # defined with \\cmd{DeclareBibliographyAlias}. That means that the alias
    # will use the same bibliography driver as the type it is aliased to, but
    # that its type-specific formatting is still handled independently of the
    # aliased type.

    # ARTICLE = "article"
    # An article in a journal, magazine, newspaper, or other periodical which
    # forms a self-contained unit with its own title. The title of the
    # periodical is given in the \\bibfield{journaltitle} field. If the issue
    # has its own title in addition to the main title of the periodical, it
    # goes in the \\bibfield{issuetitle} field. Note that \\bibfield{editor}
    # and related fields refer to the journal while \\bibfield{translator} and
    # related fields refer to the article.
    # Required: author, title, journaltitle, year/date
    # Optional: translator, annotator, commentator, subtitle, titleaddon,
    # editor, editora, editorb, editorc, journalsubtitle, journaltitleaddon,
    # issuetitle, issuesubtitle, issuetitleaddon, language, origlanguage,
    # series, volume, number, eid, issue, month, pages, version, note, issn,
    # addendum, pubstate, doi, eprint, eprintclass, eprinttype, url, urldate

    # BOOK = "book"
    # A single"=volume book with one or more authors where the authors share
    # credit for the work as a whole. This entry type also covers the function
    # of the \\bibtype{inbook} type of traditional \\bibtex, see
    # \\secref{bib:use:inb} for details.
    # Required: author, title, year/date
    # Optional: editor, editora, editorb, editorc, translator, annotator,
    # commentator, introduction, foreword, afterword, subtitle, titleaddon,
    # maintitle, mainsubtitle, maintitleaddon, language, origlanguage, volume,
    # part, edition, volumes, series, number, note, publisher, location, isbn,
    # eid, chapter, pages, pagetotal, addendum, pubstate, doi, eprint,
    # eprintclass, eprinttype, url, urldate

    # MVBOOK = "mvbook"
    # A multi"=volume \\bibtype{book}. For backwards compatibility,
    # multi"=volume books are also supported by the entry type \\bibtype{book}.
    # However, it is advisable to make use of the dedicated entry type
    # \\bibtype{mvbook}.
    # Required: author, title, year/date
    # Optional: editor, editora, editorb, editorc, translator, annotator,
    # commentator, introduction, foreword, afterword, subtitle, titleaddon,
    # language, origlanguage, edition, volumes, series, number, note,
    # publisher, location, isbn, pagetotal, addendum, pubstate, doi, eprint,
    # eprintclass, eprinttype, url, urldate

    # INBOOK = "inbook"
    # A part of a book which forms a self"=contained unit with its own title.
    # Note that the profile of this entry type is different from standard
    # \\bibtex, see \\secref{bib:use:inb}.
    # Required: author, title, booktitle, year/date
    # Optional: bookauthor, editor, editora, editorb, editorc, translator,
    # annotator, commentator, introduction, foreword, afterword, subtitle,
    # titleaddon, maintitle, mainsubtitle, maintitleaddon, booksubtitle,
    # booktitleaddon, language, origlanguage, volume, part, edition, volumes,
    # series, number, note, publisher, location, isbn, eid, chapter, pages,
    # addendum, pubstate, doi, eprint, eprintclass, eprinttype, url, urldate

    # BOOKINBOOK = "bookinbook"
    # This type is similar to \\bibtype{inbook} but intended for works
    # originally published as a stand-alone book. A typical example are
    # books reprinted in the collected works of an author.

    # SUPPBOOK = "suppbook"
    # Supplemental material in a \\bibtype{book}. This type is closely related
    # to the \\bibtype{inbook} entry type. While \\bibtype{inbook} is primarily
    # intended for a part of a book with its own title (\\eg a single essay
    # in
    # a collection of essays by the same author), this type is provided for
    # elements such as prefaces, introductions, forewords, afterwords, etc.
    # which often have a generic title only. Style guides may require such
    # items to be formatted differently from other \\bibtype{inbook} items. The
    # standard styles will treat this entry type as an alias for
    # \\bibtype{inbook}.

    # BOOKLET = "booklet"
    # A book"=like work without a formal publisher or sponsoring institution.
    # Use the field \\bibfield{howpublished} to supply publishing information
    # in free format, if applicable. The field \\bibfield{type} may be useful
    # as well.
    # Required: author/editor, title, year/date
    # Optional: subtitle, titleaddon, language, howpublished, type, note,
    # location, eid, chapter, pages, pagetotal, addendum, pubstate,
    # doi, eprint, eprintclass, eprinttype, url, urldate

    # COLLECTION = "collection"
    # A single"=volume collection with multiple, self"=contained contributions
    # by distinct authors which have their own title. The work as a whole has
    # no overall author but it will usually have an editor.
    # Required: editor, title, year/date
    # Optional: editora, editorb, editorc, translator, annotator, commentator,
    # introduction, foreword, afterword, subtitle, titleaddon, maintitle,
    # mainsubtitle, maintitleaddon, language, origlanguage, volume, part,
    # edition, volumes, series, number, note, publisher, location, isbn, eid,
    # chapter, pages, pagetotal, addendum, pubstate, doi, eprint, eprintclass,
    # eprinttype, url, urldate

    # MVCOLLECTION = "mvcollection"
    # A multi"=volume \\bibtype{collection}. For backwards compatibility,
    # multi"=volume collections are also supported by the entry type
    # \\bibtype{collection}. However, it is advisable to make use of the
    # dedicated entry type \\bibtype{mvcollection}.
    # Required: editor, title, year/date
    # Optional: editora, editorb, editorc, translator, annotator, commentator,
    # introduction, foreword, afterword, subtitle, titleaddon, language,
    # origlanguage, edition, volumes, series, number, note, publisher,
    # location, isbn, pagetotal, addendum, pubstate, doi, eprint, eprintclass,
    # eprinttype, url, urldate

    # INCOLLECTION = "incollection"
    # A contribution to a collection which forms a self"=contained unit with
    # a
    # distinct author and title. The \\bibfield{author} refers to the
    # \\bibfield{title}, the \\bibfield{editor} to the \\bibfield{booktitle},
    # \\ie the title of the collection.
    # Required: author, title, editor, booktitle, year/date
    # Optional: editor, editora, editorb, editorc, translator, annotator,
    # commentator, introduction, foreword, afterword, subtitle, titleaddon,
    # maintitle, mainsubtitle, maintitleaddon, booksubtitle, booktitleaddon,
    # language, origlanguage, volume, part, edition, volumes, series, number,
    # note, publisher, location, isbn, eid, chapter, pages, addendum, pubstate,
    # doi, eprint, eprintclass, eprinttype, url, urldate

    # SUPPCOLLECTION = "suppcollection"
    # Supplemental material in a \\bibtype{collection}. This type is similar
    # to
    # \\bibtype{suppbook} but related to the \\bibtype{collection} entry type.
    # The standard styles will treat this entry type as an alias for
    # \\bibtype{incollection}.

    # DATASET = "dataset"
    # A data set or a similar collection of (mostly) raw data.
    # Required: author/editor, title, year/date
    # Optional: subtitle, titleaddon, language, edition, type, series, number,
    # version, note, organization, publisher, location, addendum, pubstate,
    # doi, eprint, eprintclass, eprinttype, url, urldate

    # MANUAL = "manual"
    # Technical or other documentation, not necessarily in printed form. The
    # \\bibfield{author} or \\bibfield{editor} is omissible in terms of
    # \\secref{bib:use:key}.
    # Required: author/editor, title, year/date
    # Optional: subtitle, titleaddon, language, edition, type, series, number,
    # version, note, organization, publisher, location, isbn, eid, chapter,
    # pages, pagetotal, addendum, pubstate, doi, eprint, eprintclass,
    # eprinttype, url, urldate

    MISC = "misc"
    # A fallback type for entries which do not fit into any other category.
    # Use
    # the field \\bibfield{howpublished} to supply publishing information in
    # free format, if applicable. The field \\bibfield{type} may be useful as
    # well. \\bibfield{author}, \\bibfield{editor}, and \\bibfield{year} are
    # omissible in terms of \\secref{bib:use:key}.
    # Required: author/editor, title, year/date
    # Optional: subtitle, titleaddon, language, howpublished, type, version,
    # note, organization, location, month, addendum, pubstate, doi, eprint,
    # eprintclass, eprinttype, url, urldate

    ONLINE = "online"
    # An online resource. \\bibfield{author}, \\bibfield{editor}, and
    # \\bibfield{year} are omissible in terms of \\secref{bib:use:key}. This
    # entry type is intended for sources such as web sites which are
    # intrinsically online resources. Note that all entry types support the
    # \\bibfield{url} field. For example, when adding an article from an online
    # journal, it may be preferable to use the \\bibtype{article} type and its
    # \\bibfield{url} field.
    # Required: author/editor, title, year/date, doi/eprint/url
    # Optional: subtitle, titleaddon, language, version, note, organization,
    # month, addendum, pubstate, eprintclass, eprinttype, urldate

    # PATENT = "patent"
    # A patent or patent request. The number or record token is given in the
    # \\bibfield{number} field. Use the \\bibfield{type} field to specify the
    # type and the \\bibfield{location} field to indicate the scope of the
    # patent, if different from the scope implied by the \\bibfield{type}. Note
    # that the \\bibfield{location} field is treated as a key list with this
    # entry type, see \\secref{bib:fld:typ} for details.
    # Required: author, title, number, year/date
    # Optional: holder, subtitle, titleaddon, type, version, location, note,
    # month, addendum, pubstate, doi, eprint, eprintclass, eprinttype, url,
    # urldate

    # PERIODICAL = "periodical"
    # An complete issue of a periodical, such as a special issue of a journal.
    # The title of the periodical is given in the \\bibfield{title} field. If
    # the issue has its own title in addition to the main title of the
    # periodical, it goes in the \\bibfield{issuetitle} field. The
    # \\bibfield{editor} is omissible in terms of \\secref{bib:use:key}.
    # Required: editor, title, year/date
    # Optional: editora, editorb, editorc, subtitle, titleaddon, issuetitle,
    # issuesubtitle,  issuetitleaddon, language, series, volume, number, issue,
    # month, note, issn, addendum, pubstate, doi, eprint, eprintclass,
    # eprinttype, url, urldate

    # SUPPPERIODICAL = "suppperiodical"
    # Supplemental material in a \\bibtype{periodical}. This type is similar
    # to
    # \\bibtype{suppbook} but related to the \\bibtype{periodical} entry type.
    # The role of this entry type may be more obvious if you bear in mind that
    # the \\bibtype{article} type could also be called \\bibtype{inperiodical}.
    # This type may be useful when referring to items such as regular columns,
    # obituaries, letters to the editor, etc. which only have a generic title.
    # Style guides may require such items to be formatted differently from
    # articles in the strict sense of the word. The standard styles will treat
    # this entry type as an alias for \\bibtype{article}.

    # PROCEEDINGS = "proceedings"
    # A single"=volume conference proceedings. This type is very similar to
    # \\bibtype{collection}. It supports an optional \\bibfield{organization}
    # field which holds the sponsoring institution. The \\bibfield{editor} is
    # omissible in terms of \\secref{bib:use:key}.
    # Required: title, year/date
    # Optional: editor, subtitle, titleaddon, maintitle, mainsubtitle,
    # maintitleaddon, eventtitle, eventtitleaddon, eventdate, venue, language,
    # volume, part, volumes, series, number, note, organization, publisher,
    # location, month, isbn, eid, chapter, pages, pagetotal, addendum,
    # pubstate, doi, eprint, eprintclass, eprinttype, url, urldate

    # MVPROCEEDINGS = "mvproceedings"
    # A multi"=volume \\bibtype{proceedings} entry. For backwards
    # compatibility, multi"=volume proceedings are also supported by the entry
    # type \\bibtype{proceedings}. However, it is advisable to make use of the
    # dedicated entry type \\bibtype{mvproceedings}
    # Required: title, year/date
    # Optional: editor, subtitle, titleaddon, eventtitle, eventtitleaddon,
    # eventdate, venue, language, volumes, series, number, note, organization,
    # publisher, location, month, isbn, pagetotal, addendum, pubstate,
    # doi, eprint, eprintclass, eprinttype, url, urldate

    INPROCEEDINGS = "inproceedings"
    # An article in a conference proceedings. This type is similar to
    # \\bibtype{incollection}. It supports an optional \\bibfield{organization}
    # field.
    # Required: author, title, booktitle, year/date
    # Optional: editor, subtitle, titleaddon, maintitle, mainsubtitle,
    # maintitleaddon, booksubtitle, booktitleaddon, eventtitle,
    # eventtitleaddon, eventdate, venue, language, volume, part, volumes,
    # series, number, note, organization, publisher, location, month, isbn,
    # eid, chapter, pages, addendum, pubstate, doi, eprint, eprintclass,
    # eprinttype, url, urldate

    # REFERENCE = "reference"
    # A single"=volume work of reference such as an encyclopedia or a
    # dictionary. This is a more specific variant of the generic
    # \\bibtype{collection} entry type. The standard styles will treat this
    # entry type as an alias for \\bibtype{collection}.

    # MVREFERENCE = "mvreference"
    # A multi"=volume \\bibtype{reference} entry. The standard styles will
    # treat this entry type as an alias for \\bibtype{mvcollection}. For
    # backwards compatibility, multi"=volume references are also supported by
    # the entry type \\bibtype{reference}. However, it is advisable to make use
    # of the dedicated entry type \\bibtype{mvreference}.

    # INREFERENCE = "inreference"
    # An article in a work of reference. This is a more specific variant of
    # the
    # generic \\bibtype{incollection} entry type. The standard styles will
    # treat this entry type as an alias for \\bibtype{incollection}.

    # REPORT = "report"
    # A technical report, research report, or white paper published by a
    # university or some other institution. Use the \\bibfield{type} field to
    # specify the type of report. The sponsoring institution goes in the
    # \\bibfield{institution} field.
    # Required: author, title, type, institution, year/date
    # Optional: subtitle, titleaddon, language, number, version, note,
    # location, month, isrn, eid, chapter, pages, pagetotal, addendum,
    # pubstate, doi, eprint, eprintclass, eprinttype, url, urldate

    # SET = "set"
    # An entry set. This entry type is special, see \\secref{use:use:set} for
    # details.

    # SOFTWARE = "software"
    # Computer software. The standard styles will treat this entry type as an
    # alias for \\bibtype{misc}.

    # THESIS = "thesis"
    # A thesis written for an educational institution to satisfy the
    # requirements for a degree. Use the \\bibfield{type} field to specify the
    # type of thesis.
    # Required: author, title, type, institution, year/date
    # Optional: subtitle, titleaddon, language, note, location, month, isbn,
    # eid, chapter, pages, pagetotal, addendum, pubstate, doi, eprint,
    # eprintclass, eprinttype, url, urldate

    # UNPUBLISHED = "unpublished"
    # A work with an author and a title which has not been formally published,
    # such as a manuscript or the script of a talk. Use the fields
    # \\bibfield{howpublished} and \\bibfield{note} to supply additional
    # information in free format, if applicable.
    # Required: author, title, year/date
    # Optional: subtitle, titleaddon, type, eventtitle, eventtitleaddon,
    # eventdate, venue, language, howpublished, note, location, isbn, month,
    # addendum, pubstate, doi, eprint, eprintclass, eprinttype, url, urldate

    # XDATA = "xdata"
    # This entry type is special. \\bibtype{xdata} entries hold data which may
    # be inherited by other entries using the \\bibfield{xdata} field. Entries
    # of this type only serve as data containers; they may not be cited or
    # added to the bibliography. See \\secref{use:use:xdat} for details.

    # custom[a--f]
    # Custom types for special bibliography styles. The standard styles defined
    # no bibliography drivers for these types and will fall back to using the
    # driver for \\bibtype{misc}.

    ################
    # Type Aliases #
    ################
    # The entry types listed in this section are provided for backwards
    # compatibility with traditional \\bibtex styles. These aliases are
    # resolved by the backend as the data is processed. \\biblatex and the
    # styles will see only the entry type the alias points to (the target), not
    # the alias name (the source). In particular \\biblatex-side per-type
    # operations like type-specific formatting and filtering only work for the
    # target type, not the source type. This <hard alias> is unlike the <soft
    # alias> relation in the previous subsection. The relevant mappings for the
    # \\opt{bibtex} driver can be found in~\\secref{apx:maps:bibtex}.

    # CONFERENCE = "conference"
    # A legacy alias for \\bibtype{inproceedings}.

    # ELECTRONIC = "electronic"
    # An alias for \\bibtype{online}.

    # MASTERSTHESIS = "mastersthesis"
    # Similar to \\bibtype{thesis} except that the \\bibfield{type} field is
    # optional and defaults to the localised term <Master's thesis>. You may
    # still use the \\bibfield{type} field to override that.

    # PHDTHESIS = "phdthesis"
    # Similar to \\bibtype{thesis} except that the \\bibfield{type} field is
    # optional and defaults to the localised term <PhD thesis>. You may still
    # use the \\bibfield{type} field to override that.

    # TECHREPORT = "techreport"
    # Similar to \\bibtype{report} except that the \\bibfield{type} field is
    # optional and defaults to the localised term <technical report>. You may
    # still use the \\bibfield{type} field to override that.

    # WWW = "www"
    # An alias for \\bibtype{online}, provided for \\sty{jurabib}
    # compatibility.

    ######################
    # Non-standard Types #
    ######################
    # The types in this section are similar to the custom types
    # \\bibtype{custom[a--f]}, \\ie the standard bibliography styles provide no
    # bibliography drivers for these types. In the standard styles they will
    # use the bibliography driver for \\bibtype{misc} entries---exceptions to
    # this rule are noted in the descriptions below. The types are known to the
    # default data model and will be happily accepted by \\biber.

    # ARTWORK = "artwork"
    # Works of the visual arts such as paintings, sculpture, and installations.

    # AUDIO = "audio"
    # Audio recordings, typically on audio \\acr{CD}, \\acr{DVD}, audio
    # cassette, or similar media. See also \\bibtype{music}.

    # BIBNOTE = "bibnote"
    # This special entry type is not meant to be used in the \\file{bib} file
    # like other types. It is provided for third-party packages like
    # \\sty{notes2bib} which merge notes into the bibliography. The notes
    # should go into the \\bibfield{note} field. Be advised that the
    # \\bibtype{bibnote} type is not related to the \\cmd{defbibnote} command
    # in any way. \\cmd{defbibnote} is for adding comments at the beginning or
    # the end of the bibliography, whereas the \\bibtype{bibnote} type is meant
    # for packages which render endnotes as bibliography entries.

    # COMMENTARY = "commentary"
    # Commentaries which have a status different from regular books, such as
    # legal commentaries.

    # IMAGE = "image"
    # Images, pictures, photographs, and similar media.

    # JURISDICTION = "jurisdiction"
    # Court decisions, court recordings, and similar things.

    # LEGISLATION = "legislation"
    # Laws, bills, legislative proposals, and similar things.

    # LEGAL = "legal"
    # Legal documents such as treaties.

    # LETTER = "letter"
    # Personal correspondence such as letters, emails, memoranda, etc.

    # MOVIE = "movie"
    # Motion pictures. See also \\bibtype{video}.

    # MUSIC = "music"
    # Musical recordings. This is a more specific variant of \\bibtype{audio}.

    # PERFORMANCE = "performance"
    # Musical and theatrical performances as well as other works of the
    # performing arts. This type refers to the event as opposed to a recording,
    # a score, or a printed play.

    # REVIEW = "review"
    # Reviews of some other work. This is a more specific variant of the
    # \\bibtype{article} type. The standard styles will treat this entry type
    # as an alias for \\bibtype{article}.

    # STANDARD = "standard"
    # National and international standards issued by a standards body such as
    # the International Organization for Standardization.

    # VIDEO = "video"
    # Audiovisual recordings, typically on \\acr{DVD}, \\acr{VHS} cassette,
    # or
    # similar media. See also \\bibtype{movie}.
