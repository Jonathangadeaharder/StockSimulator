"""
Performance Reporting

Generate HTML reports with charts and statistics.
"""

from .html_report import HTMLReportGenerator
from .charts import ChartGenerator

__all__ = [
    'HTMLReportGenerator',
    'ChartGenerator',
]
