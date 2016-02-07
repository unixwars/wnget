"""
Contains main functions of console scripts
"""
import os
import lxml.html
import configargparse

from . import crawl
from . import container
from . import epub
from . import __version__
from .utils import href_to_local


def ctrl_c_wrapper(func):
    def wrap():
        try:
            return func()
        except KeyboardInterrupt:
            print('Exiting...')
    return wrap


@ctrl_c_wrapper
def wnget():
    cfg_files = ['./wnget.conf', '~/.wnget.conf', '/etc/wnget.conf']
    p = configargparse.ArgParser(default_config_files=cfg_files)

    p.add_argument('first_url', help='first URL to crawl')
    p.add_argument(
        'last_url',
        nargs='?',
        help='optional last URL to crawl (stops after reaching)')

    p.add_argument(
        '-s', '--settings',
        is_config_file=True,
        help='file path of config file')

    p.add_argument(
        '-k', '--keeplinks',
        action="store_true",
        default=False,
        dest="keeplinks",
        help="rewrite and keep navigation links in HTML content")

    p.add_argument(
        '-f', '--firsttitle',
        action="store_false",
        default=True,
        dest="smart_titles",
        help="keep first title match instead of trying to be smart about it")

    p.add_argument(
        '-n', '--next',
        default=crawl.NEXT_STR,
        dest="next_str",
        help="specify next link caption (default: '%s')" % crawl.NEXT_STR)

    p.add_argument(
        '-p', '--previous',
        default=crawl.PREV_STR,
        dest="prev_str",
        help="specify previous link caption (default: '%s')" % crawl.PREV_STR)

    p.add_argument(
        '-t', '--titleclass',
        default=crawl.T_CLASS,
        dest="title_class",
        help="specify title container class (default: '%s')" % crawl.T_CLASS)

    p.add_argument(
        '-c', '--contentclass',
        default=crawl.C_CLASS,
        dest="content_class",
        help="specify content container class (default: '%s')" % crawl.C_CLASS)

    p.add_argument(
        '-e', '--epub',
        default=None,
        dest="epub_title",
        help="create Epub with this title (will use cover.jpg/png if found)")

    p.add_argument(
        '-l', '--limit',
        default=0,
        type=int,
        dest="limit",
        help="crawl at most N pages")

    p.add_argument('-v', '--version', action='version', version=__version__)
    opts = p.parse_args()

    crawler = crawl.Crawler(opts.next_str, opts.prev_str,
                            opts.title_class, opts.content_class,
                            opts.keeplinks, opts.smart_titles)

    chapts = crawler.crawl(opts.first_url, opts.last_url, opts.limit)

    container.Index(chapts).write()
    if opts.epub_title:
        epub.create_epub(opts.epub_title, chapts)


@ctrl_c_wrapper
def wnbook():
    p = configargparse.ArgParser()
    p.add_argument('index_file', help='index.html file.')
    p.add_argument('book_title', help='Book title.')

    p.add_argument(
        '--filename', '-f',
        default=None,
        dest="ebook_filename",
        help="specify fileanme (works out something from title by default)")

    p.add_argument(
        '--language', '-l',
        default='en',
        dest="language",
        help="specify language for ebook metadata")

    p.add_argument(
        '--author', '-a',
        default=None,
        dest="author",
        help="specify author for ebook metadata")

    p.add_argument(
        '--cover', '-c',
        default=None,
        dest="cover_image",
        help="specify cover image (uses cover.jpg/png by default if found)")

    p.add_argument('-v', '--version', action='version', version=__version__)
    opts = p.parse_args()

    index = container.Index(filename=opts.index_file)
    epub.create_epub(opts.book_title, index.chapters, opts.ebook_filename,
                     opts.language, opts.author, opts.cover_image)


@ctrl_c_wrapper
def wnlocal():
    p = configargparse.ArgParser()
    p.add_argument('input_file', help='Input html file.')
    p.add_argument(
        'output_file',
        help='output file (defaults to stdout)',
        nargs='?')

    p.add_argument('-v', '--version', action='version', version=__version__)
    opts = p.parse_args()

    dirname = os.path.dirname(os.path.abspath(opts.input_file))

    tree = lxml.html.parse(opts.input_file)
    links = tree.xpath('//a')
    for link in links:
        in_link = link.get('href')
        out_link = href_to_local(in_link, dirname)
        if not (in_link and out_link):
            continue
        link.set('href', out_link)

    def prn(*args, **kwargs):
        print(lxml.etree.tostring(*args, **kwargs))

    arg, fn = tree, prn
    if opts.output_file:
        arg, fn = opts.output_file, tree.write

    return fn(arg, encoding='utf-8', method='html', pretty_print=True)
