import lxml.html
import lxml.etree
import requests
import os
import eventlet
import index
import epub
import chapter

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

    def crawl(self, url, with_navlinks=False, index_file=None, epub_title=None,
              smart_titles=True, limit=0):
        "Crawl given url, rewriting/deleting navigation links, and " + \
            "overwriting index file if provided"

        with index.Index(index_file) as indexer:
            lst = self._crawl(url, with_navlinks, indexer, smart_titles, limit)

        if epub_title is not None:
            epub.create_epub(epub_title, lst)

    def _get_title(self, tree, default_title='', heuristic=True):
        # Wuxiaworld titles are inconsistent among creations. The ones
        # inside the content, if present, tend to look better than the ones
        # in H1 elements.
        titles = tree.xpath('//*[@class="%s"]' % self.title_class)
        strongs = tree.xpath('//p/strong')
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

        return candidates[0].text_content().strip()

    def _url_to_filename(self, url):
        url = url or ''
        url = url.strip()
        end = filter(None, url.split('/'))[-1]
        return '%s.html' % (end) if end else '#'

    def _process_nav(self, tree, with_navlinks):
        """Process navigation links & find/rewrite/remove as appropriate"""

        next_nodes = tree.xpath("//a[starts-with(., '%s')]" % self.next_str) \
            or tree.xpath("//p[starts-with(., '%s')]" % self.next_str)
        prev_nodes = tree.xpath("//a[starts-with(., '%s')]" % self.prev_str) \
            or tree.xpath("//p[starts-with(., '%s')]" % self.prev_str)
        next_url = next_nodes[0].get('href') if next_nodes else None

        for node in next_nodes + prev_nodes:
            if with_navlinks and node.tag == 'a':
                node.set('href', self.url_to_filename(node.get('href')))
            elif not with_navlinks:
                node.getparent().remove(node)

        return tree, next_url

    def _crawl(self, next_url, with_navlinks, indexer, smart_titles, limit):
        assert isinstance(indexer, index.Index) or indexer is None

        eventlet.monkey_patch()  # eventlet magic...

        chapters = []
        count = 0
        last_url = None
        while next_url:
            fname = self._url_to_filename(next_url)
            print 'URL: %s (%s%s)' % (next_url, fname,
                                      ' *' if os.path.isfile(fname) else '')

            try:
                with eventlet.Timeout(DEFAULT_CONNECTION_TIMEOUT):
                    page = requests.get(next_url)
                    last_url = next_url
                    next_url = None
                    count += 1
            except eventlet.Timeout:
                print 'Timed out!'
                continue

            tree = lxml.html.fromstring(page.content.decode('utf8'))
            title = self._get_title(tree, fname, smart_titles)
            c_tree = tree.xpath('//*[@class="%s"]' % self.content_class)[0]
            c_tree, next_url = self._process_nav(c_tree, with_navlinks)

            if limit and count == limit:
                next_url = None

            if indexer:
                indexer.update(fname, title)

            c = chapter.Chapter(title, c_tree, last_url)
            chapters.append(c)
            if os.path.isfile(fname):
                continue

            c.write()

        return chapters
