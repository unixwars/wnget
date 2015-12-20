#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html, lxml.etree
import requests
import os
import sys
import eventlet
import optparse

"""
Crawl wuxiaworld.com novels and writes all chapters to current directory.
"""

COMPLETED_NOVELS  = [
    ('Stellar Transformations (星辰变)', 'http://www.wuxiaworld.com/st-index/st-book-1-chapter-1/'),
    ('Coiling Dragon (盘龙)', 'http://www.wuxiaworld.com/cdindex-html/book-1-chapter-1'),
    ('Dragon King With Seven Stars', 'http://www.wuxiaworld.com/master-index/dkwss-chapter-1/'),
    ('7 Killers', 'http://www.wuxiaworld.com/master-index/7-killers-chapter-1/'),
    ('Heroes Shed No Tears', 'http://www.wuxiaworld.com/master-index/prologue/'),
    ('Horizon, Bright Moon, Sabre (天涯明月刀)', 'http://www.wuxiaworld.com/tymyd-index/prologue/'),
]

INDEX_FILE = 'index.html'


def get_title(tree, default_title=''):
    # Wuxiaworld titles are inconsistent among creations. The ones
    # inside the content, if present, tend to look better than the ones
    # in H1 elements
    titles = tree.xpath('//h1[@class="entry-title"]')
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
    """Process navigation links, find next one, and either transform or remove"""

    next_nodes = tree.xpath("//a[starts-with(., 'Next Chapter')]") or tree.xpath("//p[starts-with(., 'Next Chapter')]")
    prev_nodes = tree.xpath("//a[starts-with(., 'Previous Chapter')]") or tree.xpath("//p[starts-with(., 'Previous Chapter')]")
    next_url = next_nodes[0].get('href') if next_nodes else None

    for node in next_nodes + prev_nodes:
        if with_navlinks and node.tag == 'a':
            node.set('href', url_to_filename(node.get('href')))
        elif not with_navlinks:
            node.getparent().remove(node)

    return tree, next_url


def update_index(file_handle, title, link):
    pass


def crawl(next_url, with_navlinks=False, index_handle=None):
    eventlet.monkey_patch() # eventlet magic...

    while next_url:
        fname = url_to_filename(next_url)
        print 'URL: %s (%s%s)' % (next_url, fname, ' *' if os.path.isfile(fname) else '')

        try:
            with eventlet.Timeout(5):
                page = requests.get(next_url)
                next_url = None
        except eventlet.Timeout:
            print 'Timed out!'
            continue

        tree = lxml.html.fromstring(page.content)
        title = get_title(tree, fname)
        content = tree.xpath('//div[@class="entry-content"]')[0]
        content, next_url = process_nav(content, with_navlinks)

        update_index(index_handle, title, fname)
        if os.path.isfile(fname):
            continue

        lxml.etree.ElementTree(content).write(fname, pretty_print=True)


def main():
    p = optparse.OptionParser()
    p.add_option('--navlinks', '-n',
                 action="store_true",
                 default=False,
                 dest="navlinks",
                 help="Preserve navigation links in HTML content.")

    p.add_option('--skipindex', '-s',
                 action="store_true",
                 default=False,
                 dest="skipindex",
                 help="Don't make index file.")

    opts, args = p.parse_args()

    if len(args) != 1:
        p.error("Incorrect number of arguments. Provide ONE url!")

    if opts.skipindex:
        crawl(args[0], opts.navlinks, None)
    else:
        with open(INDEX_FILE, 'w') as file_handle:
            crawl(args[0], opts.navlinks, file_handle)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting...'
