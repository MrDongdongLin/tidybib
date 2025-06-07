import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import bibtexparser
import re
from threading import Timer

class TidyBibApp:
    def __init__(self, root):
        self.root = root
        self._init_config()
        self._init_ui()
        self._bind_events()

    def _init_config(self):
        """Initialize application configuration"""
        self.root.title("TidyBib - Bibliography Manager")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.state('zoomed')
        self.root.configure(bg="#f8f9fa")

        # Data attributes
        self.bib_database = None
        self.highlight_timer = None
        self.find_dialog = None

        # Configuration constants
        self.CONSTANT_FIELDS = ['ENTRYTYPE', 'ID']
        self.FIELD_ORDER = [
            'author', 'title', 'journal', 'booktitle', 'year', 'volume',
            'number', 'pages', 'month', 'note', 'abstract', 'keywords', 
            'source', 'doi'
        ]
        self.fields = list(set(self.CONSTANT_FIELDS + self.FIELD_ORDER))
        
        # Text processing constants
        self.PREPOSITIONS = {
            'of', 'the', 'and', 'in', 'on', 'for', 'with', 'a', 'an', 
            'by', 'at', 'to', 'from', 'into', 'through'
        }
        
        # Special words and organizations that should maintain specific capitalization
        self.SPECIAL_WORDS = {
            # Technology terms
            'IEEE', 'ACM', 'AI', 'ML', 'IoT', 'API', 'GPU', 'CPU', 'HTTP', 'HTTPS',
            'XML', 'JSON', 'SQL', 'NoSQL', 'REST', 'SOAP', 'TCP', 'UDP', 'IP',
            'IEEE/CVF', 'IEEE/CVF', 'CVF', 'IEEE CVF',
            # Publishers and organizations
            'Springer', 'Elsevier', 'Wiley', 'Nature', 'Science', 'MIT', 'ACL',
            'AAAI', 'IJCAI', 'NIPS', 'ICML', 'ICLR', 'CVPR', 'ICCV', 'ECCV',
            'SIGKDD', 'SIGMOD', 'SIGCOMM', 'SIGCHI', 'SIGGRAPH'
        }
        
        # Organization abbreviations that should be corrected to uppercase
        self.ORGANIZATION_CORRECTIONS = {
            # IEEE variants - 注意：IEEE/CVF 应该保持全大写
            'ieee': 'IEEE',
            'Ieee': 'IEEE',
            'ieee/cvf': 'IEEE/CVF',
            'Ieee/cvf': 'IEEE/CVF',  # 这里应该改成全大写的 IEEE/CVF
            'Ieee/Cvf': 'IEEE/CVF',
            'IEEE/CVF': 'IEEE/CVF',
            'ieee cvf': 'IEEE CVF',
            'IEEE cvf': 'IEEE CVF',
            'Ieee cvf': 'IEEE CVF',
            'Ieee Cvf': 'IEEE CVF',
            
            # 会议名称 - 保持正确的 IEEE/CVF 格式
            'ieee conference on computer vision and pattern recognition': 'IEEE Conference on Computer Vision and Pattern Recognition',
            'ieee/cvf conference on computer vision and pattern recognition': 'IEEE/CVF Conference on Computer Vision and Pattern Recognition',
            'proceedings of the ieee conference on computer vision and pattern recognition': 'Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition',
            'proceedings of the ieee/cvf conference on computer vision and pattern recognition': 'Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition',
            
            # ACM variants
            'acm': 'ACM',
            'Acm': 'ACM',
            'acm sigsac': 'ACM SIGSAC',
            'ACM Sigsac': 'ACM SIGSAC',
            'acm sigkdd': 'ACM SIGKDD',
            'ACM Sigkdd': 'ACM SIGKDD',
            'acm sigmod': 'ACM SIGMOD',
            'ACM Sigmod': 'ACM SIGMOD',
            'acm sigcomm': 'ACM SIGCOMM',
            'ACM Sigcomm': 'ACM SIGCOMM',
            'acm sigchi': 'ACM SIGCHI',
            'ACM Sigchi': 'ACM SIGCHI',
            'acm siggraph': 'ACM SIGGRAPH',
            'ACM Siggraph': 'ACM SIGGRAPH',
            
            # Other organizations
            'aaai': 'AAAI',
            'Aaai': 'AAAI',
            'ijcai': 'IJCAI',
            'Ijcai': 'IJCAI',
            'nips': 'NIPS',
            'Nips': 'NIPS',
            'icml': 'ICML',
            'Icml': 'ICML',
            'iclr': 'ICLR',
            'Iclr': 'ICLR',
            'cvpr': 'CVPR',
            'Cvpr': 'CVPR',
            'iccv': 'ICCV',
            'Iccv': 'ICCV',
            'eccv': 'ECCV',
            'Eccv': 'ECCV',
            
            # Publishers
            'springer': 'Springer',
            'elsevier': 'Elsevier',
            'wiley': 'Wiley',
            'nature': 'Nature',
            'science': 'Science',
            
            # Universities and institutions
            'mit': 'MIT',
            'Mit': 'MIT'
        }

        # Load journal abbreviations
        self.journal_abbreviations = self._load_journal_abbreviations()

        # Syntax highlighting patterns (compiled once for efficiency)
        self.PATTERNS = {
            'keyword': re.compile(r"@\w+\{"),
            'braces': re.compile(r"[{}]"),
            'equal_sign': re.compile(r"="),
            'field': re.compile(r"\b(?:" + "|".join(self.FIELD_ORDER) + r")\b"),
            'value': re.compile(r"\{[^{}]*\}")
        }

    def _load_journal_abbreviations(self):
        """Load journal abbreviations from JSON file"""
        abbreviations = {}
        try:
            import os
            import json
            json_file_path = os.path.join(os.path.dirname(__file__), 'abbreviatelist.json')
            
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Convert to lowercase keys for case-insensitive matching
                    for full_name, abbrev in data.items():
                        abbreviations[full_name.lower()] = abbrev
                                    
        except Exception as e:
            self.output_message.insert(tk.END, f"⚠ Could not load journal abbreviations: {str(e)}\n")
            
        return abbreviations

    def _init_ui(self):
        """Initialize user interface"""
        self._setup_styles()
        self._create_menu()
        self._create_main_content()
        self._create_options_panel()
        self._create_output_panel()
        self._create_footer()
        self._setup_syntax_highlighting()

    def _setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define custom styles
        styles = {
            'Custom.TRadiobutton': {
                'font': ("Consolas", 10),
                'background': "#f8f9fa",
                'focuscolor': 'none'
            },
            'Action.TButton': {
                'font': ("Arial", 10, "bold"),
                'padding': (10, 5)
            },
            'TFrame': {'background': "#f8f9fa"},
            'TLabel': {'background': "#f8f9fa", 'font': ("Arial", 10)},
            'TLabelFrame': {'background': "#f8f9fa"},
            'TLabelFrame.Label': {'background': "#f8f9fa", 'font': ("Arial", 10, "bold")}
        }
        
        for style_name, config in styles.items():
            style.configure(style_name, **config)

    def _create_menu(self):
        """Create application menu"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.browse_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save As...", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Ctrl+Q")

        # Process menu
        process_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Process", menu=process_menu)
        process_menu.add_command(label="Tidy Bibliography", command=self.tidy, accelerator="Ctrl+T")
        process_menu.add_separator()
        process_menu.add_command(label="Clear Output", command=self.clear_output)

        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find", command=self.show_find_dialog, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All (Left)", command=lambda: self._select_all(self.text_left), accelerator="Ctrl+A")
        edit_menu.add_command(label="Select All (Right)", command=lambda: self._select_all(self.text_right))

        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_content(self):
        """Create main content area with text editors"""
        # Main content frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left text frame (Original)
        self._create_text_frame(
            parent=self.main_frame,
            title="Original BibTeX",
            side=tk.LEFT,
            attr_name="text_left"
        )

        # Right text frame (Tidied)
        self._create_text_frame(
            parent=self.main_frame,
            title="Tidied BibTeX",
            side=tk.RIGHT,
            attr_name="text_right"
        )

    def _create_text_frame(self, parent, title, side, attr_name):
        """Create a text editing frame with scrollbar"""
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        padx = (0, 5) if side == tk.LEFT else (5, 0)
        frame.pack(side=side, fill=tk.BOTH, expand=True, padx=padx)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        text_widget = tk.Text(
            frame,
            wrap=tk.NONE,
            relief="flat",
            bd=1,
            font=("Consolas", 11),
            yscrollcommand=scrollbar.set,
            bg="white",
            selectbackground="#007acc",
            selectforeground="white",
            insertbackground="#007acc",
            cursor="ibeam"
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_widget.bind("<KeyRelease>", self._schedule_highlight_syntax)

        scrollbar.config(command=text_widget.yview)

        # Store reference
        setattr(self, attr_name, text_widget)
        setattr(self, f"{attr_name}_scrollbar", scrollbar)

    def _create_options_panel(self):
        """Create options panel"""
        self.options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        self.options_frame.pack(fill=tk.X, padx=10, pady=5)

        # Citation key options
        self.modify_citation_key_var = tk.StringVar(value="keep")
        
        # Journal format options
        self.journal_format_var = tk.StringVar(value="full")

        # Left section - Citation Key Options
        citation_frame = ttk.Frame(self.options_frame)
        citation_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(citation_frame, text="Citation Keys:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        citation_options = [
            ("Keep Citation Keys", "keep"),
            ("Modify Citation Keys", "modify")
        ]

        for i, (text, value) in enumerate(citation_options):
            radio = ttk.Radiobutton(
                citation_frame,
                text=text,
                variable=self.modify_citation_key_var,
                value=value,
                style='Custom.TRadiobutton'
            )
            radio.pack(anchor=tk.W, pady=2)

        # Right section - Journal Format Options
        journal_frame = ttk.Frame(self.options_frame)
        journal_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))

        ttk.Label(journal_frame, text="Journal Format:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        journal_options = [
            ("Full Journal Names", "full"),
            ("Abbreviated Journal Names", "abbreviated")
        ]

        for i, (text, value) in enumerate(journal_options):
            radio = ttk.Radiobutton(
                journal_frame,
                text=text,
                variable=self.journal_format_var,
                value=value,
                style='Custom.TRadiobutton'
            )
            radio.pack(anchor=tk.W, pady=2)

    def _create_output_panel(self):
        """Create output message panel"""
        self.output_frame = ttk.LabelFrame(self.root, text="Output Messages", padding=10)
        self.output_frame.pack(fill=tk.X, padx=10, pady=5)

        self.output_message = tk.Text(
            self.output_frame,
            height=8,
            wrap=tk.WORD,
            relief="flat",
            bd=1,
            font=("Consolas", 10),
            bg="white"
        )
        self.output_message.pack(fill=tk.X, expand=False)
        
        # Add button frame below output message
        button_frame = ttk.Frame(self.output_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Tidy button
        self.tidy_button = ttk.Button(
            button_frame,
            text="🔧 Tidy Bibliography",
            command=self.tidy,
            style='Action.TButton'
        )
        self.tidy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save As button
        self.save_button = ttk.Button(
            button_frame,
            text="💾 Save As...",
            command=self.save_file,
            style='Action.TButton'
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Output button
        self.clear_button = ttk.Button(
            button_frame,
            text="🗑️ Clear Output",
            command=self.clear_output
        )
        self.clear_button.pack(side=tk.RIGHT)

    def _create_footer(self):
        """Create footer"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, pady=5)

        footer_label = ttk.Label(
            footer_frame,
            text="Copyright dongdonglin8@gmail.com",
            foreground="#6c757d",
            font=("Arial", 9, "italic")
        )
        footer_label.pack(side=tk.BOTTOM)

    def _setup_syntax_highlighting(self):
        """Setup syntax highlighting for text widgets"""
        for text_widget in [self.text_left, self.text_right]:
            # Configure tags
            text_widget.tag_configure("keyword", foreground="#0066cc", font=("Consolas", 11, "bold"))
            text_widget.tag_configure("braces", foreground="#ff8800")
            text_widget.tag_configure("equal_sign", foreground="#cc0000")
            text_widget.tag_configure("field", foreground="#6600cc", font=("Consolas", 11, "bold"))
            text_widget.tag_configure("value", foreground="#009900")
            text_widget.tag_configure("found", foreground="red", background="yellow")

            # Context menu
            context_menu = tk.Menu(text_widget, tearoff=0)
            context_menu.add_command(label="Find", command=lambda w=text_widget: self.show_find_dialog(widget=w))
            text_widget.bind("<Button-3>", lambda e, menu=context_menu: self._show_context_menu(e, menu))

    def _bind_events(self):
        """Bind keyboard shortcuts and events"""
        shortcuts = {
            '<Control-o>': self.browse_file,
            '<Control-s>': self.save_file,
            '<Control-t>': self.tidy,
            '<Control-q>': self.exit_app,
            '<Control-f>': self.show_find_dialog,
            '<Control-a>': lambda e: self._select_all(self.text_left)
        }

        for shortcut, command in shortcuts.items():
            self.root.bind(shortcut, lambda e, cmd=command: cmd())

    # Event handlers and utility methods
    def _select_all(self, text_widget):
        """Select all text in the specified widget"""
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see(tk.INSERT)

    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About TidyBib",
            "TidyBib - Bibliography Manager\n\n"
            "A tool for cleaning and organizing BibTeX files.\n\n"
            "Copyright dongdonglin8@gmail.com"
        )

    def _show_context_menu(self, event, menu):
        """Show context menu"""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _schedule_highlight_syntax(self, event):
        """Schedule syntax highlighting with debouncing"""
        if self.highlight_timer:
            self.highlight_timer.cancel()
        self.highlight_timer = Timer(0.3, self._highlight_syntax)
        self.highlight_timer.start()

    def _highlight_syntax(self):
        """Apply syntax highlighting to text widgets"""
        for text_widget in [self.text_left, self.text_right]:
            self._clear_highlight_tags(text_widget)
            content = text_widget.get("1.0", tk.END)
            
            for tag_name, pattern in self.PATTERNS.items():
                for match in pattern.finditer(content):
                    start_pos = f"1.0+{match.start()}c"
                    end_pos = f"1.0+{match.end()}c"
                    text_widget.tag_add(tag_name, start_pos, end_pos)

    def _clear_highlight_tags(self, text_widget):
        """Clear all highlighting tags from text widget"""
        for tag_name in self.PATTERNS.keys():
            text_widget.tag_remove(tag_name, "1.0", tk.END)

    def _capitalize_title(self, title, is_booktitle=False):
        """Capitalize title according to bibliography standards"""
        if not title:
            return title

        # First apply organization corrections
        corrected_title = self._correct_organizations(title)

        def capitalize_word(word, is_first_word=False):
            # Skip words already in braces (protected)
            if word.startswith('{') and word.endswith('}'):
                return word
            
            # Check if word is a special word that should maintain specific capitalization
            if word in self.SPECIAL_WORDS or word.upper() in self.SPECIAL_WORDS:
                return word.upper()
            
            # Check if word is a preposition (should be lowercase except at beginning)
            if word.lower() in self.PREPOSITIONS and not is_booktitle and not is_first_word:
                return word.lower()
            
            # Default capitalization
            return word.capitalize()

        words = corrected_title.split()
        if not words:
            return corrected_title
        
        # Capitalize first word regardless of preposition rules
        capitalized_words = [capitalize_word(words[0], is_first_word=True)]
        
        # Process remaining words
        for word in words[1:]:
            capitalized_words.append(capitalize_word(word))
        
        return ' '.join(capitalized_words)

    def _correct_organizations(self, text):
        """Correct organization names and abbreviations"""
        if not text:
            return text
            
        corrected_text = text
        
        # Apply corrections (case-insensitive matching)
        for incorrect, correct in self.ORGANIZATION_CORRECTIONS.items():
            # Handle special cases with slashes or other non-word characters
            pattern = re.escape(incorrect)  # Escape special characters for exact matching
            corrected_text = re.sub(pattern, correct, corrected_text, flags=re.IGNORECASE)
        
        # Ensure IEEE/CVF is always uppercase
        corrected_text = re.sub(r'\bieee/cvf\b', 'IEEE/CVF', corrected_text, flags=re.IGNORECASE)
        
        return corrected_text

    def _get_journal_abbreviation(self, journal_name):
        """Get journal abbreviation from the loaded list"""
        if not journal_name or not self.journal_abbreviations:
            return None
            
        # Clean the journal name
        journal_clean = journal_name.strip()
        journal_lower = journal_clean.lower()
        
        # Try exact match (case-insensitive)
        if journal_lower in self.journal_abbreviations:
            return self.journal_abbreviations[journal_lower]
        
        # Try exact match without punctuation
        journal_no_punct = re.sub(r'[^\w\s]', '', journal_lower).strip()
        for full_name, abbrev in self.journal_abbreviations.items():
            full_name_no_punct = re.sub(r'[^\w\s]', '', full_name).strip()
            if journal_no_punct == full_name_no_punct:
                return abbrev
        
        # Try partial matches (journal name contains full name or vice versa)
        for full_name, abbrev in self.journal_abbreviations.items():
            # Check if the journal name contains the full name from dictionary
            if len(full_name) > 3 and full_name in journal_lower:
                return abbrev
            # Check if the full name from dictionary contains the journal name
            if len(journal_lower) > 3 and journal_lower in full_name:
                return abbrev
        
        # Try word-by-word matching for better accuracy
        journal_words = set(journal_lower.split())
        for full_name, abbrev in self.journal_abbreviations.items():
            full_name_words = set(full_name.split())
            # If most words match, consider it a match
            if len(journal_words & full_name_words) >= min(len(journal_words), len(full_name_words)) * 0.7:
                return abbrev
                
        return None

    def _process_journal_name(self, journal_name):
        """Process journal name based on user preferences"""
        if not journal_name:
            return journal_name
        
        if self.journal_format_var.get() == "abbreviated":
            # Use abbreviated form if available
            abbreviated = self._get_journal_abbreviation(journal_name)
            if abbreviated:
                # Apply organization corrections to the abbreviated form
                corrected_abbreviated = self._correct_organizations(abbreviated)
                # Add debug information
                self.output_message.insert(tk.END, f"📝 '{journal_name}' → '{corrected_abbreviated}'\n")
                return corrected_abbreviated
            else:
                # If no abbreviation found, apply organization corrections then capitalization
                corrected_name = self._correct_organizations(journal_name)
                capitalized_name = self._capitalize_title(corrected_name)
                self.output_message.insert(tk.END, f"⚠ No abbreviation found for: '{journal_name}'\n")
                return capitalized_name
        else:
            # Use full form - find full name from abbreviation first
            full_name = self._get_full_journal_name(journal_name)
            if full_name:
                # Apply organization corrections to the full name
                corrected_full_name = self._correct_organizations(full_name)
                return corrected_full_name
            else:
                # If no full name found, apply organization corrections then capitalization
                corrected_name = self._correct_organizations(journal_name)
                capitalized_name = self._capitalize_title(corrected_name)
                return capitalized_name

    def _get_full_journal_name(self, journal_name):
        """Get full journal name from abbreviation"""
        if not journal_name or not self.journal_abbreviations:
            return None
            
        journal_lower = journal_name.lower().strip()
        
        # Try to find by abbreviation (reverse lookup)
        for full_name, abbrev in self.journal_abbreviations.items():
            if abbrev.lower() == journal_lower:
                return self._capitalize_title(full_name)
                
        # Try partial matches with abbreviations
        for full_name, abbrev in self.journal_abbreviations.items():
            if journal_lower == abbrev.lower().strip('.'):
                return self._capitalize_title(full_name)
                
        return None

    # Main functionality methods
    def browse_file(self):
        """Browse and load BibTeX file"""
        file_path = filedialog.askopenfilename(
            title="Open BibTeX File",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            self.text_left.delete("1.0", tk.END)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_left.insert(tk.END, content)
                
                # Parse the content
                parser = bibtexparser.bparser.BibTexParser(common_strings=True)
                parser.customization = bibtexparser.customization.convert_to_unicode
                parser.homogenize_fields = False
                parser.ignore_nonstandard_types = False
                self.bib_database = bibtexparser.loads(content, parser=parser)
                
            self.output_message.insert(tk.END, f"✓ Loaded file: {file_path}\n")
            self._schedule_highlight_syntax(None)
            
        except Exception as e:
            error_msg = f"✗ Failed to load file: {file_path}\n  Error: {str(e)}\n"
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            self.output_message.insert(tk.END, error_msg)

    def save_file(self):
        """Save tidied BibTeX content to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save BibTeX File",
            defaultextension=".bib",
            filetypes=[("BibTeX files", "*.bib"), ("All files", "*.*")]
        )
        
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                content = self.text_right.get("1.0", tk.END)
                file.write(content)
            
            self.output_message.insert(tk.END, f"✓ Saved file: {file_path}\n")
            
        except Exception as e:
            error_msg = f"✗ Failed to save file: {file_path}\n  Error: {str(e)}\n"
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            self.output_message.insert(tk.END, error_msg)

    def tidy(self):
        """Process and tidy the BibTeX content"""
        try:
            content = self.text_left.get("1.0", tk.END).strip()
            if not content:
                self.output_message.insert(tk.END, "⚠ No content to process\n")
                return

            # Parse content
            parser = bibtexparser.bparser.BibTexParser(common_strings=True)
            parser.customization = bibtexparser.customization.convert_to_unicode
            parser.homogenize_fields = False
            parser.ignore_nonstandard_types = False
            self.bib_database = bibtexparser.loads(content, parser=parser)
            
            # Process and display results
            simplified_content = self._simplify_bib()
            self.text_right.delete("1.0", tk.END)
            self.text_right.insert(tk.END, simplified_content)
            
            self._display_processing_stats()
            self._schedule_highlight_syntax(None)
            
        except Exception as e:
            error_msg = f"✗ Failed to tidy content: {str(e)}\n"
            messagebox.showerror("Error", f"Failed to tidy content: {str(e)}")
            self.output_message.insert(tk.END, error_msg)

    def _simplify_bib(self):
        """Simplify and format bibliography entries"""
        if not self.bib_database or not self.bib_database.entries:
            return ""

        for entry in self.bib_database.entries:
            original_id = entry.get('ID', '')
            
            # Remove unwanted fields
            fields_to_remove = [field for field in entry.keys() if field not in self.fields]
            for field in fields_to_remove:
                del entry[field]
            
            # Process journal names with abbreviation support
            if 'journal' in entry:
                entry['journal'] = self._process_journal_name(entry['journal'])
            
            # Process other title fields
            other_title_fields = ['title', 'booktitle', 'publisher']
            for title_field in other_title_fields:
                if title_field in entry:
                    is_booktitle = (title_field == 'booktitle')
                    entry[title_field] = self._capitalize_title(entry[title_field], is_booktitle=is_booktitle)

            # Handle citation key modification
            if self.modify_citation_key_var.get() == "modify":
                entry['ID'] = self._generate_citation_key(entry)
            else:
                entry['ID'] = original_id

        return self._format_entries()

    def _generate_citation_key(self, entry):
        """Generate new citation key from entry data"""
        author = entry.get('author', '')
        year = entry.get('year', '')
        title = entry.get('title', '')
        
        author_part = re.sub(r'\W+', '', author.split()[0]) if author else 'Unknown'
        year_part = re.sub(r'\W+', '', year.split()[0]) if year else 'NoYear'
        title_part = ''.join([word[:2] for word in title.split()[:3]]) if title else 'NoTitle'
        
        return f"{author_part}:{year_part}:{title_part}"

    def _format_entries(self):
        """Format bibliography entries as BibTeX string"""
        if not self.bib_database or not self.bib_database.entries:
            return ""

        content_parts = []
        
        for entry in self.bib_database.entries:
            entry_type = entry.get('ENTRYTYPE', 'article')
            entry_id = entry.get('ID', 'unknown')
            
            entry_lines = [f"@{entry_type}{{{entry_id},"]
            
            # Add fields in specified order
            for field in self.FIELD_ORDER:
                if field in entry and entry[field]:
                    entry_lines.append(f"  {field:<12} = {{{entry[field]}}},")
            
            entry_lines.append("}")
            content_parts.append('\n'.join(entry_lines))
        
        return '\n\n'.join(content_parts) + '\n\n'

    def _display_processing_stats(self):
        """Display processing statistics"""
        if not self.bib_database or not self.bib_database.entries:
            self.output_message.insert(tk.END, "⚠ No entries found to process\n")
            return
        
        # Count statistics
        total_entries = len(self.bib_database.entries)
        entry_types = {}
        journal_conversions = 0
        
        for entry in self.bib_database.entries:
            entry_type = entry.get('ENTRYTYPE', 'unknown').lower()
            entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
            
            # Count journal conversions if in abbreviated mode
            if 'journal' in entry and self.journal_format_var.get() == "abbreviated":
                original_journal = entry['journal']
                if self._get_journal_abbreviation(original_journal):
                    journal_conversions += 1
        
        # Display results
        self.output_message.insert(tk.END, f"✓ Tidied {total_entries} entries successfully\n")
        
        if self.journal_format_var.get() == "abbreviated":
            self.output_message.insert(tk.END, f"📖 Journal abbreviations applied: {journal_conversions}\n")
        
        self.output_message.insert(tk.END, "📊 Entry types breakdown:\n")
        
        # Sort by count (descending)
        sorted_types = sorted(entry_types.items(), key=lambda x: x[1], reverse=True)
        
        for entry_type, count in sorted_types:
            self.output_message.insert(tk.END, f"   • {entry_type}: {count}\n")
        
        self.output_message.insert(tk.END, "─" * 50 + "\n")

    def clear_output(self):
        """Clear the output message area"""
        self.output_message.delete("1.0", tk.END)

    def show_find_dialog(self, event=None, widget=None):
        """Show find dialog"""
        if widget is None:
            widget = self.text_left if self.text_left.focus_get() == self.text_left else self.text_right
        
        # Close existing dialog
        if self.find_dialog:
            self.find_dialog.destroy()
        
        self.find_dialog = tk.Toplevel(self.root)
        self.find_dialog.title("Find Text")
        self.find_dialog.geometry("350x120")
        self.find_dialog.resizable(False, False)
        
        # Center the dialog
        self.find_dialog.transient(self.root)
        self.find_dialog.grab_set()
        
        # Create UI
        main_frame = ttk.Frame(self.find_dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Find:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.find_entry = ttk.Entry(main_frame, width=30)
        self.find_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.find_entry.focus_set()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Find All", command=lambda: self._find_text(widget)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=lambda: self._clear_find_highlights(widget)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.find_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.find_entry.bind('<Return>', lambda e: self._find_text(widget))

    def _find_text(self, widget):
        """Find and highlight text in widget"""
        search_term = self.find_entry.get().strip()
        if not search_term:
            return
        
        # Clear previous highlights
        widget.tag_remove('found', '1.0', tk.END)
        
        # Find all occurrences
        idx = '1.0'
        count = 0
        
        while True:
            idx = widget.search(search_term, idx, nocase=1, stopindex=tk.END)
            if not idx:
                break
            
            lastidx = f'{idx}+{len(search_term)}c'
            widget.tag_add('found', idx, lastidx)
            idx = lastidx
            count += 1
        
        # Show result
        if count > 0:
            widget.see('1.0')
            # Jump to first occurrence
            first_match = widget.search(search_term, '1.0', nocase=1, stopindex=tk.END)
            if first_match:
                widget.see(first_match)
                widget.mark_set(tk.INSERT, first_match)
        
        # Update status (you could add a status label if needed)
        status = f"Found {count} occurrence{'s' if count != 1 else ''}"
        self.output_message.insert(tk.END, f"🔍 {status} of '{search_term}'\n")

    def _clear_find_highlights(self, widget):
        """Clear find highlights from widget"""
        widget.tag_remove('found', '1.0', tk.END)

    def exit_app(self):
        """Exit the application"""
        if self.highlight_timer:
            self.highlight_timer.cancel()
        self.root.quit()


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = TidyBibApp(root)
    
    # Set minimum window size
    root.minsize(800, 600)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.exit_app()


if __name__ == "__main__":
    main()
