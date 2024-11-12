# Entry field types as defined in biblatex documentation:
# https://raw.githubusercontent.com/plk/biblatex/dev/doc/latex/biblatex/biblatex.tex
# Before defining a custom entry field type check if an existing one would be
# relevant.

# Data Types
# In datasources such as a \\file{bib} file, all bibliographic data is
# specified in fields. Some of those fields, for example \\bibfield{author} and
# \\bibfield{editor}, may contain a list of items. This list structure is
# implemented by the \\bibtex file format via the keyword <|and|>, which is
# used to separate the individual items in the list. The \\biblatex package
# implements three distinct data types to handle bibliographic data: name
# lists, literal lists, and fields. There are also several list and field
# subtypes and a content type which can be used to semantically distinguish
# fields which are otherwise not distinguishable on the basis of only their
# datatype (see \\secref{aut:ctm:dm}). This section gives an overview of the
# data types supported by this package. See \\secref{bib:fld:dat, bib:fld:spc}
# for information about the mapping of the \\bibtex file format fields to
# \\biblatex's data types.


from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Hashable, List, Optional

################
# Custom Types #
################


class SeparatedLiterals(List[str]):
    def __str__(self) -> str:
        return ";".join(sorted(literal.strip() for literal in self))


@dataclass
class File:
    remote: str  # url of remote resource
    local: Path  # relative pass of local copy
    type: Optional[str] = None

    def __str__(self) -> str:
        if self.type is None:
            self.type = self.local.suffix[1:].upper()
        return f":{self.local}:{self.type.strip()}"


class FileList(List[File]):
    def __str__(self) -> str:
        return ";".join(sorted(str(file) for file in self))


##############
# Name lists #
##############
# Name lists are parsed and split up into the individual items at the
# \\texttt{and} delimiter. Each item in the list is then dissected into the
# name part components: by default the given name, the name prefix (von, van,
# of, da, de, della, \\dots), the family name, and the name suffix (junior,
# senior, \\dots). The valid name parts can be customised by changing the
# datamodel definition described in \\secref{aut:bbx:drv}. Name lists may be
# truncated in the \\file{bib} file with the keyword <\\texttt{and others}>.
# Typical examples of name lists are \\bibfield{author} and \\bibfield{editor}.

# Name list fields automatically have an \\cmd{ifuse*} test created as per the
# name lists in the default data model (see \\secref{aut:aux:tst}). They are
# also automatically have a \\opt{ifuse*} option created which controls
# labelling and sorting behaviour with the name (see
# \\secref{use:opt:bib:hyb}). \\biber supports a customisable set of name parts
# but currently this is defined to be the same set of parts as supported by
# traditional \\bibtex:

# - Family name (also known as <last> part)
# - Given name (also known as <first> part)
# - Name prefix (also known as <von> part)
# - Name suffix (also known as <Jr> part)

# The supported list of name parts is defined as a constant list in the default
# data model using the \\cmd{DeclareDatamodelConstant} command (see
# \\ref{aut:ctm:dm}). However, it is not enough to simply add to this list in
# order to add support for another name part as name parts typically have to be
# hard coded into bibliography drivers and the backend processing. See the
# example file \\file{93-nameparts.tex} for details on how to define and use
# custom name parts. Also see \\cmd{DeclareUniquenameTemplate} in
# \\secref{aut:cav:amb} for information on how to customise name disambiguation
# using custom name parts.


@dataclass
class Name:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id: Optional[Hashable] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    url: Optional[str] = None

    def __str__(self) -> str:
        # check for empty name parts
        if self.last_name in ["", ".", "&nbsp;"]:
            if self.full_name is None:
                self.full_name = self.first_name
            self.last_name = None
        if self.first_name in ["", ".", "&nbsp;"]:
            if self.full_name is None:
                self.full_name = self.last_name
            self.first_name = None

        # build str
        if self.last_name is not None and self.first_name is not None:
            output = f"{self.last_name.strip()}, {self.first_name.strip()}"
        elif self.full_name is not None:
            output = self.full_name.strip()
        else:
            output = "Anonymous"
        return output.replace(" and ", " {and} ")


class NameList(List[Name]):
    def __str__(self) -> str:
        return " and ".join(str(name) for name in self)


#################
# Literal lists #
#################
# Literal lists are parsed and split up into the individual items at the
# \\texttt{and} delimiter but not dissected further. Literal lists may be
# truncated in the \\file{bib} file with the keyword <\\texttt{and others}>.
# There are two subtypes:

# -----------------#
# - Literal lists -#
# -----------------#
# Literal lists in the strict sense are handled as described above. The
# individual items are simply printed as is. Typical examples of such literal
# lists are \\bibfield{publisher} and \\bibfield{location}.


class LiteralList(List[str]):
    def __str__(self) -> str:
        return " and ".join(literal.strip() for literal in self)


# -------------#
# - Key lists -#
# -------------#
# Key lists are a variant of literal lists which may hold printable data or
# localisation keys. For each item in the list, styles should perform a test to
# determine whether it is a known localisation key (the localisation keys
# defined by default are listed in \\secref{aut:lng:key}). If so, the localised
# string should be printed. If not, the item should be printed as is. The
# standard styles are set up to exhibit this behaviour for all key lists listed
# below. New key lists do not automatically perform this test, it has to be
# implemented explicitly via the list format. A typical example of a key list
# is \\bibfield{language}.

##########
# Fields #
##########
# Fields are usually printed as a whole. There are several subtypes:

# ------------------#
# - Literal fields -#
# ------------------#
# Literal fields are printed as is. Typical examples of literal fields are
# \\bibfield{title} and \\bibfield{note}.
LiteralField = str

# ----------------#
# - Range fields -#
# ----------------#
# Range fields consist of one or more ranges where all dashes are normalized
# and replaced by the command \\cmd{bibrangedash}. A range is something
# optionally followed by one or more dashes optionally followed by some
# non-dash (e.g. \\texttt{5--7}). Any number of consecutive dashes will only
# yield a single range dash. A typical example of a range field is the
# \\bibfield{pages} field. See also the \\cmd{bibrangessep} command which can
# be used to customise the separator between multiple ranges. Range fields will
# be skipped and will generate a warning if they do not consist of one or more
# ranges. You can normalise messy range fields before they are parsed using
# \\cmd{DeclareSourcemap} (see \\secref{aut:ctm:map}).

# ------------------#
# - Integer fields -#
# ------------------#
# Integer fields hold integers which may be converted to ordinals or strings as
# they are printed. A typical example is the \\bibfield{extradate} or
# \\bibfield{volume} field. Such fields are sorted as integers. \\biber makes a
# (quite serious) effort to map non-arabic representations (roman numerals for
# example) to integers for sorting purposes. See the \\opt{noroman} option
# which can be used to suppress roman numeral parsing. This can help in cases
# where there is an ambiguity between parsing as roman numerals or alphanumeric
# (e.g. <C>), see \\secref{use:opt:pre:int}.

# -------------------#
# - Datepart fields -#
# -------------------#
# Datepart fields hold unformatted integers which may be converted to ordinals
# or strings as they are printed. A typical example is the \\bibfield{month}
# field. For every field of datatype \\bibfield{date} in the datamodel,
# datepart fields are automatically created with the following names:
# \\bibfield{$<$datetype$>$year}, \\bibfield{$<$datetype$>$endyear},
# \\bibfield{$<$datetype$>$month}, \\bibfield{$<$datetype$>$endmonth},
# \\bibfield{$<$datetype$>$day}, \\bibfield{$<$datetype$>$endday},
# \\bibfield{$<$datetype$>$hour}, \\bibfield{$<$datetype$>$endhour},
# \\bibfield{$<$datetype$>$minute}, \\bibfield{$<$datetype$>$endminute},
# \\bibfield{$<$datetype$>$second}, \\bibfield{$<$datetype$>$endsecond},
# \\bibfield{$<$datetype$>$timezone}, \\bibfield{$<$datetype$>$endtimezone}.
# $<$datetype$>$ is the string preceding <date> for any datamodel field of
# \\kvopt{datatype}{date}. For example, in the default datamodel, <event>,
# <orig>, <url> and the empty string <> for the date field \\bibfield{date}.

# ---------------#
# - Date fields -#
# ---------------#
# Date fields hold a date specification in
# \\texttt{yyyy-mm-ddThh:nn[+|-][hh[:nn]|Z]} format or a date range in
# \\texttt{yyyy-mm-ddThh:nn[+|-][hh[:nn]|Z]/yyyy-mm-ddThh:nn[+|-][hh[:nn]|Z]}
# format and other formats permitted by \\acr{ISO8601-2} Clause 4, level 1, see
# \\secref{bib:use:dat}. Date fields are special in that the date is parsed and
# split up into its datepart type components. The \\bibfield{datepart}
# components (see above) are automatically defined and recognised when a field
# of datatype \\bibfield{date} is defined in the datamodel. A typical example
# is the \\bibfield{date} field.
DateField = date

# -------------------#
# - Verbatim fields -#
# -------------------#
# Verbatim fields are processed in verbatim mode and may contain special
# characters. Typical examples of verbatim fields are \\bibfield{file}
# and \\bibfield{doi}.
VerbatimField = str

# --------------#
# - URI fields -#
# --------------#
# URI fields are processed in verbatim mode and may contain special characters.
# They are also URL-escaped if they don't look like they already are. The
# typical example of a uri field is \\bibfield{url}.
UriField = str

# --------------------------#
# - Separated value fields -#
# --------------------------#
# A separated list of literal values. Examples are the \\bibfield{keywords} and
# \\bibfield{options} fields. The separator can be configured to be any Perl
# regular expression via the \\opt{xsvsep} option which defaults to the usual
# \\bibtex comma surrounded by optional whitespace.

# ------------------#
# - Pattern fields -#
# ------------------#
# A literal field which must match a particular pattern. An example is the
# \\bibfield{gender} field from \\secref{bib:fld:spc}.

# --------------#
# - Key fields -#
# --------------#
# Key fields May hold printable data or localisation keys. Styles should
# perform a test to determine whether the value of the field is a known
# localisation key (the localisation keys defined by default are listed in
# \\secref{aut:lng:key}). If so, the localised string should be printed. If
# not, the value should be printed as is. The standard styles are set up to
# handle all key fields listed below in that way. New key fields do not
# automatically perform the test, it has to be enabled explicitly in the field
# format. A typical example is the \\bibfield{type} field.

# ---------------#
# - Code fields -#
# ---------------#
# Code fields Holds \\tex code.
