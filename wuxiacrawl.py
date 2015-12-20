#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
import crawl

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
INDEX_FILE = 'index.html'


def main():
    p = optparse.OptionParser(
        usage="Usage: %prog [options] url",
        version="wuxiacrawl version %s" % __version__)

    p.add_option(
        '--keeplinks', '-k',
        action="store_true",
        default=False,
        dest="navlinks",
        help="Rewrite and keep navigation links in HTML content.")

    p.add_option(
        '--skipindex', '-s',
        action="store_true",
        default=False,
        dest="skipindex",
        help="Don't make index file.")

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

    opts, args = p.parse_args()

    if len(args) != 1:
        p.error("Incorrect number of arguments. Provide ONE url!")

    index_file = INDEX_FILE if not opts.skipindex else None
    crawler = crawl.Crawler(opts.next_str, opts. prev_str,
                    opts.title_class, opts.content_class)

    crawler.crawl(args[0], opts.navlinks, index_file)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting...'
