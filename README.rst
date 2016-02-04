*wnget*: web novel getter
=========================

Rarely will web novel sites provide any means to read their contents off
line, and this is precisely why *wnget* came to be. It is a tool to
scrape web novels from blogs, and optionally convert them to epub
format. It provides several options to configure the exact behaviour,
while at the same time trying to provide sane defaults. The strings for
the next/previous navigation links, as well as CSS class for
title/content containers can be configured, among other settings.

Besides the main *wnget* utility, the suite include *wnbook*, to
generate ebooks from the downloaded contents, and *wnlocal*, to rewrite
the links of html files that can be resolved to a local file using the
same rules applied by *wnget*.

Installation
------------

.. code-block:: shell

    $ pip install wnget

If you happened to have cloned the repo and are playing with the code,
you probably want to install *wnget* in "editable" mode while you’re
working on it. This is so it becomes both installed and editable in
project form.

Assuming you’re in the root of the project, just run:

.. code-block:: shell

    $ pip install -e .

Usage examples
--------------

Invoke each command without arguments to display help information.

To scrape all chapters of a given web novel, following links, and saving
each chapter in a diferent html file in the current directory:

.. code-block:: shell

    $ wnget http://example.com/first_chapter_link

Or, for more advanced uses, downloading all chapters until a given link
is retrieved, and generate an EPUB with the loot:

.. code-block:: shell

    $ wnget -e "My Web Novel" \
      http://example.com/first_chapter_link  \
      http://example.com/first_chapter_link

Adittionally, the ebook functionality can be used directly through the
*wnbook* standalone utility. Just provide the HTML index file and a
name for the book, and it will generate an ebook with all referenced
resources in the working directory:

.. code-block:: shell

    $ wnbook index.html "My Web Novel"

Also, if a cover.png or cover.jpg file is present, it will be used as
cover page. Its use as standalone command will often prove more
flexible, as it exposes features not normally used by the main
application, while allowing some manual tweaking of the downloaded
contents and index files.

Here, generating a book with relative paths, and custom filename, cover
image, and language/author metadata:

.. code-block:: shell

    $ wnbook ../index.html "I Shall Seal the Heavens (我欲封天)" \
      --filename=issth.epub --language=zh --author="Ergen (耳根)" \
      --cover ~/images/MengHao.png

And finally, to rewrite links within a file so that they point to
already downloaded resources, *wnlocal* can be used.

Either to print the converted file to stdout:

.. code-block:: shell

    $ wnlocal introduction.html

Or to write it back to disk:

.. code-block:: shell

    $ wnlocal introduction.html newfile.html
