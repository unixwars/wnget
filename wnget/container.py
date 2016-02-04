import os
import lxml
import lxml.html.builder as builder

from .utils import safe_decode


class Container(object):
    """Generic xhtml container"""
    def __init__(self, tree, title, filename):
        self.tree = tree
        self.title = title
        self.filename = filename
        self.dirname = os.path.dirname(os.path.abspath(filename))
        self.basename = os.path.basename(os.path.abspath(filename))
        self._pre = None

    @property
    def body(self):
        elem = lxml.etree.Element('body')
        if self._pre is not None:
            elem.append(self._pre)
        elem.append(self.tree)
        return elem

    @property
    def full_tree(self):
        return builder.HTML(
            builder.HEAD(
                builder.TITLE(self.title),
                builder.META(charset="utf-8")),
            self.body)

    @property
    def html(self):
        return lxml.html.tostring(
            self.full_tree, pretty_print=True, encoding='utf-8',
            method='html', doctype='<!DOCTYPE html>')

    @property
    def xhtml_filename(self):
        return self.filename.replace('.html', '.xhtml')

    def write(self):
        with open(self.filename, 'w') as f:
            f.write(self.html)


class Chapter(Container):
    """Chapters are what's kept after scraping web pages"""
    def __init__(self, tree, title, filename, url):
        Container.__init__(self, tree, title, filename)
        self.url = url

    @property
    def xhtml_filename(self):
        return self.filename.replace('.html', '.xhtml')

    @classmethod
    def from_file(cls, fname, title):
        with open(fname) as f:
            tree = lxml.html.fromstring(safe_decode(f.read()))
            body = tree.xpath('//body')[0]
            div = list(body.iterchildren())[0]

        return cls(tree=div, title=title, filename=fname, url=fname)


class Index(Container):
    """Generate index.html out of a list of chapters"""
    def __init__(self, chapters=[], title='Index', filename='index.html'):
        self._load(filename)
        self._extend(chapters)
        self._dedupe()

        Container.__init__(self, self.tree, title, filename)
        self._pre = lxml.etree.Element('h1')
        self._pre.text = self.title

    def _load(self, filename):
        self.tree = lxml.etree.Element(
            'ul', style="list-style-type:none;padding:0;")
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                tree = lxml.html.fromstring(safe_decode(f.read()))
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
