import argparse

def parses():
    # parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input bib file, default input all the bib files in the root path")
    parser.add_argument("-t", "--tidyid", choices=["yes", "no"], default="no", help="if this opt is yes, tidybib will generate an normative ID of each item")
    a = parser.parse_args()
    return a