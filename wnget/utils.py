import sys


def safe_decode(st):
    """Decode PY2 str types to utf8, not breaking PY3 ones"""
    if st is None or sys.version_info > (2,):
        return st
    return st.decode('utf8')


def is_same_url(a, b):
    """Check if different forms of same URL match"""
    return a and b and a.strip().strip('/') == b.strip().strip('/')


def url_to_filename(url):
    """Generate a filename to save a given URL"""
    url = url or '#'
    url = url.strip().strip('/').rstrip('.html') + '.html'
    return url.split('/')[-1]
