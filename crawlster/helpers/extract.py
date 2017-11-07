from bs4 import BeautifulSoup

try:
    import lxml
except ImportError:
    lxml = None

from crawlster.helpers.base import BaseHelper


class ExtractHelper(BaseHelper):
    name = 'extract'

    def __init__(self):
        super(ExtractHelper, self).__init__()

    def css(self, text, selector, attr=None):
        """Extracts data using css selector

        Returns a list of elements (as strings) with the extracted data

        Args:
            text (str):
                data to search in
            selector:
                the CSS selector
            attr (str or None):
                if present, returns a list of the attributes of the extracted
                items
        """
        items = BeautifulSoup(text, 'html.parser').select(selector)
        if attr:
            return [i[attr] for i in items if attr in i.attrs]
        else:
            return [str(i) for i in items]

    def xpath(self, text, selector):
        if not lxml:
            raise RuntimeError('lxml in required to use xpath')
        from lxml import html
        return html.fromstring(text).xpath(selector)
