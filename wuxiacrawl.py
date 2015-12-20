#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html
import lxml.etree
import requests
import os
import sys
import eventlet
import optparse
import index

"""
Crawl wuxiaworld.com novels and writes all chapters to current directory.

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
NEXT_STR = 'Next Chapter'
PREV_STR = 'Previous Chapter'
TITLE_CLASS = 'entry-title'
CONTENT_CLASS = 'entry-content'


def get_title(tree, default_title=''):
    # Wuxiaworld titles are inconsistent among creations. The ones
    # inside the content, if present, tend to look better than the ones
    # in H1 elements
    titles = tree.xpath('//h1[@class="%s"]' % TITLE_CLASS)
    strongs = tree.xpath('//strong')
    if titles:
        default_title = titles[0].text_content()
    if strongs:
        default_title = strongs[0].text_content()
    return default_title


def url_to_filename(url):
    url = url or ''
    url = url.strip()
    end = filter(None, url.split('/'))[-1]
    return '%s.html' % (end) if end else '#'


def process_nav(tree, with_navlinks):
    """Process navigation links & find/rewrite/remove as appropriate"""

    next_nodes = tree.xpath("//a[starts-with(., '%s')]" % NEXT_STR) or \
        tree.xpath("//p[starts-with(., '%s')]" % NEXT_STR)
    prev_nodes = tree.xpath("//a[starts-with(., '%s')]" % PREV_STR) or \
        tree.xpath("//p[starts-with(., '%s')]" % PREV_STR)
    next_url = next_nodes[0].get('href') if next_nodes else None

    for node in next_nodes + prev_nodes:
        if with_navlinks and node.tag == 'a':
            node.set('href', url_to_filename(node.get('href')))
        elif not with_navlinks:
            node.getparent().remove(node)

    return tree, next_url


def crawl(next_url, with_navlinks=False, indexer=None):
    eventlet.monkey_patch()  # eventlet magic...

    while next_url:
        fname = url_to_filename(next_url)
        print 'URL: %s (%s%s)' % (
            next_url,
            fname,
            ' *' if os.path.isfile(fname) else '')

        try:
            with eventlet.Timeout(5):
                page = requests.get(next_url)
                next_url = None
        except eventlet.Timeout:
            print 'Timed out!'
            continue

        tree = lxml.html.fromstring(page.content)
        title = get_title(tree, fname)
        content = tree.xpath('//div[@class="%s"]' % CONTENT_CLASS)[0]
        content, next_url = process_nav(content, with_navlinks)

        if indexer:
            indexer.update(fname, title)
            print type(indexer)

        if os.path.isfile(fname):
            continue

        lxml.etree.ElementTree(content).write(fname, pretty_print=True)


def main():
    p = optparse.OptionParser(
        usage="Usage: %prog [options] url",
        version="wuxiacrawl version %s" % __version__)

    p.add_option(
        '--navlinks', '-n',
        action="store_true",
        default=False,
        dest="navlinks",
        help="Preserve navigation links in HTML content.")

    p.add_option(
        '--skipindex', '-s',
        action="store_true",
        default=False,
        dest="skipindex",
        help="Don't make index file.")

    opts, args = p.parse_args()

    if len(args) != 1:
        p.error("Incorrect number of arguments. Provide ONE url!")

    index_file = INDEX_FILE if not opts.skipindex else None
    with index.Index(index_file) as indexer:
        crawl(args[0], opts.navlinks, indexer)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting...'
