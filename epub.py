import os.path
import zipfile

# Mostly taken from:
# http://www.manuel-strehl.de/dev/simple_epub_ebooks_with_python.en.html

CONTAINER_XML = '''<container version="1.0"
           xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/Content.opf"
        media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>'''

INDEX_TPL = '''<package version="2.0"
  xmlns="http://www.idpf.org/2007/opf">
  <metadata/>
  <manifest>
    %(manifest)s
  </manifest>
  <spine toc="ncx">
    %(spine)s
  </spine>
</package>'''

MANIFEST_TPL = '''<item id="file_%(num)s" href="%(filename)s"
    media-type="application/xhtml+xml"/>'''
SPINE_TPL = '<itemref idref="file_%(num)s" />'


def create_epub(filename, html_files):
    epub = zipfile.ZipFile("%s.epub" % filename, 'w')

    # The first file must be named "mimetype"
    epub.writestr("mimetype", "application/epub+zip")

    # We need an index file, that lists all other HTML files
    # This index file itself is referenced in the META_INF/container.xml
    # file
    epub.writestr("META-INF/container.xml", CONTAINER_XML)

    # Write each HTML file to the ebook, collect information for the index
    manifest = ""
    spine = ""

    for i, html in enumerate(html_files):
        basename = os.path.basename(html)
        manifest += MANIFEST_TPL % {
            'num': i+1,
            'filename': basename
        }
        spine += '<itemref idref="file_%s" />' % {'num': i+1}
        epub.write(html, 'OEBPS/'+basename)

    # The index file is another XML file, living per convention
    # in OEBPS/Content.xml
    epub.writestr('OEBPS/Content.opf', INDEX_TPL % {
        'manifest': manifest,
        'spine': spine,
    })
