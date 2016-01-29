#!/usr/bin/env python

import os
import uuid
import subprocess
import tempfile
import lxml.html
import optparse

from ebooklib import epub
from container import Chapter, Index

"""
Epub creation module. Can be used as standalone if desired.
"""

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SRC_PATH, "templates")
NAV_CSS = os.path.join(TEMPLATE_PATH, 'nav.css')
COVER_PNG = 'cover.png'
COVER_JPG = 'cover.jpg'


def create_epub(ebook_title, chapter_list, ebook_filename=None,
                language='en', author=None, cover_image=None):
    assert all(map(lambda x: isinstance(x, Chapter), chapter_list))
    book = epub.EpubBook()

    # add metadata
    book.set_identifier(uuid.uuid1().urn)
    book.set_title(ebook_title.decode('utf8'))
    book.set_language(language.decode('utf8'))
    if author:
        book.add_author(author.decode('utf8'))

    if cover_image is None:
        cover_image = find_cover()

    if cover_image:
        cover_fname = os.path.basename(cover_image)
        book.set_cover(cover_fname, open(cover_image, 'rb').read())

    # chapters
    epub_chapters = []
    for c in chapter_list:
        chapt = epub.EpubHtml(title=c.title,
                              file_name=c.xhtml_filename,
                              content=c.html, lang=language,
                              media_type="application/xhtml+xml")
        book.add_item(chapt)
        epub_chapters.append(chapt)

    # navigation & css style
    book.toc = epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    style = open(NAV_CSS).read()
    nav_css = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css",
        media_type="text/css", content=style)
    book.add_item(nav_css)
    book.spine = ['nav'] + epub_chapters

    if ebook_filename is None:
        ebook_filename = ebook_title.replace(' ', '-')
        ebook_filename += '' if ebook_filename.endswith('.epub') else '.epub'
    epub.write_epub(ebook_filename, book, {})


def test_create_epub():
    "Test only runs/works/fails if epubcheck present"

    try:
        f, bookfile = tempfile.mkstemp(suffix='.epub', dir='/tmp')
        test_chapter = Chapter(
            filename='chapter.html',
            title='title',
            tree=lxml.html.fromstring('chapter'),
            url='http://example.com/novel-chapter-1')
        create_epub('test', [test_chapter], bookfile)
        rc = subprocess.call(["epubcheck", bookfile])
        os.unlink(bookfile)
        assert rc == 0  # No errors
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return  # handle file not found error.
        else:
            raise  # Something else


def find_cover():
    if os.path.isfile(COVER_PNG):
        return COVER_PNG
    if os.path.isfile(COVER_JPG):
        return COVER_JPG
    return None


def load_chapters(index_file):
    chapters = []
    index = Index(filename=index_file)
    for link in index.links:
        fname = link.get('href')
        c = Chapter.from_file(fname, link.text)
        chapters.append(c)
    return chapters


def main():
    p = optparse.OptionParser(
        usage="Usage: %prog [options] <index.html> <book title>")

    p.add_option(
        '--filename', '-f',
        default=None,
        dest="ebook_filename",
        help="Specify fileanme. Works out something from title by default")

    p.add_option(
        '--language', '-l',
        default='en',
        dest="language",
        help="Specify language for ebook metadata")

    p.add_option(
        '--author', '-a',
        default=None,
        dest="author",
        help="Specify author for ebook metadata")

    p.add_option(
        '--cover', '-c',
        default=None,
        dest="cover_image",
        help="Specify cover image. Uses cover.jpg/png by default if found.")

    opts, args = p.parse_args()
    if len(args) != 2:
        p.error("Index file and ebook title are mandatory!")

    index, title = args[0], args[1]
    chapter_list = load_chapters(index)
    create_epub(title, chapter_list, opts.ebook_filename,
                opts.language, opts.author, opts.cover_image)

if __name__ == '__main__':
    main()
