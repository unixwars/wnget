import os
import uuid

from ebooklib import epub
from .utils import safe_decode

"""
Epub creation module.
"""

SRC_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SRC_PATH, "data")
NAV_CSS = os.path.join(DATA_PATH, 'nav.css')
COVER_PNG = 'cover.png'
COVER_JPG = 'cover.jpg'


def create_epub(ebook_title, chapter_iter, ebook_filename=None,
                language='en', author=None, cover_image=None):
    book = epub.EpubBook()

    # add metadata
    book.set_identifier(uuid.uuid1().urn)
    book.set_title(safe_decode(ebook_title))
    book.set_language(safe_decode(language))
    if author:
        book.add_author(safe_decode(author))

    cover_image = cover_image or find_cover()
    if cover_image:
        cover_fname = os.path.basename(cover_image)
        book.set_cover(cover_fname, open(cover_image, 'rb').read())

    # chapters
    epub_chapters = []
    for c in chapter_iter:
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

    ebook_filename = ebook_filename or ebook_title.replace(' ', '-')
    ebook_filename = ebook_filename.rstrip('.epub') + '.epub'
    epub.write_epub(ebook_filename, book, {})


def find_cover():
    if os.path.isfile(COVER_PNG):
        return COVER_PNG
    if os.path.isfile(COVER_JPG):
        return COVER_JPG
    return None
