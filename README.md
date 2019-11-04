# Tidy bib, the art of typesetting
- author: Donny
- email:  dongdonglin8@gmail.com

## Introduction
"Donald E. Knuth became so frustrated with the inability of the latter system to approach the quality 
of the previous volumes, which were typeset using the older system, that he took time out to work on 
digital typesetting and created $\TeX$ and Metafont." ---wiki

Knuth creates $\TeX$ for easy and simple typesetting, so a complex tex file is intolerable.

There are many databases that provide comprehensive citation data, such as Web of Science, IEEE. There
are also different formats of bib file from different database. They are often difficult to read. So I
develop the tool `tidybib` to get a tidy bib files.

Items need to process:
1. "% -----"
2. "@string{-----}" ignore case
3. "@inproceedings{-----}" ignore case
4. "@proceedings{-----}" ignore case
5. "@misc{-----} ignore case
6. "@article{{-----}" ignore case
7. "@book{-----}" ignore case

## TODO list
- More items need to be added: `@inbook`, `@collection`, `@booklet`, `@manual`, `@report`, `@conference`, 
`@phdthesis`, `@masterthesis`, `@unpublished`;
- Fileds in each item should be improved. For example, redundant braces should be removed, e.g. `title = {{Test title: {IEEE}}}`
should be `title = {Test title: {IEEE}}`;
- The first character of the field `month` should be upcese, e.g. `Nov` or `May`.
- In the field of `author`, the last name should after the first name, e.g. `Donny Lin`, not `Lin, Donny`.

## Usage
put your bib file in `bibfile`, execute `python tidybib.py` to get tidy bib files in folder `tidybib`,
or

```python
python tidybib.py -i yourfile.bib -o outpath.bib
```

enter `python tidybib.py -h` for help