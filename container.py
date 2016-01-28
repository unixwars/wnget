import os
import lxml.html


class _Container(object):
    """Generic xhtml container"""
    def __init__(self, filename, title, tree):
        self.title = title
        self.tree = tree
        self.filename = filename
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
    def __init__(self, filename, title, tree, url):
        _Container.__init__(self, filename, title, tree)
        self.url = url

    @property
    def xhtml_filename(self):
        return self.filename.replace('.html', '.xhtml')


class Index(_Container):
    """Generate index.html out of a list of chapters"""
    def __init__(self, chapters, filename='index.html', title='Index'):
        self._load(filename)
        self._extend(chapters)
        self._dedupe()

        _Container.__init__(self, filename, title, self.tree)
        self._pre = lxml.etree.Element('h1')
        self._pre.text = self.title

    def _load(self, filename):
        if not os.path.isfile(filename):
            self.tree = lxml.etree.Element('ul', style="list-style-type:none;padding:0;")
        else:
            with open(filename, 'r') as f:
                self.tree = lxml.html.fromstring(f.read().decode('utf8'))
                self.tree = self.tree.xpath('//ul')[0]

    def _extend(self, chapters):
        for c in chapters:
            li = lxml.etree.SubElement(self.tree, 'li')
            link = lxml.etree.SubElement(li, 'a', href=c.filename)
            link.text = c.title

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
