"""CSS Selectors based on XPath.

This module supports selecting XML/HTML tags based on CSS selectors.
See the `CSSSelector` class for details.

This is a thin wrapper around cssselect.
"""

import sys
from lxml import etree

## Work-around the lack of absolute import in Python 2.4
#from __future__ import absolute_import
#from cssselect import ...
try:
    external_cssselect = __import__('cssselect')
except ImportError:
    raise ImportError('cssselect seems not to be installed. '
                      'See http://packages.python.org/cssselect/')

SelectorSyntaxError = external_cssselect.SelectorSyntaxError
ExpressionError = external_cssselect.ExpressionError
SelectorError = external_cssselect.SelectorError


__all__ = ['SelectorSyntaxError', 'ExpressionError', 'SelectorError',
           'CSSSelector']


class LxmlTranslator(external_cssselect.GenericTranslator):
    """
    A custom CSS selector to XPath translator with lxml-specific extensions.
    """
    def xpath_contains_function(self, xpath, function):
        xpath.add_condition(
            'contains(__lxml_internal_css:lower-case(string(.)), %s)'
            % self.xpath_literal(function.arguments.lower()))
        return xpath


class LxmlHTMLTranslator(LxmlTranslator, external_cssselect.HTMLTranslator):
    """
    lxml extensions + HTML support.
    """


def _make_lower_case(context, s):
    return s.lower()

ns = etree.FunctionNamespace('http://codespeak.net/lxml/css/')
ns.prefix = '__lxml_internal_css'
ns['lower-case'] = _make_lower_case


class CSSSelector(etree.XPath):
    """A CSS selector.

    Usage::

        >>> from lxml import etree, cssselect
        >>> select = cssselect.CSSSelector("a tag > child")

        >>> root = etree.XML("<a><b><c/><tag><child>TEXT</child></tag></b></a>")
        >>> [ el.tag for el in select(root) ]
        ['child']

    To use CSS namespaces, you need to pass a prefix-to-namespace
    mapping as ``namespaces`` keyword argument::

        >>> rdfns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        >>> select_ns = cssselect.CSSSelector('root > rdf|Description',
        ...                                   namespaces={'rdf': rdfns})

        >>> rdf = etree.XML((
        ...     '<root xmlns:rdf="%s">'
        ...       '<rdf:Description>blah</rdf:Description>'
        ...     '</root>') % rdfns)
        >>> [(el.tag, el.text) for el in select_ns(rdf)]
        [('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description', 'blah')]

    """
    def __init__(self, css, namespaces=None, translator='xml'):
        if translator == 'xml':
            translator = LxmlTranslator()
        elif translator == 'html':
            translator = LxmlHTMLTranslator()
        elif translator == 'xhtml':
            translator = LxmlHTMLTranslator(xhtml=True)
        path = translator.css_to_xpath(css)
        etree.XPath.__init__(self, path, namespaces=namespaces)
        self.css = css

    def __repr__(self):
        return '<%s %s for %r>' % (
            self.__class__.__name__,
            hex(abs(id(self)))[2:],
            self.css)
