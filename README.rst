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

Configuration
-------------

Any argument that starts with '--' can also be set in a config file
(./wnget.conf or ~/.wnget.conf or specified via -s). The
recognized syntax for setting (key, value) pairs is based on the INI and YAML
formats (e.g. key=value or foo=TRUE). If an argument is specified in more than
one  place, then commandline values override config file values which override
defaults.

The default configuration looks like this:

.. code-block:: yaml

  keeplinks: no
  firsttitle: no
  next: "Next Chapter"
  previous: "Previous Chapter"
  titleclass: entry-title
  contentclass: entry-content
  epub: default_ebook
  limit: 0 # No limit if < 1

Since every web novel site will have a unique theme, it is unlikely the
default configurations shipped with _wnget_ will work out of the box (unless
you happen to be addicted to the same ones as yours truly). Feel free to
extend data/sites.yaml for your favorite sites and issue a pull request.

Usage
-----

.. code-block:: shell

  $ wnget --help
  usage: wnget [-h] [-s file] [-k] [-f] [-n caption] [-p caption] [-t css_class]
               [-c css_class] [-e title] [-l N] [-v]
               first_url [last_url]

  positional arguments:
    first_url             first URL to crawl
    last_url              optional last URL to crawl (stops after reaching)

  optional arguments:
    -h, --help            show this help message and exit
    -s file, --settings file
                          config file path
    -k, --keeplinks       rewrite and keep navigation links in HTML content
    -f, --firsttitle      keep first title match instead of trying to be smart
                          about it
    -n caption, --next caption
                          next link caption (default: 'Next Chapter')
    -p caption, --previous caption
                          previous link caption (default: 'Previous Chapter')
    -t css_class, --titleclass css_class
                          title container class (default: 'entry-title')
    -c css_class, --contentclass css_class
                          content container class (default: 'entry-content')
    -e title, --epub title
                          create Epub with this title (will use cover.jpg/png if
                          found)
    -l N, --limit N       crawl at most N pages
    -v, --version         show program's version number and exit

Usage examples
--------------

Invoke each command without arguments to display help information.

The scraper looks for a given CSS class in the title and content containers,
and those can be set manually to suit your web novel site of choice. It also
looks for links with default strings to find the next and previous chapters,
and this can also be set by hand.

To scrape all chapters of a given web novel, following links, and saving
each chapter in a different html file in the current directory:

.. code-block:: shell

    $ wnget http://example.com/first_chapter_link

Or, for more advanced uses, downloading all chapters until a given link
is retrieved, and generate an EPUB with the loot:

.. code-block:: shell

    $ wnget -e "My Web Novel" \
      http://example.com/first_chapter_link  \
      http://example.com/first_chapter_link

Additionally, the ebook functionality can be used directly through the
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


TODO
----

+ Make content selection more flexible: by tag, class, caption, or xpath.
+ Add option for elements to be removed during the parsing stage.
+ Add interactive title selection mode (and ability to repeat choice).
+ In-content image support (download, and store locally).
