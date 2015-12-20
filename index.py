import lxml.etree

class Index(object):
    """
    Index objects create index files suitable for Epub TOC creation
    """
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if self.filename is not None:
            self.entries = lxml.etree.Element('p', style="text-indent:0pt")
        return self

    def __exit__(self, type, value, traceback):
        if self.entries is not None:
            html = lxml.etree.Element('body')
            head = lxml.etree.SubElement(html, 'head')
            meta = lxml.etree.SubElement(head, 'meta', charset='UTF-8')
            body = lxml.etree.SubElement(html, 'body')
            h1 = lxml.etree.SubElement(body, 'h1')
            h1.text = 'TOC'
            body.append(self.entries)

            lxml.etree.ElementTree(html).write(self.filename, encoding='utf8', pretty_print=True)

    def update(self, link, title):
        if self.entries is not None:
            entry = lxml.etree.SubElement(self.entries, 'a', href=link)
            entry.text = title
            br = lxml.etree.SubElement(self.entries, 'br')
