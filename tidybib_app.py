import tkinter as tk
import bibtexparser
from tkinter import filedialog
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

        # Create a list of unique field
        self.fields = list(set(
            self.CONSTANT_FIELD
            + self.incollection_regex 
            + self.article_regex 
            + self.proceedings_regex 
            + self.misc_regex 
            + self.book_regex
            + self.article_regex
            + self.incollection_regex
        ))  # All fields

        # Make the window adaptive to screen size
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.state('zoomed')

        # Create the main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create text areas
        self.text_left = tk.Text(self.main_frame, wrap=tk.NONE)
        self.text_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_right = tk.Text(self.main_frame, wrap=tk.NONE)
        self.text_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.checkboxes_frame = tk.Frame(self.main_frame)
        self.checkboxes_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # self.field_vars = {}  # Dictionary to store the field variables

        # # Create checkboxes for each field
        # for field in self.fields:
        #     var = tk.BooleanVar()
        #     self.field_vars[field] = var
        #     checkbox = tk.Checkbutton(self.checkboxes_frame, text=field, variable=var)
        #     checkbox.pack(anchor=tk.W)

        # Create bottom frame
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(fill=tk.X, expand=False)

        # Create buttons
        self.browse_button = tk.Button(self.bottom_frame, text="Browse", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT)

        self.tidy_button = tk.Button(self.bottom_frame, text="Tidy", command=self.tidy)
        self.tidy_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.bottom_frame, text="Save As...", command=self.save_file)
        self.save_button.pack(side=tk.LEFT)

        self.exit_button = tk.Button(self.bottom_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(side=tk.LEFT)

        # Create output message box
        self.output_message = tk.Text(root, height=10)
        self.output_message.pack(fill=tk.X, expand=False)

        # Create trial period label
        self.trial_label = tk.Label(root, text="Copyright dongdonglin8@gmail.com", fg="red")
        self.trial_label.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        self.text_left.delete("1.0", tk.END)  # Clear the existing content
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_left.insert(tk.END, content)
                
                # Load with OrderedDict
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                parser.customization = bibtexparser.customization.convert_to_unicode
                parser.homogenize_fields = False
                parser.ignore_nonstandard_types = False
                self.bib_database = bibtexparser.loads(content, parser=parser)
                
            self.output_message.insert(tk.END, f"Loaded file: {file_path}\n")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".bib", filetypes=[("BibTeX files", "*.bib")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_right.get("1.0", tk.END))
            self.output_message.insert(tk.END, f"Saved file: {file_path}\n")

    def exit_app(self):
        self.root.quit()

    def tidy(self):
        simplified_content = self.simplify_bib()
        self.text_right.delete("1.0", tk.END)
        self.text_right.insert(tk.END, simplified_content)
        self.output_message.insert(tk.END, "Tidied content.\n")

    # def modify_entry_keys(self):
    #     new_entries_dict = {}
    #     for old_key, entry in list(self.bib_database.entries_dict.items()):
    #         author = entry.get('author', '')
    #         year = entry.get('year', '')
    #         title = entry.get('title', '')
            
    #         # Extract the first word of author, year, and title
    #         author_first_word = re.sub(r'\W+', '', author.split()[0]) if author else ''
    #         year_first_word = re.sub(r'\W+', '', year.split()[0]) if year else ''
    #         title_first_word = re.sub(r'\W+', '', title.split()[0]) if title else ''
            
    #         # Create the new key in the desired format
    #         new_key = f"{author_first_word}:{year_first_word}:{title_first_word}"
            
    #         # Update the key in the entries_dict
    #         new_entries_dict[new_key] = entry
    #     self.new_entries_dict = new_entries_dict

    def simplify_bib(self):
        # Define your BibTeX simplification logic here
        if self.bib_database is None:
            return ""

        # Simplify the BibTeX by removing the 'publisher' field from all entries
        for entry in self.bib_database.entries:
            for field in list(entry.keys()):  # We need to create a copy of the keys
                if field not in self.fields:
                    del entry[field]
            author = entry.get('author', '')
            year = entry.get('year', '')
            title = entry.get('title', '')
            
            # Extract the first word of author, year, and title
            author_first_word = re.sub(r'\W+', '', author.split()[0]) if author else ''
            year_first_word = re.sub(r'\W+', '', year.split()[0]) if year else ''
            title_first_word = ''.join([word[:2] for word in title.split()[:3]])
            
            # Create the new key in the desired format
            new_key = f"{author_first_word}:{year_first_word}:{title_first_word}"
            entry['ID'] = new_key

        # Convert the simplified BibTeX database back to a string, preserving order
        writer = bibtexparser.bwriter.BibTexWriter()
        writer.order_entries_by = None  # Preserve the original order
        simplified_content = writer.write(self.bib_database)

        # Format the output with aligned equal signs
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
                key, value = line.split('=')
                formatted_line = "  {:<12} {}".format(key.strip(), " = " +value.strip())
                formatted_content += formatted_line + '\n'
            else:
                formatted_content += line + '\n'
            i += 1

        return formatted_content

if __name__ == "__main__":
    root = tk.Tk()
    app = TidyBibApp(root)
    root.mainloop()

