import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import bibtexparser
import re

class TidyBibApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TidyBib")
        self.bib_database = None

        self.CONSTANT_FIELD = ['ENTRYTYPE', 'ID']
        
        self.inproceedings_regex = [
            'author',
            'title',
            'booktitle',
            'year',
            'editor',
            'volume',
            'number',
            'series',
            'pages',
            'doi',
        ]

        self.proceedings_regex = [
            'title',
            'year',
            'editor',
            'publisher',
            'volume',
            'number',
            'series',
            'month',
        ]

        self.misc_regex = [
            'author',
            'title',
            'howpublished',
            'year',
            'month',
        ]

        self.book_regex = [
            'author',
            'title',
            'year',
            'edition',
            'publisher',
            'address',
            'doi',
        ]

        self.article_regex = [
            'author',
            'title',
            'journal',
            'year',
            'volume',
            'number',
            'pages',
            'doi',
        ]

        self.incollection_regex = [
            'author',
            'title',
            'booktitle',
            'pages',
            'year',
        ]

        self.fields = list(set(
            self.CONSTANT_FIELD
            + self.incollection_regex 
            + self.article_regex 
            + self.proceedings_regex 
            + self.misc_regex 
            + self.book_regex
            + self.article_regex
            + self.incollection_regex
        ))

        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.state('zoomed')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=6, relief="flat", background="#ccc")
        style.configure('TText', padding=6, relief="flat")

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.text_left = tk.Text(self.main_frame, wrap=tk.NONE, relief="flat", bd=2, font=("Courier", 12))
        self.text_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_left.bind("<KeyRelease>", self.highlight_syntax)

        self.text_right = tk.Text(self.main_frame, wrap=tk.NONE, relief="flat", bd=2, font=("Courier", 12))
        self.text_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_right.bind("<KeyRelease>", self.highlight_syntax)

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
        self.text_left.tag_configure("keyword", foreground="blue")
        self.text_left.tag_configure("braces", foreground="orange")
        self.text_left.tag_configure("equal_sign", foreground="red")
        self.text_left.tag_configure("field", foreground="purple")
        self.text_left.tag_configure("value", foreground="green")

        self.text_right.tag_configure("keyword", foreground="blue")
        self.text_right.tag_configure("braces", foreground="orange")
        self.text_right.tag_configure("equal_sign", foreground="red")
        self.text_right.tag_configure("field", foreground="purple")
        self.text_right.tag_configure("value", foreground="green")

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
                self.highlight_syntax(None)
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
            self.highlight_syntax(None)
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
        simplified_content = writer.write(self.bib_database)

        lines = simplified_content.split('\n')
        formatted_content = ""
        i = 0
        while i < len(lines):
            line = lines[i]
            if i < len(lines) - 1 and len(line) > 1 and not line.startswith('@') and not line.endswith('},') and not line.endswith('}'):
                next_line = lines[i + 1]
                line += ' ' + next_line
                i += 1
            if '=' in line:
                key, value = line.split('=', 1)
                formatted_line = "  {:<12} {}".format(key.strip(), " = " +value.strip())
                formatted_content += formatted_line + '\n'
            else:
                formatted_content += line + '\n'
            i += 1

        return formatted_content

    def highlight_syntax(self, event):
        self.text_left.tag_remove("keyword", "1.0", tk.END)
        self.text_left.tag_remove("braces", "1.0", tk.END)
        self.text_left.tag_remove("equal_sign", "1.0", tk.END)
        self.text_left.tag_remove("field", "1.0", tk.END)
        self.text_left.tag_remove("value", "1.0", tk.END)
        
        self.text_right.tag_remove("keyword", "1.0", tk.END)
        self.text_right.tag_remove("braces", "1.0", tk.END)
        self.text_right.tag_remove("equal_sign", "1.0", tk.END)
        self.text_right.tag_remove("field", "1.0", tk.END)
        self.text_right.tag_remove("value", "1.0", tk.END)

        keyword_pattern = re.compile(r"@\w+{")
        braces_pattern = re.compile(r"[{}]")
        equal_sign_pattern = re.compile(r"=")
        field_pattern = re.compile(r"\b(?:author|title|booktitle|year|editor|volume|number|series|pages|doi|publisher|month|journal|address|edition|howpublished)\b")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = TidyBibApp(root)
    root.mainloop()
