"""
Chart Generation

Create charts for performance reports using matplotlib.
"""

from typing import List, Dict, Any, Optional
from datetime import date
import sys
import os
import base64
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class ChartGenerator:
    """Generate charts for performance reporting."""

    def __init__(self, use_matplotlib: bool = True):
        """
        Initialize chart generator.

        Args:
            use_matplotlib: Try to use matplotlib for charts
        """
        self.use_matplotlib = use_matplotlib and self._check_matplotlib()

    def _check_matplotlib(self) -> bool:
        """Check if matplotlib is available."""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            return True
        except ImportError:
            return False

    def generate_equity_curve(
        self,
        dates: List[date],
        values: List[float],
        title: str = "Equity Curve"
    ) -> str:
        """
        Generate equity curve chart.

        Args:
            dates: List of dates
            values: Portfolio values
            title: Chart title

        Returns:
            Base64-encoded PNG image or HTML canvas fallback
        """
        if self.use_matplotlib:
            return self._generate_matplotlib_equity_curve(dates, values, title)
        else:
            return self._generate_html_equity_curve(dates, values, title)

    def _generate_matplotlib_equity_curve(
        self,
        dates: List[date],
        values: List[float],
        title: str
    ) -> str:
        """Generate equity curve using matplotlib."""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(dates, values, linewidth=2, color='#2E86AB')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.grid(True, alpha=0.3)

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto;">'

    def _generate_html_equity_curve(
        self,
        dates: List[date],
        values: List[float],
        title: str
    ) -> str:
        """Generate simple HTML/SVG equity curve (fallback)."""
        if not dates or not values:
            return "<p>No data available</p>"

        # Simple SVG line chart
        width, height = 800, 400
        padding = 40

        # Normalize data
        min_val, max_val = min(values), max(values)
        val_range = max_val - min_val if max_val > min_val else 1

        points = []
        for i, (d, v) in enumerate(zip(dates, values)):
            x = padding + (i / (len(values) - 1 if len(values) > 1 else 1)) * (width - 2 * padding)
            y = height - padding - ((v - min_val) / val_range) * (height - 2 * padding)
            points.append(f"{x:.1f},{y:.1f}")

        polyline = " ".join(points)

        return f'''
        <div style="text-align: center;">
            <h3>{title}</h3>
            <svg width="{width}" height="{height}" style="border: 1px solid #ccc;">
                <polyline points="{polyline}"
                          style="fill: none; stroke: #2E86AB; stroke-width: 2" />
                <text x="{padding}" y="20" font-size="12">
                    ${max_val:,.0f}
                </text>
                <text x="{padding}" y="{height - padding + 20}" font-size="12">
                    ${min_val:,.0f}
                </text>
            </svg>
        </div>
        '''

    def generate_drawdown_chart(
        self,
        dates: List[date],
        drawdowns: List[float],
        title: str = "Drawdown"
    ) -> str:
        """
        Generate drawdown chart.

        Args:
            dates: List of dates
            drawdowns: Drawdown percentages (negative values)
            title: Chart title

        Returns:
            Base64-encoded PNG image or HTML canvas fallback
        """
        if self.use_matplotlib:
            return self._generate_matplotlib_drawdown(dates, drawdowns, title)
        else:
            return self._generate_html_drawdown(dates, drawdowns, title)

    def _generate_matplotlib_drawdown(
        self,
        dates: List[date],
        drawdowns: List[float],
        title: str
    ) -> str:
        """Generate drawdown chart using matplotlib."""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates

        fig, ax = plt.subplots(figsize=(12, 4))

        ax.fill_between(dates, drawdowns, 0, alpha=0.3, color='red')
        ax.plot(dates, drawdowns, linewidth=2, color='darkred')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.grid(True, alpha=0.3)

        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)

        plt.tight_layout()

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.read()).decode()
        plt.close()

        return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto;">'

    def _generate_html_drawdown(
        self,
        dates: List[date],
        drawdowns: List[float],
        title: str
    ) -> str:
        """Generate simple HTML/SVG drawdown chart."""
        return "<p>Drawdown chart (install matplotlib for visualization)</p>"

    def generate_monthly_returns_heatmap(
        self,
        monthly_returns: Dict[tuple, float],
        title: str = "Monthly Returns"
    ) -> str:
        """
        Generate monthly returns heatmap.

        Args:
            monthly_returns: Dict of (year, month) -> return percentage
            title: Chart title

        Returns:
            HTML table heatmap
        """
        if not monthly_returns:
            return "<p>No monthly returns data</p>"

        # Group by year
        years = sorted(set(year for year, month in monthly_returns.keys()))
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        html = f'<h3>{title}</h3>'
        html += '<table style="border-collapse: collapse; margin: auto;">'
        html += '<tr><th>Year</th>'
        for month in months:
            html += f'<th>{month}</th>'
        html += '<th>YTD</th></tr>'

        for year in years:
            html += f'<tr><td style="font-weight: bold;">{year}</td>'

            ytd_return = 1.0
            for month_idx in range(1, 13):
                ret = monthly_returns.get((year, month_idx), None)

                if ret is not None:
                    ytd_return *= (1 + ret / 100)

                    # Color coding
                    if ret > 0:
                        color = f'rgba(0, 128, 0, {min(abs(ret) / 10, 0.8)})'
                    elif ret < 0:
                        color = f'rgba(255, 0, 0, {min(abs(ret) / 10, 0.8)})'
                    else:
                        color = 'rgba(200, 200, 200, 0.3)'

                    html += f'<td style="background-color: {color}; padding: 5px; text-align: center; border: 1px solid #ddd;">{ret:+.1f}%</td>'
                else:
                    html += '<td style="padding: 5px; text-align: center; border: 1px solid #ddd;">-</td>'

            ytd_pct = (ytd_return - 1) * 100
            ytd_color = 'green' if ytd_pct > 0 else 'red'
            html += f'<td style="font-weight: bold; color: {ytd_color}; padding: 5px; text-align: center; border: 1px solid #ddd;">{ytd_pct:+.1f}%</td>'
            html += '</tr>'

        html += '</table>'
        return html
