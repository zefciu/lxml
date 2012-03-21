import re
import cgi

from lxml import etree

try:
    _basestring = basestring
except NameError:
    _basestring = (str, bytes)

_norm_whitespace_re = re.compile(r'[ \t\n][ \t\n]+')
def norm_whitespace(v):
    return _norm_whitespace_re.sub(' ', v)

def strip(v):
    if v is None:
        return None
    else:
        return v.strip()

_html_parser = etree.HTMLParser(recover=False, remove_blank_text=True)

def html_fromstring(html):
    return etree.fromstring(html, _html_parser)

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
            y_keys = sorted(y.attrib.keys())
            if x_keys != y_keys:
                return False
            for key in x_keys:
                if not self.text_compare(x.attrib[key], y.attrib[key], False):
                    return False
        if not (x.text == '...' or y.text == '...') and (len(x) or len(y)):
            x_children = list(x)
            y_children = list(y)
            while x_children or y_children:
                if not x_children or not y_children:
                    return False
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

    def get_diff(self, x, y):
        errors = []
        x_formatted = self.format_doc(x, 0)
        y_formatted = self.format_doc(y, 0)
        diff = self.collect_diff(x, y, 0)
        return (x_formatted, y_formatted, diff)

    def html_empty_tag(self, el):
        if not self.html:
            return False
        if el.tag not in self.empty_tags:
            return False
        if el.text or len(el):
            # This shouldn't happen (contents in an empty tag)
            return False
        return True

    def format_doc(self, doc, indent, prefix=''):
        parts = []
        if not len(doc):
            # No children...
            line_parts = [prefix, ' ' * indent, self.format_tag(doc)]
            if not self.html_empty_tag(doc):
                if strip(doc.text):
                    line_parts.append(self.format_text(doc.text))
                line_parts.append(self.format_end_tag(doc))
            if strip(doc.tail):
                line_parts.append(self.format_text(doc.tail))
            return [''.join(line_parts)]
        parts.append(prefix + ' ' * indent + self.format_tag(doc))
        if not self.html_empty_tag(doc):
            if strip(doc.text):
                parts.append(
                    prefix + ' ' * indent + self.format_text(doc.text)
                )
            for el in doc:
                parts += self.format_doc(el, indent+2, prefix)
            parts.append(prefix + ' ' * indent + self.format_end_tag(doc))
        if strip(doc.tail):
            parts.append(prefix + ' '*indent + self.format_text(doc.tail))
        return parts

    def format_text(self, text, strip=True):
        if text is None:
            return ''
        if strip:
            text = text.strip()
        return cgi.escape(text, 1)

    def format_tag(self, el):
        attrs = []
        if isinstance(el, etree.CommentBase):
            # FIXME: probably PIs should be handled specially too?
            return '<!--'
        for name, value in sorted(el.attrib.items()):
            attrs.append('%s="%s"' % (name, self.format_text(value, False)))
        if not attrs:
            return '<%s>' % el.tag
        return '<%s %s>' % (el.tag, ' '.join(attrs))

    def format_end_tag(self, el):
        if isinstance(el, etree.CommentBase):
            # FIXME: probably PIs should be handled specially too?
            return '-->'
        return '</%s>' % el.tag

    def collect_diff(self, x, y, indent):
        parts = []
        if not len(x) and not len(y):
            parts.append(' '*indent)
            parts.append(self.collect_diff_tag(x, y))
            if not self.html_empty_tag(x):
                parts.append(self.collect_diff_text(x.text, y.text))
                parts.append(self.collect_diff_end_tag(x, y))
            parts.append(self.collect_diff_text(x.tail, y.tail))
            return [''.join(parts)]
        parts.append(' ' * indent + self.collect_diff_tag(x, y))
        if strip(x.text) or strip(y.text):
            parts.append(' ' * indent + self.collect_diff_text(x.text, y.text))
        x_children = list(x)
        y_children = list(y)
        while x_children or y_children:
            if not x_children:
                parts += self.format_doc(y_children.pop(0), indent+2, '-')
                continue
            if not y_children:
                parts += self.format_doc(x_children.pop(0), indent+2, '+')
                continue
            parts += self.collect_diff(
                x_children.pop(0), y_children.pop(0), indent+2
            )
        parts.append(' '*indent + self.collect_diff_end_tag(x, y))
        if strip(x.tail) or strip(y.tail):
            parts.append(' '*indent + self.collect_diff_text(x.tail, y.tail))
        return parts

    def collect_diff_tag(self, x, y):
        if not self.tag_compare(x.tag, y.tag):
            tag = '%s (- %s)' % (x.tag, y.tag)
        else:
            tag = x.tag
        attrs = []
        any_x = self.ellipses and (y.tag == 'any' or 'any' in y.attrib)
        any_y = self.ellipses and (x.tag == 'any' or 'any' in x.attrib)
        # (sic!)
        sorted_x = sorted(x.attrib.keys())
        sorted_y = sorted(y.attrib.keys())
        if self.ellipses:
            if 'any' in sorted_x:
                del sorted_x[sorted_x.index('any')]
            if 'any' in sorted_y:
                del sorted_y[sorted_y.index('any')]
        while sorted_x or sorted_y:
            if not sorted_x:
                name = sorted_y.pop(0)
                attrs.append('%(sign)s%(name)s="%(value)s"' % {
                    'sign': ('' if any_y else '+'),
                    'name': name,
                    'value': y.attrib[name],
                })
            elif not sorted_y:
                name = sorted_x.pop(0)
                attrs.append('%(sign)s%(name)s="%(value)s"' % {
                    'sign': ('' if any_x else '-'),
                    'name': name,
                    'value': x.attrib[name],
                })
            else:
                next_x = sorted_x.pop(0)
                try:
                    y_index = sorted_y.index(next_x)
                except ValueError:
                    attrs.append('%(sign)s%(name)s="%(value)s"' % {
                        'sign': ('' if any_y else '-'),
                        'name': next_x,
                        'value': x.attrib[next_x],
                    })
                else:
                    next_y = sorted_y.pop(y_index)
                    attrs.append('%s="%s"' % (next_x, self.collect_diff_text(
                        x.attrib[next_x], y.attrib[next_y], False
                    )))
        if attrs:
            tag = '<%s %s>' % (tag, ' '.join(attrs))
        else:
            tag = '<%s>' % tag
        return tag

    def collect_diff_end_tag(self, x, y):
        if not self.tag_compare(x.tag, y.tag):
            tag = '%s (- %s)' % (x.tag, y.tag)
        else:
            tag = x.tag
        return '</%s>' % tag

    def collect_diff_text(self, x, y, strip=True):
        if self.text_compare(x, y, strip):
            return self.format_text(x, strip)
        text = '%s (- %s)' % (x, y)
        return self.format_text(text, strip)
    
def assertXMLEqual(x, y, html = False, **kwargs):
    comparator = Comparator(html=html, **kwargs)
    parser = html_fromstring if html else etree.XML
    if isinstance (x, _basestring):
        x = parser(x)
    if isinstance (y, _basestring):
        y = parser(y)
    if not comparator.compare(x, y):
        raise AssertionError('\n'.join(comparator.get_diff(x, y)[2]))
