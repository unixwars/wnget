import os
import lxml.etree
import lxml.html


class Index(object):
    """
    Index objects create index files suitable for Epub TOC creation
    """
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if self.filename is not None:
            if os.path.isfile(self.filename):
                self.entries = self._load_entries()
            else:
                self.entries = lxml.etree.Element('p', style="text-indent:0pt")
        return self

    def __exit__(self, type, value, traceback):
        if self.entries is not None:
            html = lxml.etree.Element('html',
                                      xmlns="http://www.w3.org/1999/xhtml")
            head = lxml.etree.SubElement(html, 'head')
            title = lxml.etree.SubElement(head, 'title')
            title.text = 'Index'
            meta = lxml.etree.SubElement(head, 'meta', charset='UTF-8')
            body = lxml.etree.SubElement(html, 'body')
            h1 = lxml.etree.SubElement(body, 'h1')
            h1.text = 'Index'
            body.append(self.entries)

            lxml.etree.ElementTree(html).write(self.filename,
                                               encoding='utf-8',
                                               method='html',
                                               pretty_print=True)

    def _load_entries(self):
        with open(self.filename, 'r') as f:
            tree = lxml.html.fromstring(f.read().decode('utf8'))
            return tree.xpath('//p')[0]

    def update(self, link, title):
        if self.entries is not None:
            entry = lxml.etree.SubElement(self.entries, 'a', href=link)
            entry.text = title
            br = lxml.etree.SubElement(self.entries, 'br')
