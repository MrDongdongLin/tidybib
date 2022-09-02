import re


def field_content(reg_field, reg_content, object_str):
    match_field = re.finditer(reg_field, object_str, re.MULTILINE | re.IGNORECASE)
    try:
        next_match = next(match_field).group()
        match_content = re.finditer(reg_content, next_match, re.MULTILINE | re.IGNORECASE)
        next_content = next(match_content).group()
        # remove extra blanks and enters
        _content = re.sub("\n+", "", next_content)
        content = re.sub(" +", " ", _content)
        if len(content) != 0:
            content = content if content[0] == "{" and content[-1] == "}" else "{" + content + "}"
        else:
            content = "{}"

    except StopIteration:
        content = "{}"

    return content


def tidy_title(title):
    match_str = re.finditer(r"{[^{}]+}", title, re.MULTILINE)
    title = title.capitalize()
    try:
        next_match = next(match_str).group()
        title = re.sub("{[^{}]+}", next_match, title)
    except StopIteration:
        title = title
    return title


def tidy_journal(str_journal, item, regs):
    journal_abbr = ""
    content = field_content(str_journal, regs.outer_brace, item)
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
            journal_abbr += word.upper() if end else word.upper() + ' '
        else:
            for _, upper_word in enumerate(regs.uppercases):
                if word.upper() == upper_word:
                    journal_abbr += word.upper() if end else word.upper() + ' '
                    flag = False
            for _, lower_word in enumerate(regs.lowercases):
                if word.lower() == lower_word:
                    journal_abbr += lower_word if end else lower_word + ' '
                    flag = False
            if flag:
                journal_abbr += word.capitalize() if end else word.capitalize() + ' '
    journal_abbr = "{" + journal_abbr + "}"

    return journal_abbr


class Tidyer():
    def __init__(self, indent):
        self.outputs = []
        self.indent = indent  # 'space'
        self.spaces = 2

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
                        author_content = field_content(value, regs.outer_brace, item)
                        first_author = re.finditer(regs.head_author, author_content)
                        first_author_name = next(first_author).group()
                        id_head = id_head + first_author_name
                    if key == "title":
                        contraction_title = ""
                        title_content = field_content(value, regs.outer_brace, item)
                        inner_title = re.finditer(regs.outer_brace, title_content)
                        innertitle = next(inner_title).group()
                        first_characters = [i[0] if str.isalpha(i[0]) else i[1] for i in innertitle.split()]
                        if len(first_characters) >= 5:
                            for i in range(5):
                                contraction_title = contraction_title + first_characters[i]
                        else:
                            for i in range(len(first_characters)):
                                contraction_title = contraction_title + first_characters[i]
                        id_head = id_head + ":" + contraction_title
                    if key == "year":
                        year_content = field_content(value, regs.outer_brace, item)
                        first_year = re.finditer(regs.inner_year, year_content)
                        inneryear = next(first_year).group()
                        id_head = id_head + ":" + inneryear
                # write file
                for key, value in regex.items():
                    if key == "item" or len(value) == 0:
                        continue
                    elif key == "head":
                        content = re.finditer(value, item, re.MULTILINE | re.IGNORECASE)
                        head_content = next(content).group()
                        head_content = head_content + id_head + "," if regs.tidyid else head_content
                        new_head = re.sub(" +", "", head_content)
                        new_head = new_head + '\n'
                        fout.append(new_head)
                    else:
                        if key == "journal" or key == "booktitle":
                            journal_abbr = tidy_journal(value, item, regs)
                            if self.indent == 'space':
                                new_journal_abbr = "{e:<{size}}{k:<14} {c},\n".format(e=' ', size=self.spaces,
                                                                                      k=key + ' =', c=journal_abbr)
                            elif self.indent == 'tab':
                                new_journal_abbr = "{e:<{size}}{k:<14} {c},\n".format(e='\t', size=1, k=key + ' =',
                                                                                      c=journal_abbr)
                            fout.append(new_journal_abbr)
                            # fout.write("  {:<14} {},\n".format(key + " =", journal_abbr))
                        elif key == "title":
                            content = field_content(value, regs.outer_brace, item)
                            # content = content[0] + content[1].upper() + content[2:]
                            # content = content[1:-1]
                            # content = "{" + self.tidy_title(content) + "}"
                            if self.indent == 'space':
                                new_content = "{e:<{size}}{k:<14} {c},\n".format(e=' ', size=self.spaces, k=key + ' =',
                                                                                 c=content)
                            elif self.indent == 'tab':
                                new_content = "{e:<{size}}{k:<14} {c},\n".format(e='\t', size=1, k=key + ' =',
                                                                                 c=content)
                            fout.append(new_content)
                            # fout.write("  {:<14} {},\n".format(key + " =", content))
                        else:
                            content = field_content(value, regs.outer_brace, item)
                            if content == "{}":
                                continue
                            else:
                                if self.indent == 'space':
                                    new_content = "{e:<{size}}{k:<14} {c},\n".format(e=' ', size=self.spaces,
                                                                                     k=key + ' =', c=content)
                                elif self.indent == 'tab':
                                    new_content = "{e:<{size}}{k:<14} {c},\n".format(e='\t', size=1, k=key + ' =',
                                                                                     c=content)
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
        self.outputs = []
        for _, match in enumerate(abbr_matches, start=1):
            item = match.group()
            abbr = re.sub("\n+", "", item)
            abbr = re.sub(" +", " ", abbr)
            new_abbr = abbr + '\n'
            if abbr == '':
                self.outputs.append(abbr)
            else:
                self.outputs.append(new_abbr)

        num_inproc = self.tidy_item(regs.inproceedings_regex, bibin, self.outputs, regs)
        num_proc = self.tidy_item(regs.proceedings_regex, bibin, self.outputs, regs)
        num_misc = self.tidy_item(regs.misc_regex, bibin, self.outputs, regs)
        num_book = self.tidy_item(regs.book_regex, bibin, self.outputs, regs)
        num_article = self.tidy_item(regs.article_regex, bibin, self.outputs, regs)
        num_incollec = self.tidy_item(regs.incollection_regex, bibin, self.outputs, regs)

        count = num_inproc + num_proc + num_misc + num_book + num_article + num_incollec

        return self.outputs, {'total': count,
                              'inproc': num_inproc,
                              'proc': num_proc,
                              'misc': num_misc,
                              'book': num_book,
                              'article': num_article,
                              'incollect': num_incollec}
