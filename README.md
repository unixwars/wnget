# _wnget_: **w**eb **n**ovel **get**ter #

Rarely will web novel sites provide any means to read their contents
off line, and this is precisely why _wnget_ came to be. It is a tool
to scrape web novels from blogs, and optionally convert them to epub
format. It provides several options to configure the exact behaviour,
while at the same time trying to provide sane defaults. The strings
for the next/previous navigation links, as well as CSS class for
title/content containers can be configured, among other settings.


## Usage examples ##

To scrape all chapters of a given web novel, following links, and
saving each chapter in a diferent html file in the current directory:

```
$ wnget.py http://example.com/first_chapter_link
```

Or, for more advanced uses, downloading all chapters until a given
link is retrieved, and generate an EPUB with the loot:

```
$ wnget.py -e "My Web Novel" 'http://example.com/first_chapter_link  http://example.com/first_chapter_link
```

Adittionally, the *epub* module can be used as stand-alone command.
Just provide the HTML index file and a name for the book, and it will
generate an ebook with all referenced resources in the working
directory:

```
$ epub.py index.html "My Web Novel"
```

Also, if a cover.png or cover.jpg file is present, it will be used as
cover page. Its use as standalone command will often prove more
flexible, as it exposes features not normally used by the main
application, while allowing some manual tweaking of the downloaded
contents and index files.

Here, generating a book with unicode characters, relative paths, and
customized filename, cover image, and language/author metadata:

```
$ epub.py ../index.html "I Shall Seal the Heavens (我欲封天)" \
  --filename=issth.epub --language=zh --author="Ergen (耳根)" \
  --cover ~/images/MengHao.png
```
