TOP_TEMPLATE = """<html>\n<body>
<h1>TOC</h1>
<p style="text-indent:0pt">\n"""

BOTTOM_TEMPLATE = '</p>\n</body>\n</html>\n'
ENTRY_TEMPLATE = '<a href="%s">%s</a><br/>\n'  # %(link, title)


class Index(object):
    """
    Create index files, suitable as TOC epub TOC
    """
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        if self.filename:
            self.f = open(self.filename, 'w')
            self.f.write(TOP_TEMPLATE)
        return self

    def __exit__(self, type, value, traceback):
        if self.f:
            self.f.write(BOTTOM_TEMPLATE)
            return self.f.__exit__(type, value, traceback)

    def update(self, link, title):
        if self.f:
            self.f.write(ENTRY_TEMPLATE % (link, title))
