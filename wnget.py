#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import optparse

import crawl
import container
import epub

"""
Crawl WuxiaWorld novels and write chapters to current directory.

As of 2015-12-20, completed translations include:
  Stellar Transf., http://www.wuxiaworld.com/st-index/st-book-1-chapter-1
  Coiling Dragon, http://www.wuxiaworld.com/cdindex-html/book-1-chapter-1
  Dragon King + 7 Stars, http://www.wuxiaworld.com/master-index/dkwss-chapter-1
  7 Killers, http://www.wuxiaworld.com/master-index/7-killers-chapter-1
  Heroes Shed No Tears, http://www.wuxiaworld.com/master-index/prologue
  Horizon, Bright Moon, Sabre, http://www.wuxiaworld.com/tymyd-index/prologue
"""

__version__ = '0.1'


def main():
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

    setup_logger()

    crawler = crawl.Crawler(opts.next_str, opts.prev_str,
                            opts.title_class, opts.content_class)

    try:
        chapts = crawler.crawl(first_url, last_url, opts.navlinks,
                               not opts.firsttitle, opts.limit)
    except KeyboardInterrupt:
        raise
    finally:  # Finish generating index/book for retrieved content
        container.Index(chapts).write()
        if opts.epub_title:
            epub.create_epub(opts.epub_title, chapts)


def setup_logger():
    logger = logging.getLogger('__wnget__')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    logger.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting...'
