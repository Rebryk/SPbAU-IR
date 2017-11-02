import logging

from .textprocessor import TextProcessor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

__all__ = ("TextProcessor")
