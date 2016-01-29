wnget: the WebNovel getter
=================================

This is a tool to scrape web novels from blogs, and optionally convert
them to EPUBs.  It has a few configuration options, but tries to set
sane defaults. The strings for the next/previous navigation links, as
well as CSS class for title/content containers can be configured,
among other settings.

Usage example:

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
directory.

```
$ epub.py index.html "My Web Novel"
```

Also, if a cover.png or cover.jpg file is present, it will be used as
cover page.
