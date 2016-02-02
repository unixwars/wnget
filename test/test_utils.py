import sys

from wnget.utils import safe_decode, is_same_url, url_to_filename


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
