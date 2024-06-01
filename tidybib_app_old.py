#!/usr/bin/env python
from utils.regs import TidyBIBRegex
from layout import TidyBIBLayout
from tidyer import Tidyer


class TidyBIBApp(TidyBIBLayout):
    def __init__(self):
        super().__init__()
        self.base_cls = 'TidyBIB'

    def tidy_processor(self):
        bibin = "".join(self.values['input'])
        regs = TidyBIBRegex()  # build regex
        if self.values['tidyid']:
            regs.tidyid = True
        regs.build_regex()
        if self.custom_fileds:  # custom fields not empty
            for k, v in self.custom_fileds.items():
                if not v:  # if the field is not selected
                    for regex in [regs.inproceedings_regex, regs.proceedings_regex, regs.misc_regex, regs.book_regex, regs.article_regex, regs.incollection_regex]:
                        if k in regex:
                            del regex[k]
        if self.values['ind_space']:
            self.tidyer = Tidyer(indent='space')
        elif self.values['ind_tab']:
            self.tidyer = Tidyer(indent='tab')
        outputs, msg = self.tidyer.tidyer(regs, bibin)
        mystr = ''.join(outputs)
        self.tidybib_window['output'].Update(mystr)
        outmsg = f"Total bib items: {msg['total']} (Article: {msg['article']} | Inproceedings: {msg['inproc']} | Proceedings: {msg['proc']} | Book: {msg['book']} | Misc: {msg['misc']} | Incollection: {msg['incollect']})"
        self.tidybib_window['outmsg'].Update(outmsg)


if __name__ == '__main__':
    tidybib_app = TidyBIBApp()
    tidybib_app.event_processor()
