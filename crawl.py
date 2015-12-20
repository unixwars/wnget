import lxml.html
import lxml.etree
import requests
import os
import eventlet
import index

NEXT_STR = 'Next Chapter'
PREV_STR = 'Previous Chapter'
T_CLASS = 'entry-title'
C_CLASS = 'entry-content'
DEFAULT_CONNECTION_TIMEOUT = 5  # seconds

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

    def crawl(self, url, with_navlinks=False, index_file=None):
        "Crawl given url, rewriting/deleting navigation links, and " + \
            "overwriting index file if provided"

        with index.Index(index_file) as indexer:
            self._crawl(url, with_navlinks, indexer)

    def _get_title(self, tree, default_title=''):
        # Wuxiaworld titles are inconsistent among creations. The ones
        # inside the content, if present, tend to look better than the ones
        # in H1 elements
        titles = tree.xpath('//*[@class="%s"]' % self.title_class)
        strongs = tree.xpath('//strong')
        if titles:
            default_title = titles[0].text_content()
        if strongs:
            default_title = strongs[0].text_content()
        return default_title

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
                node.set('href', url_to_filename(node.get('href')))
            elif not with_navlinks:
                node.getparent().remove(node)

        return tree, next_url

    def _crawl(self, next_url, with_navlinks, indexer):
        assert isinstance(indexer, index.Index) or indexer is None

        eventlet.monkey_patch()  # eventlet magic...

        while next_url:
            fname = self._url_to_filename(next_url)
            print 'URL: %s (%s%s)' % (next_url,  fname,
                                      ' *' if os.path.isfile(fname) else '')

            try:
                with eventlet.Timeout(DEFAULT_CONNECTION_TIMEOUT):
                    page = requests.get(next_url)
                    next_url = None
            except eventlet.Timeout:
                print 'Timed out!'
                continue

            tree = lxml.html.fromstring(page.content.decode('utf8'))
            title = self._get_title(tree, fname)
            content = tree.xpath('//*[@class="%s"]' % self.content_class)[0]
            content, next_url = self._process_nav(content, with_navlinks)

            if indexer:
                indexer.update(fname, title)

            if os.path.isfile(fname):
                continue

            self._write_html(content, fname)

    def _write_html(self, content, fname):
        html = lxml.etree.Element('html')
        head = lxml.etree.SubElement(html, 'head')
        meta = lxml.etree.SubElement(head, 'meta', charset='UTF-8')
        body = lxml.etree.SubElement(html, 'body')
        body.append(content)
        lxml.etree.ElementTree(html).write(fname, encoding='utf8', pretty_print=True)
