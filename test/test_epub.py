import os
import subprocess
import tempfile
import lxml.html

from wnget.epub import create_epub
from wnget.container import Chapter


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
