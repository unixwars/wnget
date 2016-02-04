"""
Contains main functions of console scripts
"""
import os
import optparse
import lxml.html

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
    p = optparse.OptionParser(
        usage="Usage: %prog [options] first_url [last_url]",
        version="wnget version %s" % __version__)

    p.add_option(
        '--keeplinks', '-k',
        action="store_true",
        default=False,
        dest="navlinks",
        help="Rewrite and keep navigation links in HTML content.")

    p.add_option(
        '--firsttitle', '-f',
        action="store_true",
        default=False,
        dest="firsttitle",
        help="Keep first title match instead of trying to be smart about it")

    p.add_option(
        '--next', '-n',
        default=crawl.NEXT_STR,
        dest="next_str",
        help='Specify next link caption. Default: "%s"' % crawl.NEXT_STR)

    p.add_option(
        '--previous', '-p',
        default=crawl.PREV_STR,
        dest="prev_str",
        help='Specify previous link caption. Default: "%s"' % crawl.PREV_STR)

    p.add_option(
        '--titleclass', '-t',
        default=crawl.T_CLASS,
        dest="title_class",
        help="Specify title container class. Default: %s." % crawl.T_CLASS)

    p.add_option(
        '--contentclass', '-c',
        default=crawl.C_CLASS,
        dest="content_class",
        help="Specify content container class. Default: %s." % crawl.C_CLASS)

    p.add_option(
        '--epub', '-e',
        default=None,
        dest="epub_title",
        help="Create Epub with this title. Will use cover.jpg/png if found.")

    p.add_option(
        '--limit', '-l',
        default=0,
        type="int",
        dest="limit",
        help="Crawl at most N pages.")

    opts, args = p.parse_args()

    first_url, last_url = None, None
    if len(args) == 2:
        first_url, last_url = args[0], args[1]
    elif len(args) == 1:
        first_url = args[0]
    else:
        p.error("Incorrect number of arguments. Provide 1 or 2 URLs!")

    crawler = crawl.Crawler(opts.next_str, opts.prev_str,
                            opts.title_class, opts.content_class)

    chapts = crawler.crawl(first_url, last_url, opts.navlinks,
                           not opts.firsttitle, opts.limit)

    container.Index(chapts).write()
    if opts.epub_title:
        epub.create_epub(opts.epub_title, chapts)


@ctrl_c_wrapper
def wnbook():
    p = optparse.OptionParser(
        usage="Usage: %prog [options] <index.html> <book title>",
        version="wnget version %s" % __version__)

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

    index_file, title = args[0], args[1]
    index = container.Index(filename=index_file)
    epub.create_epub(title, index.chapters, opts.ebook_filename,
                     opts.language, opts.author, opts.cover_image)


@ctrl_c_wrapper
def wnlocal():
    p = optparse.OptionParser(
        usage="Usage: %prog <input_file.html> [output_file.html]",
        version="wnget version %s" % __version__)

    opts, args = p.parse_args()
    if len(args) < 1:
        p.error("At least an input file must be specified. ")

    filename = args[0]
    dirname = os.path.dirname(os.path.abspath(filename))

    tree = lxml.html.parse(filename)
    links = tree.xpath('//a')
    for link in links:
        in_link = link.get('href')
        out_link = href_to_local(in_link, dirname)
        if not (in_link and out_link):
            continue
        link.set('href', out_link)

    if len(args) > 1:
        return tree.write(
            args[1], encoding='utf-8', method='html', pretty_print=True)
    else:
        print(lxml.etree.tostring(
            tree, encoding='utf-8', method='html', pretty_print=True))
