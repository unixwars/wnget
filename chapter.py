import lxml


class Chapter(object):
    def __init__(self, title, content_tree, url):
        self.title = title
        self.content = content_tree
        self.url = url
        self.filename = self._url_to_filename()
        self.etree = self._content_to_etree()

    def _url_to_filename(self):
        url = self.url or ''
        end = filter(None, url.strip().split('/'))[-1]
        return '%s.html' % (end) if end else '#'

    def _content_to_etree(self):
        html = lxml.etree.Element('html', xmlns="http://www.w3.org/1999/xhtml")
        head = lxml.etree.SubElement(html, 'head')
        chap = lxml.etree.SubElement(head, 'title')
        chap.text = self.title
        meta = lxml.etree.SubElement(head, 'meta', charset='UTF-8')
        body = lxml.etree.SubElement(html, 'body')
        body.append(self.content)
        return lxml.etree.ElementTree(html)

    @property
    def html(self):
        return lxml.etree.tostring(self.etree)

    @property
    def xhtml_filename(self):
        return self.filename.replace('.html', '.xhtml')

    def write(self):
        self.etree.write(self.filename, encoding='utf-8', method='html',
                         pretty_print=True)
