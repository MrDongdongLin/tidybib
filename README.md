# Tidy bib, the art of typesetting

- author: Donny
- email:  dongdonglin8@gmail.com

## Introduction

"Donald E. Knuth became so frustrated with the inability of the latter system to approach the quality 
of the previous volumes, which were typeset using the older system, that he took time out to work on 
digital typesetting and created TeX and Metafont." ---wiki

Knuth creates TeX for easy and simple typesetting, so a complex tex file is intolerable.

There are many databases that provide comprehensive citation data, such as Web of Science, IEEE. There
are also different formats of bib file from different database. They are often difficult to read. Therefore `Tidybib` is developed to tidy the bib files into a standardize style.

The bib items before processing:

```tex
@inproceedings{ WOS:000766209400010,
Author = {Li, Yue and Abady, Lydia and Wang, Hongxia and Barni, Mauro},
Editor = {Zhao, X and Piva, A and ComesanaAlfaro, P},
Title = {A Feature-Map-Based Large-Payload DNN Watermarking Algorithm},
Booktitle = {DIGITAL FORENSICS AND WATERMARKING, IWDW 2021},
Series = {Lecture Notes in Computer Science},
Year = {2022},
Volume = {13180},
Pages = {135-148},
Note = {20th International Workshop on Digital-Forensics and Watermarking
   (IWDW), Beijing, PEOPLES R CHINA, NOV 20-22, 2021},
Organization = {Chinese Acad Sci, Inst Informat Engn, State Key Lab Informat Secur; New
   Jersey Institute of Technology; Springer},
DOI = {10.1007/978-3-030-95398-0\_10},
ISSN = {0302-9743},
EISSN = {1611-3349},
ISBN = {978-3-030-95398-0; 978-3-030-95397-3},
Unique-ID = {WOS:000766209400010},
}
```

After processing:

```tex
@inproceedings{WOS:000766209400010,
  author =       {Li, Yue and Abady, Lydia and Wang, Hongxia and Barni, Mauro},
  title =        {A feature-map-based large-payload dnn watermarking algorithm},
  booktitle =    {Digital Forensics and Watermarking, Iwdw 2021},
  year =         {2022},
  editor =       {Zhao, X and Piva, A and ComesanaAlfaro, P},
  volume =       {13180},
  series =       {Lecture Notes in Computer Science},
  pages =        {135-148},
  doi =          {10.1007/978-3-030-95398-0\_10},
}
```

## Download

https://github.com/MrDongdongLin/tidybib/releases

## 