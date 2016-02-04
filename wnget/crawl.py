import logging
import os
import lxml.html
import requests
import eventlet

from . import container
from .utils import safe_decode, is_same_url, url_to_filename


NEXT_STR = 'Next Chapter'
PREV_STR = 'Previous Chapter'
T_CLASS = 'entry-title'
C_CLASS = 'entry-content'
DEFAULT_CONNECTION_TIMEOUT = 5  # seconds
TITLE_DELTA = 10  # Chapter titles should be within 10 lines of each other


class Crawler(object):
    """
    Crawler objects crawl the specified URL, following the link of whatever
    caption is specified upon creation.
    """
    def __init__(self, next_str=NEXT_STR, prev_str=PREV_STR,
                 title_class=T_CLASS, content_class=C_CLASS):
        self.next_str = next_str
        self.prev_str = prev_str
        self.title_class = title_class
        self.content_class = content_class
        self.logger = logging.getLogger(__name__)

    def _get_title(self, tree, default_title='', heuristic=True):
        # There is no one standard for title formatting across
        # webnovels. Ironically, the ones in the title containers tend
        # to look worse than the ones in the contents. Hence the
        # empiric precedence logic of this function.
        titles = tree.xpath('//*[@class="%s"]' % self.title_class)
        strongs = tree.xpath('//strong')
        bolds = tree.xpath('//p/b/span') or tree.xpath('//p/b')
        candidates = []

        if titles:
            candidates.append(titles[0])
        if strongs:
            candidates.append(strongs[0])
        if bolds:
            candidates.append(bolds[0])

        if heuristic:
            # cleanup candidates, and leave "best" first
            ref_sl = candidates[0].sourceline + TITLE_DELTA
            candidates = [c for c in candidates[::-1] if c.sourceline < ref_sl]
            candidates = list(filter(lambda x: x.text_content(), candidates))

        return candidates[0].text_content().strip()

    def _get_content(self, tree):
        return tree.xpath('//*[contains(@class,"%s")]' % self.content_class)[0]

    def _process_nav(self, tree, with_navlinks):
        """Process navigation links & find/rewrite/remove as appropriate"""

        next_nodes = tree.xpath("//a[starts-with(., '%s')]" % self.next_str) \
            or tree.xpath("//p[starts-with(., '%s')]" % self.next_str)
        prev_nodes = tree.xpath("//a[starts-with(., '%s')]" % self.prev_str) \
            or tree.xpath("//p[starts-with(., '%s')]" % self.prev_str)
        next_url = next_nodes[0].get('href') if next_nodes else None

        same_line_parents = []  # proper nav containers, if present
        for node in next_nodes + prev_nodes:
            if not with_navlinks:
                p = node.getparent()
                if p.sourceline == node.sourceline:
                    same_line_parents.append(p)
                p.remove(node)
            elif with_navlinks and node.tag == 'a':
                node.set('href', url_to_filename(node.get('href')))

        for node in set(same_line_parents):
            node.getparent().remove(node)

        return tree, next_url

    def crawl(self, next_url, last_url=None, with_navlinks=False,
              smart_titles=True, limit=0):
        "Crawl given url, rewriting/deleting navigation links if needed"
        eventlet.monkey_patch()  # eventlet magic...

        chapters = []
        prev_url = None
        while next_url:
            fname = url_to_filename(next_url)
            self.logger.info('URL: %s (%s%s)', next_url, fname,
                             ' *' if os.path.isfile(fname) else '')

            try:
                with eventlet.Timeout(DEFAULT_CONNECTION_TIMEOUT):
                    page = requests.get(next_url)
                    prev_url = next_url
                    next_url = None
                    limit -= 1
            except eventlet.Timeout:
                self.logger.error('Timed out! (%s)', next_url)
                break
            except requests.exceptions.MissingSchema as e:
                self.logger.error(e.message)
                break
            except KeyboardInterrupt:
                # End loop to return partial result
                break

            tree = lxml.html.fromstring(safe_decode(page.content))
            try:
                title = self._get_title(tree, fname, smart_titles)
                c_tree = self._get_content(tree)
                c_tree, next_url = self._process_nav(c_tree, with_navlinks)
            except IndexError:
                self.logger.error("Crawling stopped. Last page unexpected!")
                break

            if limit == 0 or is_same_url(last_url, prev_url):
                next_url = None

            c = container.Chapter(tree=c_tree, title=title, filename=fname,
                                  url=prev_url)
            chapters.append(c)
            if not os.path.isfile(fname):
                c.write()

        return chapters
