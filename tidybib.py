# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
import os
import glob
import argparse
from utils.parse import parses
from utils.regs import BuildRegex

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
        if len(content) != 0:
            if content[0] == "{" and content[-1] == "}":
                content = content
                # content = content[:1] + content[1].upper() + content[2:]
            else:
                content = "{" + content + "}"
                # content = "{" + content[0].upper() + content[1:] + "}"
        else:
            content = "{}"
    except StopIteration:
        content = "{}"

    return content

def tidy_title(title):
    match_str = re.finditer(r"{[^{}]+}", title, re.MULTILINE)
    title = title.capitalize()
    try:
        next_match = next(match_str).group()
        title = re.sub("{[^{}]+}", next_match, title)
    except StopIteration:
        title = title
    return title

def tidy_item(regex, object_str, fout, regs):
    # output_str = [] # TODO: we can buffer the tidy item and write them out afterwards
    matches = re.finditer(regex["item"], object_str, re.MULTILINE | re.IGNORECASE)

    counter = 0
    while True:
        try:
            match = next(matches)
            item = match.group()
            id_head = ""

            # extract head from author, title and year, e.g. Lin:ISEA:2017
            for key, value in regex.items():
                if key == "author":
                    author_content = field_content(key, value, regs.outer_brace, item)
                    first_author = re.finditer(regs.head_author, author_content)
                    first_author_name = next(first_author).group()
                    id_head = id_head + first_author_name
                if key == "title":
                    contraction_title = ""
                    title_content = field_content(key, value, regs.outer_brace, item)
                    inner_title = re.finditer(regs.outer_brace, title_content)
                    innertitle = next(inner_title).group()
                    first_characters = [i[0] for i in innertitle.split()]
                    if len(first_characters) >= 5:
                        for i in range(5):
                            contraction_title = contraction_title + first_characters[i]
                    else:
                        for i in range(len(first_characters)):
                            contraction_title = contraction_title + first_characters[i]
                    id_head = id_head + ":" + contraction_title
                if key == "year":
                    year_content = field_content(key, value, regs.outer_brace, item)
                    first_year = re.finditer(regs.inner_year, year_content)
                    inneryear = next(first_year).group()
                    id_head = id_head + ":" + inneryear
            # write file
            for key, value in regex.items():
                if key == "item":
                    continue
                elif key == "head":
                    content = re.finditer(value, item, re.MULTILINE | re.IGNORECASE)
                    head_content = next(content).group()
                    if args.tidyid == "yes":
                        fout.write(head_content + id_head + ",\n")
                    else:
                        fout.write(head_content + "\n")
                else:
                    if key == "journal" or key == "booktitle":
                        journal_abbr = tidy_journal(key, value, item, regs)
                        fout.write("  {:<14} {},\n".format(key + " =", journal_abbr))
                    elif key == "title":
                        content = field_content(key, value, regs.outer_brace, item)
                        content = content[0] + content[1].upper() + content[2:]
                        content = content[1:-1]
                        content = "{" + tidy_title(content) + "}"
                        fout.write("  {:<14} {},\n".format(key + " =", content))
                    else:
                        content = field_content(key, value, regs.outer_brace, item)
                        fout.write("  {:<14} {},\n".format(key + " =", content))
            fout.write("}\n\n")
            counter += 1
        except StopIteration:
            break
    return counter


def tidy_journal(regex, str_journal, item, regs):
    journal_abbr = ""
    content = field_content(regex, str_journal, regs.outer_brace, item)
    inner_journal = re.finditer(regs.outer_brace, content)
    journal_name = next(inner_journal).group()
    journal_list = [i for i in journal_name.split()]
    for i, word in enumerate(journal_list):
        flag = True
        end = False
        if i == len(journal_list) - 1:
            end = True
        # TODO: simple process. not good!
        if word[0] == "(":
            if end:
                journal_abbr = journal_abbr + word.upper()
            else:
                journal_abbr = journal_abbr + word.upper() + " "
        else:
            for _, upper_word in enumerate(regs.uppercases):
                if word.upper() == upper_word:
                    if end:
                        journal_abbr = journal_abbr + upper_word
                    else:
                        journal_abbr = journal_abbr + upper_word + " "
                    flag = False
            for _, lower_word in enumerate(regs.lowercases):
                if word.lower() == lower_word:
                    if end:
                        journal_abbr = journal_abbr + lower_word
                    else:
                        journal_abbr = journal_abbr + lower_word + " "
                    flag = False
            if flag:
                if end:
                    journal_abbr = journal_abbr + word.capitalize()
                else:
                    journal_abbr = journal_abbr + word.capitalize() + " "
    journal_abbr = "{" + journal_abbr + "}"

    return journal_abbr


def main(args, regs):
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
    print("\tpython tidybib.py -i yourfile.bib")
    print("")
    print("* Try `python tidybib.py -h` for more information.")
    print("======================================== end =============================================")

    # batch process
    if args.input is None:
        print("Searching bib files in `bibfile`...")
        bib_files = glob.glob("bibfile/*.bib")
        if len(bib_files) <= 0:
            raise Exception("No bib file in the folder `bibfile`!")
        else:
            inpaths = bib_files
    else:
        inputs = args.input
        inpaths = inputs.split()

    for _, inpath in enumerate(inpaths):
        # open a bib file and read all the items in one time
        fin = open(inpath, 'r', encoding='UTF-8')
        bibin = fin.read()  # TODO: buffering all the items as a list in one time, if bib file is large, it will consume much time
        fin.close()

        # add end mark to bib file to ensure the last item can be matched
        if bibin[-1] != "%":
            try:
                bibin = bibin + "%"
            except:
                print("Format ERROR: cannot add end mark! Please add '%' in the end of the bib file manually!")

        # matched items
        comments_matches = re.finditer(regs.comments, bibin, re.MULTILINE | re.IGNORECASE)
        abbr_matches = re.finditer(regs.abbr, bibin, re.MULTILINE | re.IGNORECASE)

        # write tidy bib file
        _, out_name = os.path.split(inpath)
        if args.input is None:
            fout = open("bibfile/tidy_" + out_name, 'w', encoding='UTF-8')
        else:
            fout = open("tidy_" + out_name, 'w', encoding='UTF-8')
        fcomments = open("comment_logs.txt", 'w', encoding='UTF-8')

        print("\nBegin to process " + inpath + ". Please wait...")

        # comments
        for matchNum, match in enumerate(comments_matches, start=1):
            item = match.group()
            fcomments.write(item + "\n")
        fcomments.write("\n")

        # abbr
        for matchNum, match in enumerate(abbr_matches, start=1):
            item = match.group()
            abbr = re.sub("\n+", "", item)
            abbr = re.sub(" +", " ", abbr)
            fout.write(abbr + "\n")
        fout.write("\n")

        # set a counter for processed items
        count = 0

        numInproceed = tidy_item(regs.inproceedings_regex, bibin, fout, regs)
        numProceed = tidy_item(regs.proceedings_regex, bibin, fout, regs)
        numMisc = tidy_item(regs.misc_regex, bibin, fout, regs)
        numBook = tidy_item(regs.book_regex, bibin, fout, regs)
        numArticle = tidy_item(regs.article_regex, bibin, fout, regs)
        numIncollection = tidy_item(regs.incollection_regex, bibin, fout, regs)

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


if __name__ == '__main__':
    args = parses()
    regs = BuildRegex()
    main(args, regs)