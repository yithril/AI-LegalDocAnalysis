"""
Text-based file extraction strategies.

Handles plain text files like .txt, .md and structured text like .json, .xml, .yaml
CSV files are handled by the dedicated CSVStrategy.
Excel files are handled by the dedicated ExcelStrategy.
"""

from .plain_text_strategy import PlainTextStrategy
from .csv_strategy import CSVStrategy
from .rtf_strategy import RTFStrategy
from .excel_strategy import ExcelStrategy

__all__ = ['PlainTextStrategy', 'CSVStrategy', 'RTFStrategy', 'ExcelStrategy'] 