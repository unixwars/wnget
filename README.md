# _wnget_: **w**eb **n**ovel **get**ter #

Rarely will web novel sites provide any means to read their contents
off line, and this is precisely why _wnget_ came to be. It is a tool
to scrape web novels from blogs, and optionally convert them to epub
format. It provides several options to configure the exact behaviour,
while at the same time trying to provide sane defaults. The strings
for the next/previous navigation links, as well as CSS class for
title/content containers can be configured, among other settings.

##Installation##

```
$ pip install wnget
```

If you happened to have cloned the repo and are playing with the code,
in which case you probably want to install _wnget_ in "editable" mode
while you’re working on it. This is so it becomes both installed and
editable in project form.

Assuming you’re in the root of the project, just run:

```
$ pip install -e .
```

## Usage examples ##

To scrape all chapters of a given web novel, following links, and
saving each chapter in a diferent html file in the current directory:

```
$ wnget http://example.com/first_chapter_link
```

Or, for more advanced uses, downloading all chapters until a given
link is retrieved, and generate an EPUB with the loot:

```
$ wnget -e "My Web Novel" \
  http://example.com/first_chapter_link  \
  http://example.com/first_chapter_link
```

Adittionally, the ebook functionality can be used directly through the
_wnbook_ standalone utility.  Just provide the HTML index file and a
name for the book, and it will generate an ebook with all referenced
resources in the working directory:

```
$ wnbook index.html "My Web Novel"
```

Also, if a cover.png or cover.jpg file is present, it will be used as
cover page. Its use as standalone command will often prove more
flexible, as it exposes features not normally used by the main
application, while allowing some manual tweaking of the downloaded
contents and index files.

Here, generating a book with relative paths, and custom filename,
cover image, and language/author metadata:

```
$ wnbook ../index.html "I Shall Seal the Heavens (我欲封天)" \
  --filename=issth.epub --language=zh --author="Ergen (耳根)" \
  --cover ~/images/MengHao.png
```
