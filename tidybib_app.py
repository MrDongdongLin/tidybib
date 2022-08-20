#!/usr/bin/env python
from pathlib import Path
import PySimpleGUI as sg
import re
import os
import glob
import argparse
from utils.parse import parses
from utils.regs import BuildRegex


def second_window():

    layout = [[sg.Text('tidybib')],
              [sg.OK()]]

    window = sg.Window('About tidybib', layout)
    event, values = window.read()
    window.close()


def test_menus():

    sg.theme('LightGreen')
    sg.set_options(element_padding=(0, 0))
    font = ("Consolas", 11)

    # ------ Menu Definition ------ #
    menu_def = [['&File', ['&Open', '&Save', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo'], ],
                ['&Help', '&About'], ]

    right_click_menu = ['Unused', ['Right', '!&Click', '&Menu', 'E&xit', 'Properties']]

    # ------ GUI Defintion ------ #
    layout = [  [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
                [sg.Multiline(size=(80,30), key='-Input-', expand_x=True, expand_y=True, font=font),
                 sg.Multiline(size=(80,30), key='-Output-', expand_x=True, expand_y=True, font=font)],
                [sg.Multiline(size=(162,2), key='-OutMsg-', expand_x=True, expand_y=True, background_color='Gray', text_color='White', font=font)],
                [sg.Input(visible=False, enable_events=True, key='-IN-'), sg.FilesBrowse(pad=(10,10)),
                 sg.Button('Tidy', pad=(10,10)), 
                 sg.InputText('', do_not_clear=False, visible=False, key='Filepath', enable_events=True),
                 sg.FileSaveAs(initial_folder='./bibfile',pad=(10,10)), 
                 sg.Button('Exit', pad=(10,10))]
    ]

    window = sg.Window("tidybib",
                       layout,
                       default_element_size=(12, 1),
                       default_button_element_size=(12, 1),
                       right_click_menu=right_click_menu,
                       resizable=True)

    # ------ Loop & Process button menu choices ------ #
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # ------ Process menu choices ------ #
        if event == 'About':
            second_window()
        elif event == 'Open':
            filename = sg.popup_get_file('file to open', no_window=True)
            if Path(filename).is_file():
                try:
                    with open(filename, "r", encoding='utf-8') as f:
                        text = f.read()
                    window['-Input-'].Update(text)
                except Exception as e:
                    print("Error: ", e)
        elif event == '-IN-':
            filename = values['-IN-']
            if Path(filename).is_file():
                try:
                    with open(filename, "r", encoding='utf-8') as f:
                        text = f.read()
                    window['-Input-'].Update(text)
                except Exception as e:
                    print("Error: ", e)
        elif event == 'Tidy':
            bibin = ""
            args = parses()
            regs = BuildRegex()
            for lines in values["-Input-"]:
                bibin = bibin + lines
            # window['-Output-'].Update(text)
            msg = main(regs, bibin)
            mystr = ''
            for x in outputs:
                mystr += ''+x
            window['-Output-'].Update(mystr)
            # print(outputs)
            outmsg = ''
            outmsg += 'Total bib tiems: ' + str(msg['total']) + ' ('
            outmsg += 'Article: ' + str(msg['article']) + ' |'
            outmsg += '\t' + 'Inproceedings: ' + str(msg['inproc']) + ' |'
            outmsg += '\t' + 'Proceedings: ' + str(msg['proc']) + ' |'
            outmsg += '\t' + 'Book: ' + str(msg['book']) + ' |'
            outmsg += '\t' + 'Misc: ' + str(msg['misc']) + ' |'
            outmsg += '\t' + 'Incollection: ' + str(msg['incollect'])
            outmsg += ')'
            window['-OutMsg-'].Update(outmsg)

        elif event == 'Filepath':
            with open(values['Filepath'], "wt", encoding='UTF-8') as f:
                f.write(window['-Output-'].get())


    window.close()


def field_content(field, reg_field, reg_content, object_str):
    match_field = re.finditer(reg_field, object_str, re.MULTILINE | re.IGNORECASE)
    try:
        next_match = next(match_field).group()
        match_content = re.finditer(reg_content, next_match, re.MULTILINE | re.IGNORECASE)
        next_content = next(match_content).group()
        # remove extra blanks and enters
        _content = re.sub("\n+", "", next_content)
        content = re.sub(" +", " ", _content)
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
                if key == "item" or len(value)==0:
                    continue
                elif key == "head":
                    content = re.finditer(value, item, re.MULTILINE | re.IGNORECASE)
                    head_content = next(content).group()
                    new_head = re.sub(" +", "", head_content)
                    new_head = new_head + '\n'
                    fout.append(new_head)
                else:
                    if key == "journal" or key == "booktitle":
                        journal_abbr = tidy_journal(key, value, item, regs)
                        new_journal_abbr = "  {:<14} {},\n".format(key + " =", journal_abbr)
                        fout.append(new_journal_abbr)
                        # fout.write("  {:<14} {},\n".format(key + " =", journal_abbr))
                    elif key == "title":
                        content = field_content(key, value, regs.outer_brace, item)
                        content = content[0] + content[1].upper() + content[2:]
                        content = content[1:-1]
                        content = "{" + tidy_title(content) + "}"
                        new_content = "  {:<14} {},\n".format(key + " =", content)
                        fout.append(new_content)
                        # fout.write("  {:<14} {},\n".format(key + " =", content))
                    else:
                        content = field_content(key, value, regs.outer_brace, item)
                        if content == "{}":
                            continue
                        else:
                            new_content = "  {:<14} {},\n".format(key + " =", content)
                            fout.append(new_content)
                            # fout.write("  {:<14} {},\n".format(key + " =", content))
            fout.append("}\n\n")
            # fout.write("}\n\n")
            counter += 1
        except StopIteration:
            break
    return counter


def main(regs, bibin):
    if bibin[-1] != "%":
        try:
            bibin = bibin + "%"
        except:
            print("Format ERROR: cannot add end mark! Please add '%' in the end of the bib file manually!")
    comments_matches = re.finditer(regs.comments, bibin, re.MULTILINE | re.IGNORECASE)
    abbr_matches = re.finditer(regs.abbr, bibin, re.MULTILINE | re.IGNORECASE)

    # write tidy bib file
    global outputs
    outputs = []
    for matchNum, match in enumerate(abbr_matches, start=1):
        item = match.group()
        abbr = re.sub("\n+", "", item)
        abbr = re.sub(" +", " ", abbr)
        new_abbr = abbr + '\n'
        if abbr == '':
            outputs.append(abbr)
        else:
            outputs.append(new_abbr)
    # outputs.append("\n")

    # set a counter for processed items
    count = 0

    numInproceed = tidy_item(regs.inproceedings_regex, bibin, outputs, regs)
    numProceed = tidy_item(regs.proceedings_regex, bibin, outputs, regs)
    numMisc = tidy_item(regs.misc_regex, bibin, outputs, regs)
    numBook = tidy_item(regs.book_regex, bibin, outputs, regs)
    numArticle = tidy_item(regs.article_regex, bibin, outputs, regs)
    numIncollection = tidy_item(regs.incollection_regex, bibin, outputs, regs)

    count = numInproceed + numProceed + numMisc + numBook + numArticle + numIncollection

    return {'total': count, 
            'inproc': numInproceed, 
            'proc': numProceed, 
            'misc': numMisc, 
            'book': numBook,
            'article': numArticle,
            'incollect': numIncollection}



test_menus()
