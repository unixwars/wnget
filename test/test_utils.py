import os
import sys
import tempfile

from wnget.utils import (
    safe_decode,
    is_same_url,
    url_to_filename,
    href_to_local,
    get_site_defaults,
)

def test_is_same_url():
    assert is_same_url('http://example.com', 'http://example.com/') is True
    assert is_same_url('http://example.com/1', 'http://example.com/2') is False


def test_url_to_filename():
    assert url_to_filename('http://foo/bar') == 'bar.html'
    assert url_to_filename('http://foo/bar/') == 'bar.html'
    assert url_to_filename('') == '#.html'


def test_safe_decode():
    u, b, s = u'test', b'test', 'test'
    su, sb, ss = safe_decode(u), safe_decode(b), safe_decode(s)

    assert safe_decode(None) is None
    if sys.version_info > (2,):
        # PY3: str == unicode, b'' is data format
        assert su == ss == s == u
        assert sb == b
    else:
        # PY2: b'' == str != unicode, so sb is unicode as well
        assert su == sb == ss == u


def test_href_to_local():
    f, html_f = tempfile.mkstemp(suffix='.html', dir='/tmp')
    local_href = os.path.basename(html_f)
    href = 'http://example.com/' + local_href

    assert href_to_local(href, '/', False) == href
    assert href_to_local(href, '/', True) == local_href
    assert href_to_local(href, '/tmp', False) == local_href
    os.unlink(html_f)


def test_get_site_defaults():
    default = get_site_defaults(None)
    wuxia = get_site_defaults('http://www.wuxiaworld.com')
    nnao1 = get_site_defaults('http://www.novelsnao.com')
    nnao2 = get_site_defaults('http://novelsnao.com')

    assert default == wuxia
    assert nnao1 == nnao2
    assert nnao1['contentclass'] == "CommonWhiteTypeOne"
