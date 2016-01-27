import os
import uuid
import subprocess
import tempfile

from ebooklib import epub
import chapter


SRC_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SRC_PATH, "templates")
NAV_CSS = os.path.join(TEMPLATE_PATH, 'nav.css')


def create_epub(ebook_title, chapter_list, ebook_filename=None,
                language='en', author=None, cover_image=None):
    assert all(map(lambda x: isinstance(x, chapter.Chapter), chapter_list))
    book = epub.EpubBook()

    # add metadata
    book.set_identifier(uuid.uuid1().urn)
    book.set_title(ebook_title)
    book.set_language(language)
    if author:
        book.add_author(author)
    if cover_image:
        cover_fname = os.path.basename(cover_image)
        book.set_cover(cover_fname, open(cover_image, 'rb').read())

    # chapters
    epub_chapters = []
    for c in chapter_list:
        chapt = epub.EpubHtml(title=c.title, file_name=c.xhtml_filename,
                              content=c.html, lang=language)
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
        test_chapter = chapter.Chapter(
            'title',
            '<html><head></head><body>content</body></html>',
            '/test/test-chapter')
        create_epub('test', [test_chapter], bookfile)
        rc = subprocess.call(["epubcheck", bookfile])
        os.unlink(bookfile)
        assert rc == 0  # No errors
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return  # handle file not found error.
        else:
            raise  # Something else


if __name__ == '__main__':
    test_create_epub()
