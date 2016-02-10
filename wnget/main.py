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
from .utils import href_to_local, get_site_defaults


def ctrl_c_wrapper(func):
    def wrap():
        try:
            return func()
        except KeyboardInterrupt:
            print('Exiting...')
    return wrap


@ctrl_c_wrapper
def wnget():
    # Disposable preparser, just used to obtain site specific defaults
    preparser = configargparse.ArgumentParser(add_help=False)
    preparser.add_argument('url', help=configargparse.SUPPRESS)
    url = None
    try:
        opts, _ = preparser.parse_known_args()
        url = opts.url
    except SystemExit:
        pass
    d = get_site_defaults(url)

    p = configargparse.ArgParser(
        default_config_files=('./wnget.conf', '~/.wnget.conf'),
        add_config_file_help=False)

    p.add_argument('first_url', help='first URL to crawl')

    p.add_argument(
        'last_url',
        nargs='?',
        help='optional last URL to crawl (stops after reaching)')

    p.add_argument(
        '-s', '--settings',
        metavar='file',
        is_config_file=True,
        help='config file path')

    p.add_argument(
        '-k', '--keeplinks',
        action="store_true",
        default=d['keeplinks'],
        dest="keeplinks",
        help="rewrite and keep navigation links in HTML content")

    p.add_argument(
        '-f', '--firsttitle',
        action="store_false",
        default=d['firsttitle'],
        dest="smart_titles",
        help="keep first title match instead of trying to be smart about it")

    p.add_argument(
        '-n', '--next',
        default=d['next'],
        metavar='caption',
        dest="next_str",
        help="next link caption (default: '%s')" % d['next'])

    p.add_argument(
        '-p', '--previous',
        default=d['previous'],
        metavar='caption',
        dest="prev_str",
        help="previous link caption (default: '%s')" % d['previous'])

    p.add_argument(
        '-t', '--titleclass',
        default=d['titleclass'],
        metavar='css_class',
        dest="title_class",
        help="title container class (default: '%s')" % d['titleclass'])

    p.add_argument(
        '-c', '--contentclass',
        default=d['contentclass'],
        metavar='css_class',
        dest="content_class",
        help="content container class (default: '%s')" % d['contentclass'])

    p.add_argument(
        '-e', '--epub',
        default=None,
        metavar='title',
        dest="epub_title",
        help="create Epub with this title (will use cover.jpg/png if found)")

    p.add_argument(
        '-l', '--limit',
        default=d['limit'],
        type=int,
        metavar='N',
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
