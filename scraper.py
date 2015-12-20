from lxml import html
import requests
import os

URL_TPL = 'http://www.wuxiaworld.com/%s-index/%s-chapter-%d' # %(novel, book, chapter)
FNAME_TPL = '%s-chapter-%.3d.html' # %(book, chapter)
TARGET_TOUPLES = [
    ('tdg', 'tdg', (1,135)),
    ('issth', 'issth-book-1', (1,95)),
    ('issth', 'issth-book-2', (96,204)),
    ('issth', 'issth-book-3', (205,282)),
]

for tgt in TARGET_TOUPLES:
    novel, book, chapter_range = tgt
    start, end = chapter_range
    for chapter in xrange(start, end+1):
        fname = FNAME_TPL %(book, chapter)

        if os.path.isfile(fname):
            continue

        print 'File: %s' % fname
        url = URL_TPL % (novel, book, chapter)
        page = requests.get(url)
        tree = html.fromstring(page.content)

        with open(fname, 'w') as f:
            content = tree.xpath('//div[@class="entry-content"]')[0].text_content()
            #next_link = tree.xpath('//div[@class="entry-content"]/p[1]/span/a/@href')[0]
            f.write(content.encode('utf8'))
