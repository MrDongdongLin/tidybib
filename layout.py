import PySimpleGUI as sg


class TidyBIB():

    def __init__(self):
        self.theme = 'LightGreen'
        self.font = 'Consolas'
        self.font_size = 11

    def about(self):

        layout = [[sg.Text('tidybib')],
                [sg.OK()]]

        window = sg.Window('About tidybib', layout)
        event, values = window.read()
        window.close()


    def menus(self):

        sg.theme(self.theme)
        sg.set_options(element_padding=(0, 0))
        font = (self.font, self.font_size)

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
        
        return window