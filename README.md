# version 1.0 beta
author: Donny
email:  dongdonglin8@gmail.com

## Introduction
tidy bib

Items need to process:
1. "% -----"
2. "@string{-----}" ignore case
3. "@inproceedings{-----}" ignore case
4. "@misc{-----} ignore case
5. "@article{{-----}" ignore case
6. "@book{-----}" ignore case

## Usage
```python
python tidybib.py --input yourfile.bib --output outpath.bib
```

enter `python tidybib.py -h` for help