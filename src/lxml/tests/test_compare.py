import unittest

from lxml.etree import fromstring
from lxml.compare import Comparator

BASIC_EXAMPLE = fromstring("""<knights>
    <knight iq="98" found-grail="nope">
        <name>Sir Galahad</name>
        <nickname>The Pure</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="200" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
</knights>""")

WRONG_ROOT_TAG = fromstring("""<peasants>
    <knight iq="98" found-grail="nope">
        <name>Sir Galahad</name>
        <nickname>The Pure</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="200" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
</peasants>""")
 
EXTRA_CHILD = fromstring("""<knights>
    <knight iq="98" found-grail="nope">
        <name>Sir Galahad</name>
        <nickname>The Pure</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="200" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
    <knight iq="80" found-grail="nope">
        <name>Sir Robin</name>
        <nickname>The Not-So-Brave</nickname>
    </knight>
</knights>""")

WRONG_ATTRIB = fromstring("""<knights>
    <knight iq="98" found-grail="nope">
        <name>Sir Galahad</name>
        <nickname>The Pure</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="70" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
</knights>""")

ELLIPSED_TEXT = fromstring("""<knights>
    <knight iq="98" found-grail="nope">
        <name>...</name>
        <nickname>...</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="200" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
</knights>""")
 
ELLIPSED_TAG = fromstring("""<any>
    <knight iq="98" found-grail="nope">
        <name>Sir Galahad</name>
        <nickname>The Pure</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="200" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
</any>""")

ELLIPSED_ATTRIB = fromstring("""<knights>
    <knight any="any">
        <name>Sir Galahad</name>
        <nickname>The Pure</nickname>
    </knight>
    <knight iq="90" found-grail="nope">
        <name>Sir Lancelot</name>
        <nickname>The Brave</nickname>
    </knight>
    <knight iq="200" found-grail="nope">
        <name>Sir Bedevere</name>
        <nickname>The Wise</nickname>
    </knight>
</knights>""")

non_ellipsing_comp = Comparator(ellipses=False)
ellipsing_comp = Comparator(ellipses=True)

class Test(unittest.TestCase):
    maxDiff = None
    def test_identical(self):
        self.assertTrue(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, BASIC_EXAMPLE
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, BASIC_EXAMPLE
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])

    def test_tag_difference(self):
        self.assertFalse(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, WRONG_ROOT_TAG
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, WRONG_ROOT_TAG
        )[2], [
            '<knights (- peasants)>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights (- peasants)>',
        ])

    def test_extra_child(self):
        self.assertFalse(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, EXTRA_CHILD
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, EXTRA_CHILD
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '-  <knight found-grail="nope" iq="80">',
            '-    <name>Sir Robin</name>',
            '-    <nickname>The Not-So-Brave</nickname>',
            '-  </knight>',
            '</knights>',
        ])

    def test_wrong_attrib(self):
        self.assertFalse(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, WRONG_ATTRIB
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, WRONG_ATTRIB
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200 (- 70)">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])

    def test_ellipsed_text(self):
        self.assertTrue(ellipsing_comp.compare(
            BASIC_EXAMPLE, ELLIPSED_TEXT
        ))
        self.assertListEqual(ellipsing_comp.get_diff(
            BASIC_EXAMPLE, ELLIPSED_TEXT
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])

    def test_ellipsed_text_disabled(self):
        self.assertFalse(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, ELLIPSED_TEXT
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, ELLIPSED_TEXT
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad (- ...)</name>',
            '    <nickname>The Pure (- ...)</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])

    def test_ellipsed_tag(self):
        self.assertTrue(ellipsing_comp.compare(
            BASIC_EXAMPLE, ELLIPSED_TAG
        ))
        self.assertListEqual(ellipsing_comp.get_diff(
            BASIC_EXAMPLE, ELLIPSED_TAG
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])

    def test_ellipsed_tag_disabled(self):
        self.assertFalse(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, ELLIPSED_TAG
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, ELLIPSED_TAG
        )[2], [
            '<knights (- any)>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights (- any)>',
        ])

    def test_ellipsed_attrib(self):
        self.assertTrue(ellipsing_comp.compare(
            BASIC_EXAMPLE, ELLIPSED_ATTRIB
        ))
        self.assertListEqual(ellipsing_comp.get_diff(
            BASIC_EXAMPLE, ELLIPSED_ATTRIB
        )[2], [
            '<knights>',
            '  <knight found-grail="nope" iq="98">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])

    def test_ellipsed_attrib_disabled(self):
        self.assertFalse(non_ellipsing_comp.compare(
            BASIC_EXAMPLE, ELLIPSED_ATTRIB
        ))
        self.assertListEqual(non_ellipsing_comp.get_diff(
            BASIC_EXAMPLE, ELLIPSED_ATTRIB
        )[2], [
            '<knights>',
            '  <knight -found-grail="nope" -iq="98" +any="any">',
            '    <name>Sir Galahad</name>',
            '    <nickname>The Pure</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="90">',
            '    <name>Sir Lancelot</name>',
            '    <nickname>The Brave</nickname>',
            '  </knight>',
            '  <knight found-grail="nope" iq="200">',
            '    <name>Sir Bedevere</name>',
            '    <nickname>The Wise</nickname>',
            '  </knight>',
            '</knights>',
        ])
