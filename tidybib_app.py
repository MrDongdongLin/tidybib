import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import bibtexparser
import re
from threading import Timer

class TidyBibApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TidyBib")
        self.bib_database = None

        self.CONSTANT_FIELD = ['ENTRYTYPE', 'ID']

        self.field_order = [
            'author', 'title', 'journal', 'year', 'volume', 
            'number', 'pages', 'month', 'note', 'abstract', 
            'keywords', 'source', 'doi'
        ]

        self.fields = list(set(
            self.CONSTANT_FIELD
            + self.field_order
        ))

        self.prepositions = {'of', 'the', 'and', 'in', 'on', 'for', 'with', 'a', 'an', 'by', 'at', 'to'}
        self.special_words = {'IEEE', 'ACM', 'IEEE/ACM'}

        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.state('zoomed')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=6, relief="flat", background="#ccc")
        style.configure('TText', padding=6, relief="flat")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.text_left_frame = ttk.Frame(self.main_frame)
        self.text_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_left_scrollbar = ttk.Scrollbar(self.text_left_frame)
        self.text_left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_left = tk.Text(self.text_left_frame, wrap=tk.NONE, relief="flat", bd=2, font=("Courier", 12), yscrollcommand=self.text_left_scrollbar.set)
        self.text_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_left.bind("<KeyRelease>", self.schedule_highlight_syntax)

        self.text_left_scrollbar.config(command=self.text_left.yview)

        self.text_right_frame = ttk.Frame(self.main_frame)
        self.text_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_right_scrollbar = ttk.Scrollbar(self.text_right_frame)
        self.text_right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_right = tk.Text(self.text_right_frame, wrap=tk.NONE, relief="flat", bd=2, font=("Courier", 12), yscrollcommand=self.text_right_scrollbar.set)
        self.text_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_right_scrollbar.config(command=self.text_right.yview)

        self.checkboxes_frame = ttk.Frame(self.main_frame)
        self.checkboxes_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(fill=tk.X, expand=False, pady=10)

        self.browse_button = ttk.Button(self.bottom_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        self.tidy_button = ttk.Button(self.bottom_frame, text="Tidy", command=self.tidy)
        self.tidy_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(self.bottom_frame, text="Save As...", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = ttk.Button(self.bottom_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        self.output_message = tk.Text(root, height=10, wrap=tk.WORD, relief="flat", bd=2, font=("Courier", 12))
        self.output_message.pack(fill=tk.X, expand=False, padx=10, pady=10)

        self.trial_label = ttk.Label(root, text="Copyright dongdonglin8@gmail.com", foreground="red", font=("Courier", 10, "italic"))
        self.trial_label.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # Set up tags for syntax highlighting
        self.setup_syntax_tags(self.text_left)
        self.setup_syntax_tags(self.text_right)

        self.highlight_timer = None

        # Context menus
        self.context_menu_left = tk.Menu(self.text_left, tearoff=0)
        self.context_menu_left.add_command(label="Find", command=lambda: self.show_find_dialog(self.text_left))

        self.context_menu_right = tk.Menu(self.text_right, tearoff=0)
        self.context_menu_right.add_command(label="Find", command=lambda: self.show_find_dialog(self.text_right))

        self.text_left.bind("<Button-3>", self.show_context_menu)
        self.text_right.bind("<Button-3>", self.show_context_menu)

        # Bind Ctrl+F to find function
        self.root.bind('<Control-f>', self.show_find_dialog)

    def setup_syntax_tags(self, text_widget):
        text_widget.tag_configure("keyword", foreground="blue")
        text_widget.tag_configure("braces", foreground="orange")
        text_widget.tag_configure("equal_sign", foreground="red")
        text_widget.tag_configure("field", foreground="purple")
        text_widget.tag_configure("value", foreground="green")

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.text_left.delete("1.0", tk.END)
        try:
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_left.insert(tk.END, content)
                    
                    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                    parser.customization = bibtexparser.customization.convert_to_unicode
                    parser.homogenize_fields = False
                    parser.ignore_nonstandard_types = False
                    self.bib_database = bibtexparser.loads(content, parser=parser)
                    
                self.output_message.insert(tk.END, f"Loaded file: {file_path}\n")
                self.schedule_highlight_syntax(None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.output_message.insert(tk.END, f"Failed to load file: {file_path}\n{str(e)}\n")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".bib", filetypes=[("BibTeX files", "*.bib")])
        try:
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_right.get("1.0", tk.END))
                self.output_message.insert(tk.END, f"Saved file: {file_path}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            self.output_message.insert(tk.END, f"Failed to save file: {file_path}\n{str(e)}\n")

    def exit_app(self):
        self.root.quit()

    def tidy(self):
        try:
            content = self.text_left.get("1.0", tk.END)
            parser = bibtexparser.bparser.BibTexParser(common_strings=True)
            parser.customization = bibtexparser.customization.convert_to_unicode
            parser.homogenize_fields = False
            parser.ignore_nonstandard_types = False
            self.bib_database = bibtexparser.loads(content, parser=parser)
            
            simplified_content = self.simplify_bib()
            self.text_right.delete("1.0", tk.END)
            self.text_right.insert(tk.END, simplified_content)
            self.output_message.insert(tk.END, "Tidied content.\n")
            self.schedule_highlight_syntax(None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to tidy content: {str(e)}")
            self.output_message.insert(tk.END, f"Failed to tidy content: {str(e)}\n")

    def simplify_bib(self):
        if self.bib_database is None:
            return ""

        for entry in self.bib_database.entries:
            for field in list(entry.keys()):
                if field not in self.fields:
                    del entry[field]
            if 'journal' in entry:
                entry['journal'] = self.capitalize_title(entry['journal'])

            author = entry.get('author', '')
            year = entry.get('year', '')
            title = entry.get('title', '')
            
            author_first_word = re.sub(r'\W+', '', author.split()[0]) if author else ''
            year_first_word = re.sub(r'\W+', '', year.split()[0]) if year else ''
            title_first_word = ''.join([word[:2] for word in title.split()[:3]])
            
            new_key = f"{author_first_word}:{year_first_word}:{title_first_word}"
            entry['ID'] = new_key

        writer = bibtexparser.bwriter.BibTexWriter()
        writer.order_entries_by = None

        simplified_content = ""
        for entry in self.bib_database.entries:
            entry_type = entry.pop('ENTRYTYPE', 'article')
            entry_id = entry.pop('ID', 'unknown')
            simplified_content += f"@{entry_type}{{{entry_id},\n"
            for field in self.field_order:
                if field in entry:
                    simplified_content += f"  {field:<12} = {{{entry[field]}}},\n"
            simplified_content += "}\n\n"

        return simplified_content

    def capitalize_title(self, title):
        def capitalize_word(word):
            if word.startswith('{') and word.endswith('}'):
                return word
            if word in self.special_words:
                return word
            if word.lower() in self.prepositions:
                return word.lower()
            return word.capitalize()

        words = title.split()
        capitalized_words = [capitalize_word(word) for word in words]
        capitalized_title = ' '.join(capitalized_words)
        return capitalized_title

    def schedule_highlight_syntax(self, event):
        if self.highlight_timer:
            self.highlight_timer.cancel()
        self.highlight_timer = Timer(0.5, self.highlight_syntax)
        self.highlight_timer.start()

    def highlight_syntax(self):
        self.clear_tags(self.text_left)
        self.clear_tags(self.text_right)

        keyword_pattern = re.compile(r"@\w+{")
        braces_pattern = re.compile(r"[{}]")
        equal_sign_pattern = re.compile(r"=")
        field_pattern = re.compile(r"\b(?:author|title|journal|year|volume|number|pages|month|note|abstract|keywords|source|doi)\b")
        value_pattern = re.compile(r"{[^{}]*}")

        for text_widget in [self.text_left, self.text_right]:
            content = text_widget.get("1.0", tk.END)
            for match in keyword_pattern.finditer(content):
                text_widget.tag_add("keyword", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            for match in braces_pattern.finditer(content):
                text_widget.tag_add("braces", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            for match in equal_sign_pattern.finditer(content):
                text_widget.tag_add("equal_sign", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            for match in field_pattern.finditer(content):
                text_widget.tag_add("field", f"1.0+{match.start()}c", f"1.0+{match.end()}c")
            for match in value_pattern.finditer(content):
                text_widget.tag_add("value", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

    def clear_tags(self, text_widget):
        text_widget.tag_remove("keyword", "1.0", tk.END)
        text_widget.tag_remove("braces", "1.0", tk.END)
        text_widget.tag_remove("equal_sign", "1.0", tk.END)
        text_widget.tag_remove("field", "1.0", tk.END)
        text_widget.tag_remove("value", "1.0", tk.END)

    def show_context_menu(self, event):
        try:
            widget = event.widget
            if widget == self.text_left:
                self.context_menu_left.tk_popup(event.x_root, event.y_root)
            elif widget == self.text_right:
                self.context_menu_right.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu_left.grab_release()
            self.context_menu_right.grab_release()

    def show_find_dialog(self, event=None, widget=None):
        if widget is None:
            widget = self.text_left if self.text_left.focus_get() == self.text_left else self.text_right
        
        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("Find")
        self.find_dialog.geometry("300x100")

        tk.Label(self.find_dialog, text="Find:").pack(side=tk.LEFT, padx=10, pady=10)
        self.find_entry = ttk.Entry(self.find_dialog)
        self.find_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.find_entry.focus_set()

        find_button = ttk.Button(self.find_dialog, text="Find", command=lambda: self.find_text(widget))
        find_button.pack(side=tk.LEFT, padx=10, pady=10)

    def find_text(self, widget):
        search_term = self.find_entry.get()
        widget.tag_remove('found', '1.0', tk.END)
        if search_term:
            idx = '1.0'
            while True:
                idx = widget.search(search_term, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = f'{idx}+{len(search_term)}c'
                widget.tag_add('found', idx, lastidx)
                idx = lastidx
            widget.tag_config('found', foreground='red', background='yellow')

if __name__ == "__main__":
    root = tk.Tk()
    app = TidyBibApp(root)
    root.mainloop()
