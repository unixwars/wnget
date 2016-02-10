import os
import sys
import logging
import yaml


SRC_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SRC_PATH, "data")
CFG_PATH = os.path.join(DATA_PATH, 'sites.yaml')

logger = logging.getLogger(__name__)


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


def href_to_local(href, dirname='.', force=False):
    """Maps a link to a local resource if present (or force==True)"""
    fname = url_to_filename(href)
    if os.path.isfile(os.path.join(dirname, fname)) or force:
        return fname
    return href


def get_site_defaults(url=None):
    """Get default parameters to processs a given site"""
    if url and not url.startswith('http'):
        url = None

    with open(CFG_PATH, 'r') as f:
        cfg = yaml.safe_load(f)

    key = None
    if url:
        netloc = url.split('/')[2]
        key = '.'.join(netloc.split('.')[-2:])  # Just second level domain
    return cfg.get(key, cfg['default'])
