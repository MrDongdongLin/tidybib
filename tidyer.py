import re


class Tidyer():
    def __init__(self):
        self.outputs = []

    def field_content(self, field, reg_field, reg_content, object_str):
        match_field = re.finditer(reg_field, object_str, re.MULTILINE | re.IGNORECASE)
        try:
            next_match = next(match_field).group()
            match_content = re.finditer(reg_content, next_match, re.MULTILINE | re.IGNORECASE)
            next_content = next(match_content).group()
            # remove extra blanks and enters
            _content = re.sub("\n+", "", next_content)
            content = re.sub(" +", " ", _content)
            if len(content) != 0:
                if content[0] == "{" and content[-1] == "}":
                    content = content
                    # content = content[:1] + content[1].upper() + content[2:]
                else:
                    content = "{" + content + "}"
                    # content = "{" + content[0].upper() + content[1:] + "}"
            else:
                content = "{}"
            
        except StopIteration:
            content = "{}"

        return content

    def tidy_title(self, title):
        match_str = re.finditer(r"{[^{}]+}", title, re.MULTILINE)
        title = title.capitalize()
        try:
            next_match = next(match_str).group()
            title = re.sub("{[^{}]+}", next_match, title)
        except StopIteration:
            title = title
        return title


    def tidy_journal(self, regex, str_journal, item, regs):
        journal_abbr = ""
        content = self.field_content(regex, str_journal, regs.outer_brace, item)
        inner_journal = re.finditer(regs.outer_brace, content)
        journal_name = next(inner_journal).group()
        journal_list = [i for i in journal_name.split()]
        for i, word in enumerate(journal_list):
            flag = True
            end = False
            if i == len(journal_list) - 1:
                end = True
            # TODO: simple process. not good!
            if word[0] == "(":
                if end:
                    journal_abbr = journal_abbr + word.upper()
                else:
                    journal_abbr = journal_abbr + word.upper() + " "
            else:
                for _, upper_word in enumerate(regs.uppercases):
                    if word.upper() == upper_word:
                        if end:
                            journal_abbr = journal_abbr + upper_word
                        else:
                            journal_abbr = journal_abbr + upper_word + " "
                        flag = False
                for _, lower_word in enumerate(regs.lowercases):
                    if word.lower() == lower_word:
                        if end:
                            journal_abbr = journal_abbr + lower_word
                        else:
                            journal_abbr = journal_abbr + lower_word + " "
                        flag = False
                if flag:
                    if end:
                        journal_abbr = journal_abbr + word.capitalize()
                    else:
                        journal_abbr = journal_abbr + word.capitalize() + " "
        journal_abbr = "{" + journal_abbr + "}"

        return journal_abbr


    def tidy_item(self, regex, object_str, fout, regs):
        # output_str = [] # TODO: we can buffer the tidy item and write them out afterwards
        matches = re.finditer(regex["item"], object_str, re.MULTILINE | re.IGNORECASE)

        counter = 0
        while True:
            try:
                match = next(matches)
                item = match.group()
                id_head = ""

                # extract head from author, title and year, e.g. Lin:ISEA:2017
                for key, value in regex.items():
                    if key == "author":
                        author_content = self.field_content(key, value, regs.outer_brace, item)
                        first_author = re.finditer(regs.head_author, author_content)
                        first_author_name = next(first_author).group()
                        id_head = id_head + first_author_name
                    if key == "title":
                        contraction_title = ""
                        title_content = self.field_content(key, value, regs.outer_brace, item)
                        inner_title = re.finditer(regs.outer_brace, title_content)
                        innertitle = next(inner_title).group()
                        first_characters = [i[0] for i in innertitle.split()]
                        if len(first_characters) >= 5:
                            for i in range(5):
                                contraction_title = contraction_title + first_characters[i]
                        else:
                            for i in range(len(first_characters)):
                                contraction_title = contraction_title + first_characters[i]
                        id_head = id_head + ":" + contraction_title
                    if key == "year":
                        year_content = self.field_content(key, value, regs.outer_brace, item)
                        first_year = re.finditer(regs.inner_year, year_content)
                        inneryear = next(first_year).group()
                        id_head = id_head + ":" + inneryear
                # write file
                for key, value in regex.items():
                    if key == "item" or len(value)==0:
                        continue
                    elif key == "head":
                        content = re.finditer(value, item, re.MULTILINE | re.IGNORECASE)
                        head_content = next(content).group()
                        new_head = re.sub(" +", "", head_content)
                        new_head = new_head + '\n'
                        fout.append(new_head)
                    else:
                        if key == "journal" or key == "booktitle":
                            journal_abbr = self.tidy_journal(key, value, item, regs)
                            new_journal_abbr = "  {:<14} {},\n".format(key + " =", journal_abbr)
                            fout.append(new_journal_abbr)
                            # fout.write("  {:<14} {},\n".format(key + " =", journal_abbr))
                        elif key == "title":
                            content = self.field_content(key, value, regs.outer_brace, item)
                            content = content[0] + content[1].upper() + content[2:]
                            content = content[1:-1]
                            content = "{" + self.tidy_title(content) + "}"
                            new_content = "  {:<14} {},\n".format(key + " =", content)
                            fout.append(new_content)
                            # fout.write("  {:<14} {},\n".format(key + " =", content))
                        else:
                            content = self.field_content(key, value, regs.outer_brace, item)
                            if content == "{}":
                                continue
                            else:
                                new_content = "  {:<14} {},\n".format(key + " =", content)
                                fout.append(new_content)
                                # fout.write("  {:<14} {},\n".format(key + " =", content))
                fout.append("}\n\n")
                # fout.write("}\n\n")
                counter += 1
            except StopIteration:
                break
        return counter


    def tidyer(self, regs, bibin):

        if bibin[-1] != "%":
            try:
                bibin = bibin + "%"
            except:
                print("Format ERROR: cannot add end mark! Please add '%' in the end of the bib file manually!")
        comments_matches = re.finditer(regs.comments, bibin, re.MULTILINE | re.IGNORECASE)
        abbr_matches = re.finditer(regs.abbr, bibin, re.MULTILINE | re.IGNORECASE)

        # write tidy bib file
        # global outputs
        # outputs = []
        for matchNum, match in enumerate(abbr_matches, start=1):
            item = match.group()
            abbr = re.sub("\n+", "", item)
            abbr = re.sub(" +", " ", abbr)
            new_abbr = abbr + '\n'
            if abbr == '':
                self.outputs.append(abbr)
            else:
                self.outputs.append(new_abbr)
        # outputs.append("\n")

        # set a counter for processed items
        count = 0

        numInproceed = self.tidy_item(regs.inproceedings_regex, bibin, self.outputs, regs)
        numProceed = self.tidy_item(regs.proceedings_regex, bibin, self.outputs, regs)
        numMisc = self.tidy_item(regs.misc_regex, bibin, self.outputs, regs)
        numBook = self.tidy_item(regs.book_regex, bibin, self.outputs, regs)
        numArticle = self.tidy_item(regs.article_regex, bibin, self.outputs, regs)
        numIncollection = self.tidy_item(regs.incollection_regex, bibin, self.outputs, regs)

        count = numInproceed + numProceed + numMisc + numBook + numArticle + numIncollection

        return self.outputs, {'total': count, 
                'inproc': numInproceed, 
                'proc': numProceed, 
                'misc': numMisc, 
                'book': numBook,
                'article': numArticle,
                'incollect': numIncollection}