# based on: https://github.com/romilly/markdown-builder/blob/master/src/markdown_builder/document.py
"""Builds a Markdown Document"""

from io import StringIO
from pathlib import Path


def bullet(text):
    """ turns raw text into a markdown bullet"""
    return '- ' + text


def make_link(text: str, link: str) -> str:

    """
    Creates a markdown link

    :param text: the text to display
    :param link: the link target
    :return: the formatted link
    """
    return '[%s](%s)' % (text, link)

# TODO: Add code to support inline bold, italic etc.


class MarkdownDocument:
    def __init__(self, indentation=None):

        #: A container for the text of the markdown document
        self._contents = StringIO()

        #: a string prefix used to indent text
        self.indentation = indentation if indentation else '    '

    def append_text(self, text: str) -> 'MarkdownDocument':
        """

        :param text:
        :return:
        """
        self._contents.write(text)
        return self

    def append_text_indented(self, text: str, depth: int):
        text = (depth*self.indentation)+text
        self.append_text(text)

    def append_link(self, text: str, link, depth: int = 0):
        self.append_text_indented(make_link(text, link), depth)

    def append_bulleted_link(self, text: str, link: str, depth: int = 0):
        self.append_text_indented(bullet(make_link(text, link)), depth)

    def append_bullet(self, text: str, depth=0):
        self.append_text_indented(bullet(text), depth)

    def close(self):
        self._contents.close()

    def contents(self):
        result = self._contents.getvalue()
        return result

    def append_heading(self, text, level=1):
        # self.append_text(level*'#' +' ' + text)
        self.append_text(f'*{text}*')

    def add_bold(self, text, breakline: bool = False):
        self.append_text(f'*{text}*')
        if breakline:
            self.append_text('\n')
        return self

    def add_normal(self, text, breakline: bool = False):
        self.append_text(text)
        if breakline:
            self.append_text('\n')
        return self

    def add_italic(self, text, breakline: bool = False):
        self.append_text(f'_{text}_')
        if breakline:
            self.append_text('\n')
        return self

    def add_underline(self, text, breakline: bool = False):
        self.append_text(f'__{text}__')
        if breakline:
            self.append_text('\n')
        return self

    def add_inline(self, text, breakline: bool = False):
        self.append_text(f'`{text}`')
        if breakline:
            self.append_text('\n')
        return self

    def add_block(self, text, breakline: bool = False):
        self.append_text(f'>{text}')
        if breakline:
            self.append_text('\n')
        return self

    def append_image_link(self, node_text, location, decoration):
        self.append_text('\n\n![%s](%s)%s\n\n' % (node_text, location, decoration))

    def new_page(self):
        self.append_text('\n\n\\newpage\n\n')

    def save(self, filepath: Path) -> None:
        filepath.write_text(self.contents())