import logging

from .emptyparser import EmptyParser
from .parser import Parser
from .saverparser import SaverParser
from .arxivparser import ArxivParser
from .springerparser import SpringerParser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

__all__ = ("EmptyParser", "SaverParser", "Parser", "ArxivParser", "SpringerParser")
