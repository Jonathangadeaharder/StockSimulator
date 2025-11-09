"""
HTML Report Generator

Generate comprehensive HTML performance reports.
"""

from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.core.backtester import BacktestResult
from stocksimulator.reporting.charts import ChartGenerator


class HTMLReportGenerator:
    """Generate HTML performance reports with charts and statistics."""

    def __init__(self):
        """Initialize HTML report generator."""
        self.chart_generator = ChartGenerator()

    def generate_report(
        self,
        backtest_result: BacktestResult,
        output_file: str,
        strategy_description: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive HTML report.

        Args:
            backtest_result: Backtest result to report on
            output_file: Path to save HTML report
            strategy_description: Optional strategy description

        Returns:
            Path to generated report

        Example:
            >>> generator = HTMLReportGenerator()
            >>> generator.generate_report(result, 'reports/backtest_report.html')
        """
        summary = backtest_result.get_performance_summary()

        html = self._generate_html(
            backtest_result=backtest_result,
            summary=summary,
            strategy_description=strategy_description
        )

        # Create output directory if needed
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

        # Write file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_file

    def _generate_html(
        self,
        backtest_result: BacktestResult,
        summary: Dict,
        strategy_description: Optional[str]
    ) -> str:
        """Generate complete HTML document."""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtest Report - {backtest_result.strategy_name}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header(backtest_result, strategy_description)}
        {self._generate_summary_section(summary)}
        {self._generate_charts_section(backtest_result)}
        {self._generate_monthly_returns_section(backtest_result)}
        {self._generate_trades_section(backtest_result)}
        {self._generate_footer()}
    </div>
</body>
</html>'''
        return html

    def _get_css(self) -> str:
        """Get CSS styles."""
        return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .metric-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }
        .metric-value.positive {
            color: #28a745;
        }
        .metric-value.negative {
            color: #dc3545;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .footer {
            text-align: center;
            color: #666;
            padding: 20px;
            font-size: 0.9em;
        }
        .chart-container {
            margin: 30px 0;
        }
        '''

    def _generate_header(
        self,
        backtest_result: BacktestResult,
        strategy_description: Optional[str]
    ) -> str:
        """Generate report header."""
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        description = strategy_description or "No description provided"

        return f'''
        <div class="header">
            <h1>📊 Backtest Report</h1>
            <p><strong>Strategy:</strong> {backtest_result.strategy_name}</p>
            <p><strong>Description:</strong> {description}</p>
            <p><strong>Generated:</strong> {generated_at}</p>
        </div>
        '''

    def _generate_summary_section(self, summary: Dict) -> str:
        """Generate performance summary section."""
        total_return = summary['total_return']
        ann_return = summary['annualized_return']
        sharpe = summary['sharpe_ratio']
        max_dd = summary['max_drawdown']

        return_class = 'positive' if total_return > 0 else 'negative'
        sharpe_class = 'positive' if sharpe > 0 else 'negative'
        dd_class = 'negative'

        html = '''
        <div class="section">
            <h2>Performance Summary</h2>
            <div class="metrics-grid">
        '''

        metrics = [
            ('Total Return', f'{total_return:+.2f}%', return_class),
            ('Annualized Return', f'{ann_return:+.2f}%', return_class),
            ('Sharpe Ratio', f'{sharpe:.3f}', sharpe_class),
            ('Max Drawdown', f'{max_dd:.2f}%', dd_class),
            ('Sortino Ratio', f'{summary.get("sortino_ratio", 0):.3f}', 'positive'),
            ('Win Rate', f'{summary.get("win_rate", 0):.1f}%', 'positive'),
            ('Number of Trades', f'{summary.get("num_trades", 0)}', ''),
            ('Volatility', f'{summary.get("volatility", 0):.2f}%', ''),
        ]

        for label, value, css_class in metrics:
            html += f'''
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {css_class}">{value}</div>
                </div>
            '''

        html += '''
            </div>
        </div>
        '''

        return html

    def _generate_charts_section(self, backtest_result: BacktestResult) -> str:
        """Generate charts section."""
        # Extract data from equity curve
        dates = [point.date for point in backtest_result.equity_curve]
        values = [point.value for point in backtest_result.equity_curve]
        drawdowns = [point.drawdown_pct for point in backtest_result.equity_curve]

        equity_chart = self.chart_generator.generate_equity_curve(dates, values)
        drawdown_chart = self.chart_generator.generate_drawdown_chart(dates, drawdowns)

        return f'''
        <div class="section">
            <h2>Performance Charts</h2>
            <div class="chart-container">
                {equity_chart}
            </div>
            <div class="chart-container">
                {drawdown_chart}
            </div>
        </div>
        '''

    def _generate_monthly_returns_section(self, backtest_result: BacktestResult) -> str:
        """Generate monthly returns heatmap section."""
        # Calculate monthly returns from equity curve
        monthly_returns = self._calculate_monthly_returns(backtest_result.equity_curve)

        heatmap = self.chart_generator.generate_monthly_returns_heatmap(monthly_returns)

        return f'''
        <div class="section">
            <h2>Monthly Returns</h2>
            {heatmap}
        </div>
        '''

    def _calculate_monthly_returns(self, equity_curve) -> Dict[tuple, float]:
        """Calculate monthly returns from equity curve."""
        monthly_returns = {}
        current_month = None
        month_start_value = None

        for point in equity_curve:
            year_month = (point.date.year, point.date.month)

            if current_month != year_month:
                # New month
                if current_month is not None and month_start_value:
                    # Calculate return for previous month
                    prev_value = month_start_value
                    curr_value = prev_point_value
                    monthly_return = ((curr_value - prev_value) / prev_value) * 100
                    monthly_returns[current_month] = monthly_return

                current_month = year_month
                month_start_value = point.value

            prev_point_value = point.value

        # Handle last month
        if current_month and month_start_value:
            monthly_return = ((prev_point_value - month_start_value) / month_start_value) * 100
            monthly_returns[current_month] = monthly_return

        return monthly_returns

    def _generate_trades_section(self, backtest_result: BacktestResult) -> str:
        """Generate trades summary section."""
        if not backtest_result.trades:
            return '''
            <div class="section">
                <h2>Trades</h2>
                <p>No trades executed (buy-and-hold strategy)</p>
            </div>
            '''

        # Limit to last 50 trades for display
        recent_trades = backtest_result.trades[-50:]

        html = '''
        <div class="section">
            <h2>Recent Trades (Last 50)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Symbol</th>
                        <th>Quantity</th>
                        <th>Price</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
        '''

        for trade in reversed(recent_trades):
            html += f'''
                <tr>
                    <td>{trade.date}</td>
                    <td>{trade.transaction_type.value}</td>
                    <td>{trade.symbol}</td>
                    <td>{trade.quantity:.2f}</td>
                    <td>${trade.price:.2f}</td>
                    <td>${abs(trade.amount):.2f}</td>
                </tr>
            '''

        html += '''
                </tbody>
            </table>
        </div>
        '''

        return html

    def _generate_footer(self) -> str:
        """Generate report footer."""
        return '''
        <div class="footer">
            <p>Generated by StockSimulator - Historical Backtesting Platform</p>
            <p>Past performance is not indicative of future results</p>
        </div>
        '''
