import PySimpleGUI as sg
from pathlib import Path
from abc import ABC, abstractmethod


class TidyBIBLayout(ABC):

    def __init__(self):
        self.mline = None
        self.theme = 'LightGreen'
        self.font = 'Consolas'  # 'Andale Mono'
        self.about_info = 'Tidybib version 1.0.0'
        self.font_size = 11
        self.event = dict()
        self.values = dict()
        self.custom_fileds = dict()
        self.tidybib_window = dict()

    @staticmethod
    def about(self):
        layout = [[sg.Text(self.about_info)],
                  [sg.OK()]]

        window = sg.Window('About tidybib', layout)
        window.close()

    @staticmethod
    def edit_fields():
        layout = [[sg.Checkbox('Author', key='author', default=True),
                   sg.Checkbox('Title', key='title', default=True),
                   sg.Checkbox('Booktitle', key='booktitle', default=True),
                   sg.Checkbox('Year', key='year', default=True),
                   sg.Checkbox('Editor', key='editor'),
                   sg.Checkbox('Volume', key='volume', default=True)],
                  [sg.Checkbox('Number', key='number', default=True),
                   sg.Checkbox('Series', key='series'),
                   sg.Checkbox('Pages', key='pages', default=True),
                   sg.Checkbox('Publisher', key='publisher'),
                   sg.Checkbox('DOI', key='doi', default=True)],
                  [sg.Button('Save', pad=(1, 10))]
                  ]

        window = sg.Window('Select fields', layout)
        _, values = window.read()
        window.close()
        return values

    def menus(self):

        sg.theme(self.theme)
        font = (self.font, self.font_size)
        sg.set_options(element_padding=(0, 0), font=font)

        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Open', '&Save', 'E&xit']],
                    ['&Edit', ['&Fields']],
                    ['&View', '&Theme'],
                    ['&Help', '&About'], ]

        right_click_menu = ['', ['Copy', 'Paste', 'Select All', 'Cut']]

        # ------ GUI Defintion ------ #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
                  [sg.Multiline(size=(60, 25), key='input', expand_x=True, expand_y=True),
                   sg.Multiline(size=(60, 25), key='output', expand_x=True, expand_y=True)],
                  [sg.Radio('Indent space', 'indent_space', key='ind_space', default=True),
                   sg.Radio('Indent tab', 'indent_space', key='ind_tab', default=False),
                   sg.Checkbox('TidyID', key='tidyid', default=False)],
                  [sg.Multiline(size=(122, 2), key='outmsg', expand_x=True, expand_y=True, background_color='Gray',
                                text_color='White', default_text='Output message...')],
                  [sg.Input(visible=False, enable_events=True, key='browsein'), sg.FilesBrowse(pad=(1, 10)),
                   sg.Button('Tidy', pad=(10, 10)),
                   sg.InputText('', do_not_clear=False, visible=False, key='saveas', enable_events=True),
                   sg.FileSaveAs(initial_folder='./bibfile', pad=(10, 10)),
                   sg.Button('Exit', pad=(10, 10))]
                  ]

        window = sg.Window("Tidybib",
                           layout,
                           default_element_size=(12, 1),
                           default_button_element_size=(12, 1),
                           right_click_menu=right_click_menu,
                           resizable=True)

        self.mline: sg.Multiline = window['input']

        return window

    def event_processor(self):
        self.tidybib_window = self.menus()
        # ------ Loop & Process button menu choices ------ #
        while True:
            self.event, self.values = self.tidybib_window.read()
            if self.event in (sg.WIN_CLOSED, 'Exit'):
                break
            # ------ Process menu choices ------ #
            if self.event == 'About':
                self.about()
            elif self.event == 'Select All':
                self.mline.Widget.selection_clear()
                self.mline.Widget.tag_add('sel', '1.0', 'end')
            elif self.event == 'Copy':
                try:
                    text = self.mline.Widget.selection_get()
                    self.tidybib_window.TKroot.clipboard_clear()
                    self.tidybib_window.TKroot.clipboard_append(text)
                except:
                    print('Nothing selected')
            elif self.event == 'Paste':
                self.mline.Widget.insert(sg.tk.INSERT, self.tidybib_window.TKroot.clipboard_get())
            elif self.event == 'Cut':
                try:
                    text = self.mline.Widget.selection_get()
                    self.tidybib_window.TKroot.clipboard_clear()
                    self.tidybib_window.TKroot.clipboard_append(text)
                    self.tidybib_window.update('')
                except:
                    print('Nothing selected')
            elif self.event == 'Open':
                filename = sg.popup_get_file('file to open', no_window=True)
                if Path(filename).is_file():
                    try:
                        with open(filename, "r", encoding='utf-8') as f:
                            text = f.read()
                        self.tidybib_window['input'].Update('')
                        self.tidybib_window['input'].Update(text)
                    except Exception as e:
                        print("Error: ", e)
            elif self.event == 'browsein':
                filename = self.values['browsein']
                if Path(filename).is_file():
                    try:
                        with open(filename, "r", encoding='utf-8') as f:
                            text = f.read()
                        self.tidybib_window['input'].Update('')
                        self.tidybib_window['input'].Update(text)
                    except Exception as e:
                        print("Error: ", e)
            elif self.event == 'saveas':
                with open(self.values['saveas'], "wt", encoding='UTF-8') as f:
                    f.write(self.tidybib_window['output'].get())
            elif self.event == 'Fields':
                self.custom_fileds = self.edit_fields()
                # print(self.custom_fileds)
            elif self.event == 'Tidy':
                self.tidy_processor()
        self.tidybib_window.close()

    @abstractmethod
    def tidy_processor(self):
        pass
