#!/usr/bin/env python
import PySimpleGUI as sg
from pathlib import Path
from utils.parse import parses
from utils.regs import BuildRegex
from layout import TidyBIB
from tidyer import Tidyer



if __name__ == '__main__':

    tidybib = TidyBIB()
    tidybib_window = tidybib.menus()
    tidyer = Tidyer()

    # ------ Loop & Process button menu choices ------ #
    while True:
        event, values = tidybib_window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # ------ Process menu choices ------ #
        if event == 'About':
            tidybib_window.about()
        elif event == 'Open':
            filename = sg.popup_get_file('file to open', no_window=True)
            if Path(filename).is_file():
                try:
                    with open(filename, "r", encoding='utf-8') as f:
                        text = f.read()
                    tidybib_window['-Input-'].Update(text)
                except Exception as e:
                    print("Error: ", e)
        elif event == '-IN-':
            filename = values['-IN-']
            if Path(filename).is_file():
                try:
                    with open(filename, "r", encoding='utf-8') as f:
                        text = f.read()
                    tidybib_window['-Input-'].Update(text)
                except Exception as e:
                    print("Error: ", e)
        elif event == 'Tidy':
            bibin = ""
            args = parses()
            regs = BuildRegex()
            for lines in values["-Input-"]:
                bibin = bibin + lines
            # window['-Output-'].Update(text)
            outputs, msg = tidyer.tidyer(regs, bibin)
            mystr = ''
            for x in outputs:
                mystr += ''+x
            tidybib_window['-Output-'].Update(mystr)
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
            tidybib_window['-OutMsg-'].Update(outmsg)

        elif event == 'Filepath':
            with open(values['Filepath'], "wt", encoding='UTF-8') as f:
                f.write(tidybib_window['-Output-'].get())
    tidybib_window.close()
