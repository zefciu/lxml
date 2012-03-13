import re

try:
    _basestring = basestring
except NameError:
    _basestring = (str, bytes)
_norm_whitespace_re = re.compile(r'[ \t\n][ \t\n]+')
def norm_whitespace(v):
    return _norm_whitespace_re.sub(' ', v)

class Comparator(object):
    """Object encapsulating etree comparison logic.
    Usage:
    >>> from lxml.etree import fromstring
    >>> c = Comparator()
    >>> c.compare(fromstring('<person><name>Sir Galahad</name><surname>'
    ... 'the Pure</surname></person>'), fromstring('''<person><name>
    ...     Sir Galahad
    ... </name><surname>
    ...     the Pure
    ... </surname></person>'''))
    True
    >>> c.compare(fromstring('<person><name>Sir Galahad</name><surname>'
    ... 'the Pure</surname></person>'), fromstring('''<person><name>
    ...     Sir Galahad
    ... </name><surname>
    ...     the Dirty
    ... </surname></person>'''))
    False
    """

    empty_tags = (
        'param', 'img', 'area', 'br', 'basefont', 'input',
        'base', 'meta', 'link', 'col')

    def __init__(self, html=False, ellipses=False):
        self.html = html
        self.ellipses = ellipses

    def compare(self, x, y):
        if not self.tag_compare(x.tag, y.tag):
            return False
        if not self.text_compare(x.text, y.text, True):
            return False
        if not self.text_compare(x.tail, y.tail, True):
            return False
        if not (self.ellipses and ('any' in x.attrib or 'any' in y.attrib)):
            x_keys = sorted(x.attrib.keys())
            y_keys = sorted(x.attrib.keys())
            if x_keys != y_keys:
                return False
            for key in x_keys:
                if not self.text_compare(x.attrib[key], y.attrib[key], False):
                    return False
        if not (x.text == '...' or y.text == '...') and (len(x) or len(y)):
            x_children = list(x)
            y_children = list(y)
            while x_children or y_children:
                x_first = x_children.pop(0)
                y_first = y_children.pop(0)
                if not self.compare(x_first, y_first):
                    return False
        return True

    def text_compare(self, x, y, strip):
        x = x or ''
        y = y or ''
        if strip:
            x = norm_whitespace(x).strip()
            y = norm_whitespace(y).strip()

        if self.ellipses:
            if '...' in x:
                x = x.replace(r'\.\.\.', '.*')
                return bool(re.match(x, y))
            if '...' in y:
                y = y.replace(r'\.\.\.', '.*')
                return bool(re.match(y, x))
        return x == y

    def tag_compare(self, x, y):
        if self.ellipses and (x == 'any' or y == 'any'):
            return True
        if (not isinstance(x, _basestring)
            or not isinstance(y, _basestring)):
            return x == y
        x = x or ''
        y = y or ''
        if self.ellipses and (x.startswith('{...}') or y.startswith('{...}')):
            # Ellipsis on the namespace
            return x.split('}')[-1] == y.split('}')[-1]
        else:
            return x == y
