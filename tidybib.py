# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="input bib file")
parser.add_argument("-o", "--output", default="tidy.bib", help="number of workers")
a = parser.parse_args()

# function field_content returns strings after '=', i.e. the content in '{...}'
def field_content(reg_field, reg_content, object_str):
    match_field = re.finditer(reg_field, object_str, re.MULTILINE | re.IGNORECASE)
    try:
        next_match = next(match_field).group()
        match_content = re.finditer(reg_content, next_match, re.MULTILINE | re.IGNORECASE)
        next_content = next(match_content).group()
        content = re.sub("\n+", "", next_content)
        content = re.sub(" +", " ", content)
        content = "{"+content+"}"
    except StopIteration:
        content = "{}"

    return content

def tidy_item(regex, object_str, fout):
    # output_str = [] # TODO: we can buffer the tidy item and write them out afterwards
    matches = re.finditer(regex["item"], object_str, re.MULTILINE | re.IGNORECASE)

    counter = 0
    while True:
        try:
            match = next(matches)
            item = match.group()

            for key, value in regex.items():
                if key == "item" or key == "content":
                    continue
                else:
                    if key == "head":
                        content = re.finditer(value, item, re.MULTILINE | re.IGNORECASE)
                        head_content = next(content).group()
                        fout.write(head_content + "\n")
                    else:
                        content = field_content(value, regex["content"], item)
                        fout.write("  {:<15} = {},\n".format(key, content))
            fout.write("}\n\n")
            counter += 1
        except StopIteration:
            break
    return counter


# we define some regex below
# item patterns
comments = r"(%.*)"
abbr = r"(@string{[\s\S]*?})(?=[ \\\n]*[@%])"
inproceedings = r"(@inproceedings{[\s\S]*?})(?=[ \\\n]*[@%])"
proceedings = r"(@proceedings{[\s\S]*?})(?=[ \\\n]*[@%])"
misc = r"(@misc{[\s\S]*?})(?=[ \\\n]*[@%])"
article = r"(@article{[\s\S]*?})(?=[ \\\n]*[@%])"
book = r"(@book{[\s\S]*?})(?=[ \\\n]*[@%])"
# field patterns
author = r"(?<!\w)(author[\s\S]*?[}\"],)"
title = r"(?<!\w)(title[\s\S]*?[}\"],)"
journal = r"(?<!\w)(journal[\s\S]*?[}\"],)"
year = r"(?<!\w)(year[\s\S]*?[}\"],)"
volume = r"(?<!\w)(volume[\s\S]*?[}\"],)"
number = r"(?<!\w)(number[\s\S]*?[}\"],)"
pages = r"(?<!\w)(pages[\s\S]*?[}\"],)"
month = r"(?<!\w)(month[\s\S]*?[}\"],)"
doi = r"(?<!\w)(doi[\s\S]*?[}\"],)"
editor = r"(?<!\w)(editor[\s\S]*?[}\"],)"
publisher = r"(?<!\w)(publisher[\s\S]*?[}\"],)"
series = r"(?<!\w)(series[\s\S]*?[}\"],)"
organization = r"(?<!\w)(organization[\s\S]*?[}\"],)"
address = r"(?<!\w)(address[\s\S]*?[}\"],)"
edition = r"(?<!\w)(edition[\s\S]*?[}\"],)"
address = r"(?<!\w)(address[\s\S]*?[}\"],)"
booktitle = r"(?<!\w)(booktitle[\s\S]*?[}\"],)"
howpublished = r"(?<!\w)(howpublished[\s\S]*?[}\"],)"
# extra match
content = r"(?<=[{\"])([\s\S]*)(?=[}\"])"
# head of each item
head_inproceedings = r"(@inproceedings{[\s\S]*?,)(?=[ \\\n]*)"
head_proceedings = r"(@proceedings{[\s\S]*?,)(?=[ \\\n]*)"
head_misc = r"(@misc{[\s\S]*?,)(?=[ \\\n]*)"
head_article = r"(@article{[\s\S]*?,)(?=[ \\\n]*)"
head_book = r"(@book{[\s\S]*?,)(?=[ \\\n]*)"

# open a bib file and read all the items in one time
fin = open(a.input, 'r', encoding='UTF-8')
bibin = fin.read() # TODO: buffering all the items as a list in one time, if bib file is large, it will consume much time
fin.close()

# add end mark to bib file to ensure the last item can be matched
if bibin[-1] != "%":
    try:
        bibin = bibin + "%"
    except:
        print("format ERROR: cannot add end mark! Please add "%" in the end of the bib file manually!")

# matched items
comments_matches = re.finditer(comments, bibin, re.MULTILINE | re.IGNORECASE)
abbr_matches = re.finditer(abbr, bibin, re.MULTILINE | re.IGNORECASE)
# inproceedings_matches = re.finditer(inproceedings, bibin, re.MULTILINE | re.IGNORECASE)
# proceedings_matches = re.finditer(proceedings, bibin, re.MULTILINE | re.IGNORECASE)
# misc_matches = re.finditer(misc, bibin, re.MULTILINE | re.IGNORECASE)
# article_matches = re.finditer(article, bibin, re.MULTILINE | re.IGNORECASE)
# book_matches = re.finditer(book, bibin, re.MULTILINE | re.IGNORECASE)

# write tidy bib file
fout = open(a.output, 'w', encoding='UTF-8')

print("begin to process " + a.input + ". Please wait...")

# comments
for matchNum, match in enumerate(comments_matches, start=1):
    item = match.group()
    fout.write(item + "\n")
fout.write("\n")

# abbr
for matchNum, match in enumerate(abbr_matches, start=1):
    item = match.group()
    abbr = re.sub("\n+", "", item)
    abbr = re.sub(" +", " ", abbr)
    fout.write(abbr + "\n")
fout.write("\n")

# define a regex dictionary contains the field need to be writtern out
inproceedings_regex = {
    "item": inproceedings,
    "head": head_inproceedings,
    "content": content,

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "author": author,
    "title": title,
    "booktitle": booktitle,
    "year": year,
    "editor": editor,
    "volume": volume,
    "number": number,
    "series": series,
    "pages": pages,
    "publisher": publisher
}

proceedings_regex = {
    "item": proceedings,
    "head": head_proceedings,
    "content": content,

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "title": title,
    "year": year,
    "editor": editor,
    "publisher": publisher,
    "volume": volume,
    "number": number,
    "series": series,
    "organization": organization,
    "address": address,
    "month": month
}

misc_regex = {
    "item": misc,
    "head": head_misc,
    "content": content,

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "author": author,
    "title": title,
    "howpublished": howpublished,
    "year": year,
    "month": month
}

book_regex = {
    "item": book,
    "head": head_book,
    "content": content,

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "author": author,
    "title": title,
    "year": year,
    "edition": edition,
    "publisher": publisher,
    "address": address
}

article_regex = {
    "item": article,
    "head": head_article,
    "content": content,

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "author": author,
    "title": title,
    "journal": journal,
    "year": year,
    "volume": volume,
    "number": number,
    "pages": pages,
    "month": month,
    "doi": doi
}

# set a counter for processed items
count = 0

numInproceed = tidy_item(inproceedings_regex, bibin, fout)
numProceed = tidy_item(proceedings_regex, bibin, fout)
numMisc = tidy_item(misc_regex, bibin, fout)
numBook = tidy_item(book_regex, bibin, fout)
numArticle = tidy_item(article_regex, bibin, fout)

count = numInproceed + numProceed + numMisc + numBook + numArticle

print(str(count) + " items are processed successfully!")
print(str(numInproceed) + " inproceedings")
print(str(numProceed) + " proceedings")
print(str(numMisc) + " misc")
print(str(numBook) + " book")
print(str(numArticle) + " article")

fout.close()