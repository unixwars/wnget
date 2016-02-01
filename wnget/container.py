import os
import lxml.html


class _Container(object):
    """Generic xhtml container"""
    def __init__(self, tree, title, filename):
        self.tree = tree
        self.title = title
        self.filename = os.path.basename(filename)
        self._pre = None

    @property
    def content(self):
        self._html = lxml.etree.Element('html', xmlns="http://www.w3.org/1999/xhtml")
        self._head = lxml.etree.SubElement(self._html, 'head')
        self._title = lxml.etree.SubElement(self._head, 'title')
        self._title.text = self.title
        self._meta = lxml.etree.SubElement(self._head, 'meta', charset='UTF-8')
        self._body = lxml.etree.SubElement(self._html, 'body')
        if self._pre is not None:
            self._body.append(self._pre)
        self._body.append(self.tree)
        return lxml.etree.ElementTree(self._html)

    @property
    def html(self):
        return lxml.etree.tostring(self.content, encoding='utf-8',
                                   method='html', pretty_print=True)

    def write(self):
        return self.content.write(self.filename, encoding='utf-8',
                                  method='html', pretty_print=True)


class Chapter(_Container):
    """Chapters are what's kept after scraping web pages"""
    def __init__(self, tree, title, filename, url):
        _Container.__init__(self, tree, title, filename)
        self.url = url

    @property
    def xhtml_filename(self):
        return self.filename.replace('.html', '.xhtml')

    @classmethod
    def from_file(cls, fname, title):
        with open(fname) as f:
            tree = lxml.html.fromstring(f.read().decode('utf8'))
            body = tree.xpath('//body')[0]
            div = list(body.iterchildren())[0]

        return cls(tree=div, title=title, filename=fname, url=fname)


class Index(_Container):
    """Generate index.html out of a list of chapters"""
    def __init__(self, chapters=[], title='Index', filename='index.html'):
        self._load(filename)
        self._extend(chapters)
        self._dedupe()

        _Container.__init__(self, self.tree, title, filename)
        self.dirname = os.path.dirname(os.path.abspath(filename))
        self._pre = lxml.etree.Element('h1')
        self._pre.text = self.title

    def _load(self, filename):
        self.tree = lxml.etree.Element('ul', style="list-style-type:none;padding:0;")
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                tree = lxml.html.fromstring(f.read().decode('utf8'))
                links = tree.xpath('//a')
                for link in links:
                    self.append(link.get('href'), link.text)

    def _extend(self, chapters):
        for c in chapters:
            self.append(c.filename, c.title)

    def append(self, filename, title):
        li = lxml.etree.SubElement(self.tree, 'li')
        link = lxml.etree.SubElement(li, 'a', href=filename)
        link.text = title

    def _dedupe(self):
        uniques = set()
        dupes = []
        for elem in self.tree.iterchildren():
            text = lxml.html.tostring(elem).strip()
            if text in uniques:
                dupes.append(elem)
            else:
                uniques.add(text)

        for dupe in dupes:
            self.tree.remove(dupe)

    @property
    def links(self):
        return self.tree.xpath('//a')

    @property
    def chapters(self):
        for link in self.links:
            fname = os.path.join(self.dirname, link.get('href'))
            yield Chapter.from_file(fname, link.text)