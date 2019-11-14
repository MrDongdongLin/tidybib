# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
import os
import glob
import argparse

# we define some regex below
# item patterns
comments = r"(%.*)"
abbr = r"(@string{[\s\S]*?})(?=[ \\\n]*[@%])"
inproceedings = r"(@inproceedings{[\s\S]*?})(?=[ \\\n]*[@%])"
proceedings = r"(@proceedings{[\s\S]*?})(?=[ \\\n]*[@%])"
misc = r"(@misc{[\s\S]*?})(?=[ \\\n]*[@%])"
article = r"(@article{[\s\S]*?})(?=[ \\\n]*[@%])"
book = r"(@book{[\s\S]*?})(?=[ \\\n]*[@%])"
incollection = r"(@incollection{[\s\S]*?})(?=[ \\\n]*[@%])"
# head of each item
head_inproceedings = r"(@inproceedings{[\s\S]*?,)(?=[ \\\n]*)"
head_proceedings = r"(@proceedings{[\s\S]*?,)(?=[ \\\n]*)"
head_misc = r"(@misc{[\s\S]*?,)(?=[ \\\n]*)"
head_article = r"(@article{[\s\S]*?,)(?=[ \\\n]*)"
head_book = r"(@book{[\s\S]*?,)(?=[ \\\n]*)"
head_incollection = r"(@incollection{[\s\S]*?,)(?=[ \\\n]*)"
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
# other match
outer_brace = r"(?<=[{\"])([\s\S]*)(?=[}\"])"
inner_brace = r"(?<=[{\"])[^{]([^{}]+)[^}](?=[}\"])"

# define a regex dictionary contains the field need to be writtern out
inproceedings_regex = {
    "item": inproceedings,
    "head": head_inproceedings,

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
    "publisher": publisher,
    "doi": doi
}

proceedings_regex = {
    "item": proceedings,
    "head": head_proceedings,

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

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "author": author,
    "title": title,
    "journal": journal,
    "year": year,
    "volume": volume,
    "number": number,
    "pages": pages,
    "doi": doi
}

incollection_regex = {
    "item": incollection,
    "head": head_incollection,

    # NOTE: the following keys must arrange in a certain order, please DONOT change it!
    "author": author,
    "title": title,
    "booktitle": booktitle,
    "pages": pages,
    "year": year
}

def tidy_title(inner_brace, object_str):
    object_str = object_str.capitalize()

    matches = re.finditer(inner_brace, object_str, re.MULTILINE | re.IGNORECASE)
    for matchNum, match in enumerate(matches, start=1):
        object_str = object_str.replace(match.group(), match.group().upper()) # all the words in inner brace are upper case
    
    return object_str

# function field_content returns strings after '=', i.e. the content in '{...}'
def field_content(field, reg_field, reg_content, object_str):
    match_field = re.finditer(reg_field, object_str, re.MULTILINE | re.IGNORECASE)
    try:
        next_match = next(match_field).group()
        match_content = re.finditer(reg_content, next_match, re.MULTILINE | re.IGNORECASE)
        next_content = next(match_content).group()
        # remove extra blanks and enters
        content = re.sub("\n+", "", next_content)
        content = re.sub(" +", " ", content)
        # TODO: 套娃问题！
        # if field == "title":
        #     content = tidy_title(inner_brace, content)
        if len(content) != 0:
            if content[0] == "{" and content[-1] == "}":
                content = content
            else:
                content = "{"+content+"}"
        else:
            content = "{}"
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
                if key == "item":
                    continue
                elif key == "head":
                    content = re.finditer(value, item, re.MULTILINE | re.IGNORECASE)
                    head_content = next(content).group()
                    fout.write(head_content + "\n")
                else:
                    content = field_content(key, value, outer_brace, item)
                    fout.write("  {:<14} {},\n".format(key+" =", content))
            fout.write("}\n\n")
            counter += 1
        except StopIteration:
            break
    return counter

# parameters
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="input bib file, default input all the bib files in the root path")
parser.add_argument("-o", "--output", default="tidy.bib", help="output bib file, default output is 'tidy.bib'")
a = parser.parse_args()

print("=================================== Tidy your bib file ===================================")
print("* Please create two folders, named `bibfile` and `tidybib` in the root path of this program.")
print("* Put your bib file into folder `bibfile`, execute")
print("")
print("\tpython tidybib.py")
print("")
print("* with command line, then you can find the corresponding tidy bib file in folder `tidybib`,")
print("* which named `tidy_xxx.bib`.")
print("* You can also generate tidy bib file by using command")
print("")
print("\tpython tidybib.py -i yourfile.bib -o tidyfile.bib")
print("")
print("* Try `python tidybib.py -h` for more information.")
print("======================================== end =============================================")

# batch process
if a.input is None:
    print("Searching bib files in `bibfile`...")
    bib_files = glob.glob("bibfile/*.bib")
    if len(bib_files) <= 0:
        raise Exception("No bib file in the folder `bibfile`!")
    else:
        inpath = bib_files
else:
    inpath = a.input

for i in range(len(inpath)):
    # open a bib file and read all the items in one time
    fin = open(inpath[i], 'r', encoding='UTF-8')
    bibin = fin.read() # TODO: buffering all the items as a list in one time, if bib file is large, it will consume much time
    fin.close()

    # add end mark to bib file to ensure the last item can be matched
    if bibin[-1] != "%":
        try:
            bibin = bibin + "%"
        except:
            print("Format ERROR: cannot add end mark! Please add "%" in the end of the bib file manually!")

    # matched items
    comments_matches = re.finditer(comments, bibin, re.MULTILINE | re.IGNORECASE)
    abbr_matches = re.finditer(abbr, bibin, re.MULTILINE | re.IGNORECASE)

    # write tidy bib file
    _, out_name = os.path.split(inpath[i])
    fout = open("tidybib/tidy_" + out_name, 'w', encoding='UTF-8')

    print("\nBegin to process " + inpath[i] + ". Please wait...")

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

    # set a counter for processed items
    count = 0

    numInproceed = tidy_item(inproceedings_regex, bibin, fout)
    numProceed = tidy_item(proceedings_regex, bibin, fout)
    numMisc = tidy_item(misc_regex, bibin, fout)
    numBook = tidy_item(book_regex, bibin, fout)
    numArticle = tidy_item(article_regex, bibin, fout)
    numIncollection = tidy_item(incollection_regex, bibin, fout)

    count = numInproceed + numProceed + numMisc + numBook + numArticle + numIncollection

    print(str(count) + " items are processed successfully!")
    print(str(numInproceed) + " inproceedings")
    print(str(numProceed) + " proceedings")
    print(str(numMisc) + " misc")
    print(str(numBook) + " book")
    print(str(numArticle) + " article")
    print(str(numIncollection) + " incollection")
    print("Done!")

    fout.close()