import PySimpleGUI as sg
from pathlib import Path
from abc import ABC, abstractmethod


class TidyBIBLayout(ABC):

    def __init__(self):
        self.theme = 'LightGreen'
        self.font = 'Consolas'
        self.font_size = 11
        self.event = dict()
        self.values = dict()
        self.custom_fileds = dict()
        self.tidybib_window = dict()
    
    @staticmethod
    def about():
        layout = [[sg.Text('tidybib')],
                [sg.OK()]]

        window = sg.Window('About tidybib', layout)
        window.close()

    @staticmethod
    def edit_fields():
        layout = [ [sg.Checkbox('Author',key='author',default=True), 
                    sg.Checkbox('Title',key='title',default=True),
                    sg.Checkbox('Booktitle',key='booktitle'),
                    sg.Checkbox('Year',key='year',default=True),
                    sg.Checkbox('Editor',key='editor'),
                    sg.Checkbox('Volume',key='volume')],
                   [sg.Checkbox('Number',key='number',default=True),
                    sg.Checkbox('Series',key='series'),
                    sg.Checkbox('Pages',key='pages',default=True),
                    sg.Checkbox('Publisher',key='publisher'),
                    sg.Checkbox('DOI',key='doi')],
                   [sg.Button('Save', pad=(1,10))]
                    ]

        window = sg.Window('Select fields', layout)
        _, values = window.read()
        window.close()
        return values

    def menus(self):

        sg.theme(self.theme)
        sg.set_options(element_padding=(0, 0))
        font = (self.font, self.font_size)

        # ------ Menu Definition ------ #
        menu_def = [['&File', ['&Open', '&Save', 'E&xit']],
                    ['&Edit', ['&Fields']],
                    ['&Help', '&About'], ]

        right_click_menu = ['Font', ['Font size', '!&Click', '&Menu', 'E&xit', 'Properties']]

        # ------ GUI Defintion ------ #
        layout = [  [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
                    [sg.Multiline(size=(60,25), key='-Input-', expand_x=True, expand_y=True, font=font),
                     sg.Multiline(size=(60,25), key='-Output-', expand_x=True, expand_y=True, font=font)],
                    [sg.Radio('Indent space', 'indent_space', key='ind_space',default=True),
                     sg.Radio('Indent tab', 'indent_space',key='ind_tab',default=False)],
                    [sg.Multiline(size=(122,2), key='-OutMsg-', expand_x=True, expand_y=True, background_color='Gray', text_color='White', font=font)],
                    [sg.Input(visible=False, enable_events=True, key='-IN-'), sg.FilesBrowse(pad=(1,10)),
                     sg.Button('Tidy', pad=(10,10)), 
                     sg.InputText('', do_not_clear=False, visible=False, key='Filepath', enable_events=True),
                     sg.FileSaveAs(initial_folder='./bibfile',pad=(10,10)), 
                     sg.Button('Exit', pad=(10,10))]
        ]

        window = sg.Window("Tidybib",
                        layout,
                        default_element_size=(12, 1),
                        default_button_element_size=(12, 1),
                        right_click_menu=right_click_menu,
                        resizable=True)
        
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
            elif self.event == 'Open':
                filename = sg.popup_get_file('file to open', no_window=True)
                if Path(filename).is_file():
                    try:
                        with open(filename, "r", encoding='utf-8') as f:
                            text = f.read()
                        self.tidybib_window['-Input-'].Update('')
                        self.tidybib_window['-Input-'].Update(text)
                    except Exception as e:
                        print("Error: ", e)
            elif self.event == '-IN-':
                filename = self.values['-IN-']
                if Path(filename).is_file():
                    try:
                        with open(filename, "r", encoding='utf-8') as f:
                            text = f.read()
                        self.tidybib_window['-Input-'].Update('')
                        self.tidybib_window['-Input-'].Update(text)
                    except Exception as e:
                        print("Error: ", e)
            elif self.event == 'Filepath':
                with open(self.values['Filepath'], "wt", encoding='UTF-8') as f:
                    f.write(self.tidybib_window['-Output-'].get())
            elif self.event == 'Fields':
                self.custom_fileds = self.edit_fields()
                # print(self.custom_fileds)
            elif self.event == 'Tidy':
                self.tidy_processor()
        self.tidybib_window.close()

    @abstractmethod
    def tidy_processor(self):
        pass