import logging

from .emptyparser import EmptyParser
from .parser import Parser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

__all__ = ("EmptyParser", "Parser")
