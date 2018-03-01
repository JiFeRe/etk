from typing import List
from enum import Enum, auto
from bs4 import BeautifulSoup
from etk.extractor import Extractor, InputType
from etk.etk_extraction import Extraction
from etk.extractors.readability.readability import Document


class Strategy(Enum):
    """
    ALL_TEXT: return all visible text in an HTML page
    MAIN_CONTENT_STRICT: MAIN_CONTENT_STRICT: return the main content of the page without boiler plate (menu, ads...)
    MAIN_CONTENT_RELAXED: variant of MAIN_CONTENT_STRICT with less strict rules
    """
    ALL_TEXT = auto()
    MAIN_CONTENT_STRICT = auto()
    MAIN_CONTENT_RELAXED = auto()


class HTMLContentExtractor(Extractor):
    """
    Extracts text from HTML pages.

    Uses readability and BeautifulSoup
    """

    def __init__(self):
        Extractor.__init__(self,
                           input_type=InputType.HTML,
                           category="HTML extractor",
                           name="HTML content extractor")

    def extract(self, html_text: str, options: dict = None) \
            -> List[Extraction]:
        """
        Extracts text from an HTML page using a variety of strategies

        Args:
            html_text (): html page in string
            options: {'strategy': strategy () -> one of Strategy.ALL_TEXT, Strategy.MAIN_CONTENT_STRICT \
                and Strategy.MAIN_CONTENT_RELAXED}

        Returns: a list of Extraction(s) of a str, typically a singleton list with the extracted text
        """
        print(options)
        if 'strategy' in options:
            strategy = options['strategy']
        else:
            strategy = Strategy.ALL_TEXT

        try:
            if html_text:
                if strategy == Strategy.ALL_TEXT:
                    # TODO use BeautifulSoup to get all visible content of the html page
                    return []
                else:
                    relax = strategy == Strategy.MAIN_CONTENT_RELAXED
                    readable = Document(html_text, recallPriority=relax).summary(html_partial=False)
                    cleantext = BeautifulSoup(readable.encode('utf-8'), 'lxml').strings
                    readability_text = ' '.join(cleantext)
                    return [Extraction(self.wrap_html_content(readability_text))]
            else:
                return []
        except Exception as e:
            print('Error in extracting readability %s' % e)
            return []


    @staticmethod
    def wrap_html_content(readability_text: str = ''):
        return {'value': readability_text, 'confidence': 1.0, 'context': ''}

