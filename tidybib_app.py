#!/usr/bin/env python
from utils.regs import TidyBIBRegex
from layout import TidyBIBLayout
from tidyer import Tidyer


class TidyBIBApp(TidyBIBLayout):
    def __init__(self):
        TidyBIBLayout.__init__(self)
        self.base_cls = 'TidyBIB'

    def tidy_processor(self):
        bibin = ""
        regs = TidyBIBRegex()  # build regex
        if self.values['tidyid']:
            regs.tidyid = True
        regs.build_regex()
        if self.custom_fileds:  # custom fields not empty
            for k, v in self.custom_fileds.items():
                if not v:  # if the field is not selected
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
        for lines in self.values['input']:
            bibin = bibin + lines
        # window['output'].Update(text)
        if self.values['ind_space']:
            self.tidyer = Tidyer(indent='space')
        elif self.values['ind_tab']:
            self.tidyer = Tidyer(indent='tab')
        outputs, msg = self.tidyer.tidyer(regs, bibin)
        mystr = ''
        for x in outputs:
            mystr += '' + x
        self.tidybib_window['output'].Update('')
        self.tidybib_window['output'].Update(mystr)
        # print(outputs)
        outmsg = ''
        outmsg += 'Total bib items: ' + str(msg['total']) + ' ('
        outmsg += 'Article: ' + str(msg['article']) + ' |'
        outmsg += '\t' + 'Inproceedings: ' + str(msg['inproc']) + ' |'
        outmsg += '\t' + 'Proceedings: ' + str(msg['proc']) + ' |'
        outmsg += '\t' + 'Book: ' + str(msg['book']) + ' |'
        outmsg += '\t' + 'Misc: ' + str(msg['misc']) + ' |'
        outmsg += '\t' + 'Incollection: ' + str(msg['incollect'])
        outmsg += ')'
        self.tidybib_window['outmsg'].Update('')
        self.tidybib_window['outmsg'].Update(outmsg)


if __name__ == '__main__':
    tidybib_app = TidyBIBApp()
    tidybib_app.event_processor()
