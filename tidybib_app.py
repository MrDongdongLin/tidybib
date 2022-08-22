#!/usr/bin/env python
import PySimpleGUI as sg
from pathlib import Path
from utils.parse import parses
from utils.regs import BuildRegex
from layout import TidyBIBLayout
from tidyer import Tidyer



class TidyBIBApp(TidyBIBLayout):
    def __init__(self):
        TidyBIBLayout.__init__(self)
        self.base_cls = 'TidyBIB'
        self.tidyer = Tidyer()

    def tidy_processor(self):
        bibin = ""
        regs = BuildRegex()                          # build regex
        if self.custom_fileds:                       # custom fields not empty
            for k, v in self.custom_fileds.items():
                if not v:                            # if the field is not selected
                    if k in regs.inproceedings_regex:
                        del regs.inproceedings_regex[k]
                    if k in regs.proceedings_regex:
                        del regs.proceedings_regex[k]
                    if k in regs.misc_regex:
                        del regs.misc_regex[k] 
                    if k in regs.book_regex:
                        del regs.book_regex[k]
                    if k in regs.article_regex:
                        del regs.article_regex[k]
                    if k in regs.incollection_regex:
                        del regs.incollection_regex[k]
        for lines in self.values['-Input-']:
            bibin = bibin + lines
        # window['-Output-'].Update(text)
        outputs, msg = self.tidyer.tidyer(regs, bibin)
        mystr = ''
        for x in outputs:
            mystr += ''+x
        
        self.tidybib_window['-Output-'].Update('')
        self.tidybib_window['-Output-'].Update(mystr)
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
        self.tidybib_window['-OutMsg-'].Update('')
        self.tidybib_window['-OutMsg-'].Update(outmsg)

if __name__ == '__main__':

    tidybib_app = TidyBIBApp()
    tidybib_app.event_processor()

