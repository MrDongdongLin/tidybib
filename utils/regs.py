from .parse import parses


# we define some regex below
# item patterns

class BuildRegex():

    def __init__(self):
        a = parses()

        self.comments = r"(%.*)"
        self.abbr = r"(@string{[\s\S]*?})(?=[ \\\n]*[@%])"
        self.inproceedings = r"(@inproceedings{[\s\S]*?})(?=[ \\\n]*[@%])"
        self.proceedings = r"(@proceedings{[\s\S]*?})(?=[ \\\n]*[@%])"
        self.misc = r"(@misc{[\s\S]*?})(?=[ \\\n]*[@%])"
        self.article = r"(@article{[\s\S]*?})(?=[ \\\n]*[@%])"
        self.book = r"(@book{[\s\S]*?})(?=[ \\\n]*[@%])"
        self.incollection = r"(@incollection{[\s\S]*?})(?=[ \\\n]*[@%])"
        # head of each item
        if a.tidyid == "yes":
            self.head_inproceedings = r"(@inproceedings{)"
            self.head_proceedings = r"(@proceedings{)"
            self.head_misc = r"(@misc{)"
            self.head_article = r"(@article{)"
            self.head_book = r"(@book{)"
            self.head_incollection = r"(@incollection{)"
        else:
            self.head_inproceedings = r"(@inproceedings{[\s\S]*?,)(?=[ \\\n]*)"
            self.head_proceedings = r"(@proceedings{[\s\S]*?,)(?=[ \\\n]*)"
            self.head_misc = r"(@misc{[\s\S]*?,)(?=[ \\\n]*)"
            self.head_article = r"(@article{[\s\S]*?,)(?=[ \\\n]*)"
            self.head_book = r"(@book{[\s\S]*?,)(?=[ \\\n]*)"
            self.head_incollection = r"(@incollection{[\s\S]*?,)(?=[ \\\n]*)"
        # can be used
        # head_inproceedings = r"(@inproceedings{[\s\S]*?,)(?=[ \\\n]*)"
        # head_proceedings = r"(@proceedings{[\s\S]*?,)(?=[ \\\n]*)"
        # head_misc = r"(@misc{[\s\S]*?,)(?=[ \\\n]*)"
        # head_article = r"(@article{[\s\S]*?,)(?=[ \\\n]*)"
        # head_book = r"(@book{[\s\S]*?,)(?=[ \\\n]*)"
        # head_incollection = r"(@incollection{[\s\S]*?,)(?=[ \\\n]*)"

        # field patterns
        self.author = r"(?<!\w)(author)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.title = r"(?<!\w)(title)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.journal = r"(?<!\w)(journal)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.year = r"(?<!\w)(year)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.volume = r"(?<!\w)(volume)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.number = r"(?<!\w)(number)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.pages = r"(?<!\w)(pages)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.month = r"(?<!\w)(month)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.doi = r"(?<!\w)(doi)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.editor = r"(?<!\w)(editor)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.publisher = r"(?<!\w)(publisher)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.series = r"(?<!\w)(series)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.organization = r"(?<!\w)(organization)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.address = r"(?<!\w)(address)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.edition = r"(?<!\w)(edition)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.address = r"(?<!\w)(address)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.booktitle = r"(?<!\w)(booktitle)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        self.howpublished = r"(?<!\w)(howpublished)(?=[= ])([\s\S]*?)([}\"],).*(?=( |\n))"
        # other match
        self.outer_brace = r"(?<=[{\"])([\s\S]*)(?=[}\"])"
        self.inner_brace = r"(?<=[{\"])[^{]([^{}]+)[^}](?=[}\"])"
        self.head_author = r"(?<={)([a-zA-Z]*)(?=\W)"
        self.inner_year = r"(?<={)(\d*)(?=})"
        # upper cases, add more defines in the future
        self.uppercases = ['IEEE', 'IETE']
        self.lowercases = ['on', 'for', 'of', 'and', 'in']  # for journal field

        # define a regex dictionary contains the field need to be written out
        self.inproceedings_regex = {
            "item": self.inproceedings,
            "head": self.head_inproceedings,

            # NOTE: the following keys must arrange in a certain order, DONOT change it!
            "author": self.author,
            "title": self.title,
            "booktitle": self.booktitle,
            "year": self.year,
            "editor": self.editor,
            "volume": self.volume,
            "number": self.number,
            "series": self.series,
            "pages": self.pages,
            "publisher": self.publisher,
            "doi": self.doi
        }

        self.proceedings_regex = {
            "item": self.proceedings,
            "head": self.head_proceedings,

            # NOTE: the following keys must arrange in a certain order, DONOT change it!
            "title": self.title,
            "year": self.year,
            "editor": self.editor,
            "publisher": self.publisher,
            "volume": self.volume,
            "number": self.number,
            "series": self.series,
            "organization": self.organization,
            "address": self.address,
            "month": self.month
        }

        self.misc_regex = {
            "item": self.misc,
            "head": self.head_misc,

            # NOTE: the following keys must arrange in a certain order, DONOT change it!
            "author": self.author,
            "title": self.title,
            "howpublished": self.howpublished,
            "year": self.year,
            "month": self.month
        }

        self.book_regex = {
            "item": self.book,
            "head": self.head_book,

            # NOTE: the following keys must arrange in a certain order, DONOT change it!
            "author": self.author,
            "title": self.title,
            "year": self.year,
            "edition": self.edition,
            "publisher": self.publisher,
            "address": self.address
        }

        self.article_regex = {
            "item": self.article,
            "head": self.head_article,

            # NOTE: the following keys must arrange in a certain order, DONOT change it!
            "author": self.author,
            "title": self.title,
            "journal": self.journal,
            "year": self.year,
            "volume": self.volume,
            "number": self.number,
            "pages": self.pages,
            "doi": self.doi
        }

        self.incollection_regex = {
            "item": self.incollection,
            "head": self.head_incollection,

            # NOTE: the following keys must arrange in a certain order, DONOT change it!
            "author": self.author,
            "title": self.title,
            "booktitle": self.booktitle,
            "pages": self.pages,
            "year": self.year
        }