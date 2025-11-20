"""
Market Regime Detection

Identifies market regimes (normal, pre-crisis, crisis, recovery) to enable
regime-aware portfolio strategies.

Uses multiple signals:
- Drawdown depth and duration
- Volatility (VIX proxy)
- Price momentum
- Moving average trends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import date, timedelta
from enum import Enum
from dataclasses import dataclass


class MarketRegime(Enum):
    """Market regime classifications."""
    NORMAL = "normal"
    PRE_CRISIS = "pre_crisis"  # Elevated risk, bubble conditions
    CRISIS = "crisis"          # Active crash/bear market
    RECOVERY = "recovery"      # Post-crisis recovery phase


@dataclass
class RegimeInfo:
    """Information about a market regime period."""
    regime: MarketRegime
    start_date: date
    end_date: date
    severity: float  # 0-1, severity of crisis (0 = mild, 1 = severe)
    characteristics: Dict[str, float]  # Drawdown, volatility, etc.


class MarketRegimeDetector:
    """
    Detects market regimes using multiple technical indicators.

    Combines drawdown analysis, volatility, and momentum to classify
    market conditions into distinct regimes.
    """

    def __init__(
        self,
        crisis_drawdown_threshold: float = -0.15,      # 15% drawdown = crisis
        pre_crisis_vol_multiplier: float = 1.5,        # 1.5x normal vol = warning
        recovery_threshold: float = 0.75,              # Recovered 75% of losses
        lookback_days: int = 252                       # 1 year lookback
    ):
        """
        Initialize regime detector.

        Args:
            crisis_drawdown_threshold: Drawdown % that defines crisis start
            pre_crisis_vol_multiplier: Volatility multiplier for pre-crisis detection
            recovery_threshold: Fraction of losses recovered to exit crisis
            lookback_days: Days to look back for volatility calculation
        """
        self.crisis_drawdown_threshold = crisis_drawdown_threshold
        self.pre_crisis_vol_multiplier = pre_crisis_vol_multiplier
        self.recovery_threshold = recovery_threshold
        self.lookback_days = lookback_days

    def detect_regimes(
        self,
        price_data: pd.DataFrame,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """
        Detect market regimes over time.

        Args:
            price_data: DataFrame with 'Date' and 'Close' columns
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            DataFrame with columns: Date, Close, Regime, Drawdown, Volatility, Severity

        Example:
            >>> detector = MarketRegimeDetector()
            >>> regimes = detector.detect_regimes(sp500_data)
            >>> print(regimes[regimes['Regime'] == 'crisis'])
        """
        df = price_data.copy()
        df['Date'] = pd.to_datetime(df['Date'])

        if start_date:
            df = df[df['Date'] >= pd.Timestamp(start_date)]
        if end_date:
            df = df[df['Date'] <= pd.Timestamp(end_date)]

        df = df.sort_values('Date').reset_index(drop=True)

        # Calculate indicators
        df['Returns'] = df['Close'].pct_change()
        df['CumulativeMax'] = df['Close'].expanding().max()
        df['Drawdown'] = (df['Close'] / df['CumulativeMax']) - 1

        # Rolling volatility
        df['Volatility'] = df['Returns'].rolling(
            window=min(self.lookback_days, len(df))
        ).std() * np.sqrt(252)

        # Historical median volatility (for pre-crisis detection)
        df['MedianVol'] = df['Volatility'].expanding().median()

        # 200-day moving average for trend
        df['MA200'] = df['Close'].rolling(window=min(200, len(df))).mean()

        # Detect regimes
        df['Regime'] = df.apply(
            lambda row: self._classify_regime(row, df),
            axis=1
        )

        # Calculate severity (0-1 scale)
        df['Severity'] = df.apply(
            lambda row: self._calculate_severity(row),
            axis=1
        )

        return df[['Date', 'Close', 'Regime', 'Drawdown', 'Volatility', 'Severity']]

    def get_regime_periods(
        self,
        regime_data: pd.DataFrame,
        min_duration_days: int = 20
    ) -> List[RegimeInfo]:
        """
        Extract distinct regime periods.

        Args:
            regime_data: Output from detect_regimes()
            min_duration_days: Minimum days for a regime to be considered

        Returns:
            List of RegimeInfo objects

        Example:
            >>> periods = detector.get_regime_periods(regimes)
            >>> crisis_periods = [p for p in periods if p.regime == MarketRegime.CRISIS]
            >>> for period in crisis_periods:
            ...     print(f"{period.start_date} to {period.end_date}: {period.severity:.2f}")
        """
        periods = []
        current_regime = None
        start_date = None
        characteristics = {}

        for idx, row in regime_data.iterrows():
            regime = MarketRegime(row['Regime'])

            if regime != current_regime:
                # Save previous period
                if current_regime is not None and start_date is not None:
                    duration = (row['Date'] - start_date).days

                    if duration >= min_duration_days:
                        periods.append(RegimeInfo(
                            regime=current_regime,
                            start_date=start_date.date(),
                            end_date=row['Date'].date(),
                            severity=np.mean(list(characteristics.values())),
                            characteristics=characteristics.copy()
                        ))

                # Start new period
                current_regime = regime
                start_date = row['Date']
                characteristics = {
                    'drawdown': [],
                    'volatility': [],
                    'severity': []
                }

            # Accumulate characteristics
            if not pd.isna(row['Drawdown']):
                characteristics['drawdown'].append(row['Drawdown'])
            if not pd.isna(row['Volatility']):
                characteristics['volatility'].append(row['Volatility'])
            if not pd.isna(row['Severity']):
                characteristics['severity'].append(row['Severity'])

        # Save final period
        if current_regime is not None and start_date is not None:
            periods.append(RegimeInfo(
                regime=current_regime,
                start_date=start_date.date(),
                end_date=regime_data.iloc[-1]['Date'].date(),
                severity=np.mean(list(characteristics.values())),
                characteristics=characteristics.copy()
            ))

        return periods

    def _classify_regime(self, row: pd.Series, full_df: pd.DataFrame) -> str:
        """Classify a single data point into a regime."""

        drawdown = row['Drawdown']
        volatility = row['Volatility']
        median_vol = row['MedianVol']
        close = row['Close']
        ma200 = row['MA200']

        # Crisis: Significant drawdown
        if drawdown < self.crisis_drawdown_threshold:
            return MarketRegime.CRISIS.value

        # Recovery: Recovering from recent crisis
        # Check if we were recently in crisis
        idx = row.name
        if idx > 60:  # Need history to detect recovery
            recent_dd = full_df.loc[max(0, idx-60):idx, 'Drawdown']
            if (recent_dd < self.crisis_drawdown_threshold).any():
                # Were in crisis recently
                if drawdown > self.crisis_drawdown_threshold * self.recovery_threshold:
                    # Recovering (drawdown improving)
                    return MarketRegime.RECOVERY.value

        # Pre-crisis: Elevated volatility or extended rally
        if not pd.isna(median_vol) and median_vol > 0:
            if volatility > median_vol * self.pre_crisis_vol_multiplier:
                # High volatility without drawdown = pre-crisis warning
                return MarketRegime.PRE_CRISIS.value

        # Check for overextension (price far above MA200)
        if not pd.isna(ma200) and ma200 > 0:
            if close > ma200 * 1.15:  # 15% above trend
                return MarketRegime.PRE_CRISIS.value

        # Default: Normal regime
        return MarketRegime.NORMAL.value

    def _calculate_severity(self, row: pd.Series) -> float:
        """
        Calculate regime severity (0-1).

        0 = Normal/benign
        1 = Severe crisis
        """
        regime = row['Regime']
        drawdown = abs(row['Drawdown'])
        volatility = row['Volatility']

        if regime == MarketRegime.NORMAL.value:
            return 0.0

        elif regime == MarketRegime.PRE_CRISIS.value:
            # Severity based on volatility elevation
            return min(0.3, drawdown * 2 + 0.1)

        elif regime == MarketRegime.CRISIS.value:
            # Severity based on drawdown depth
            # 15% DD = 0.3, 30% DD = 0.6, 50% DD = 1.0
            severity = min(1.0, drawdown / 0.5)
            return severity

        elif regime == MarketRegime.RECOVERY.value:
            # Recovery severity diminishes as recovery progresses
            return min(0.5, drawdown * 2)

        return 0.0


class HistoricalCrisisDatabase:
    """
    Database of known historical crises for reference and validation.

    Includes major market downturns since 1950.
    """

    HISTORICAL_CRISES = [
        {
            'name': '1973-1974 Oil Crisis',
            'start': '1973-01-01',
            'end': '1974-10-31',
            'peak_drawdown': -0.48,
            'duration_days': 693,
            'severity': 0.95
        },
        {
            'name': '1987 Black Monday',
            'start': '1987-08-01',
            'end': '1987-12-31',
            'peak_drawdown': -0.34,
            'duration_days': 152,
            'severity': 0.70
        },
        {
            'name': '2000-2002 Dot-com Crash',
            'start': '2000-03-01',
            'end': '2002-10-31',
            'peak_drawdown': -0.49,
            'duration_days': 974,
            'severity': 0.98
        },
        {
            'name': '2007-2009 Financial Crisis',
            'start': '2007-10-01',
            'end': '2009-03-31',
            'peak_drawdown': -0.57,
            'duration_days': 547,
            'severity': 1.00
        },
        {
            'name': '2011 European Debt Crisis',
            'start': '2011-05-01',
            'end': '2011-10-31',
            'peak_drawdown': -0.19,
            'duration_days': 184,
            'severity': 0.40
        },
        {
            'name': '2015-2016 China Slowdown',
            'start': '2015-08-01',
            'end': '2016-02-29',
            'peak_drawdown': -0.14,
            'duration_days': 212,
            'severity': 0.30
        },
        {
            'name': '2018 Q4 Correction',
            'start': '2018-10-01',
            'end': '2018-12-31',
            'peak_drawdown': -0.20,
            'duration_days': 92,
            'severity': 0.42
        },
        {
            'name': '2020 COVID-19 Crash',
            'start': '2020-02-01',
            'end': '2020-04-30',
            'peak_drawdown': -0.34,
            'duration_days': 89,
            'severity': 0.70
        },
        {
            'name': '2022 Bear Market',
            'start': '2022-01-01',
            'end': '2022-10-31',
            'peak_drawdown': -0.25,
            'duration_days': 303,
            'severity': 0.52
        }
    ]

    @classmethod
    def get_crisis_periods(cls) -> List[Tuple[date, date, str]]:
        """Get list of (start_date, end_date, name) for all crises."""
        periods = []
        for crisis in cls.HISTORICAL_CRISES:
            start = pd.to_datetime(crisis['start']).date()
            end = pd.to_datetime(crisis['end']).date()
            name = crisis['name']
            periods.append((start, end, name))
        return periods

    @classmethod
    def is_crisis_period(cls, check_date: date) -> Optional[str]:
        """
        Check if a date falls within a known crisis.

        Returns:
            Crisis name if in crisis period, None otherwise
        """
        for crisis in cls.HISTORICAL_CRISES:
            start = pd.to_datetime(crisis['start']).date()
            end = pd.to_datetime(crisis['end']).date()
            if start <= check_date <= end:
                return crisis['name']
        return None


def visualize_regimes(regime_data: pd.DataFrame, title: str = "Market Regimes"):
    """
    Visualize market regimes over time.

    Args:
        regime_data: Output from MarketRegimeDetector.detect_regimes()
        title: Plot title
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("matplotlib not available for visualization")
        return

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Plot 1: Price with regime background
    ax1.plot(regime_data['Date'], regime_data['Close'], 'k-', linewidth=1)

    # Color background by regime
    regime_colors = {
        'normal': 'lightgreen',
        'pre_crisis': 'yellow',
        'crisis': 'red',
        'recovery': 'lightblue'
    }

    for regime, color in regime_colors.items():
        mask = regime_data['Regime'] == regime
        if mask.any():
            ax1.fill_between(
                regime_data['Date'],
                0,
                regime_data['Close'].max() * 1.1,
                where=mask,
                alpha=0.2,
                color=color,
                label=regime.replace('_', ' ').title()
            )

    ax1.set_ylabel('Price')
    ax1.set_title(title)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Drawdown
    ax2.fill_between(
        regime_data['Date'],
        regime_data['Drawdown'] * 100,
        0,
        alpha=0.3,
        color='red'
    )
    ax2.plot(regime_data['Date'], regime_data['Drawdown'] * 100, 'r-')
    ax2.axhline(y=-15, color='darkred', linestyle='--', label='Crisis Threshold')
    ax2.set_ylabel('Drawdown (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Severity
    ax3.fill_between(
        regime_data['Date'],
        regime_data['Severity'] * 100,
        0,
        alpha=0.3,
        color='purple'
    )
    ax3.plot(regime_data['Date'], regime_data['Severity'] * 100, 'purple')
    ax3.set_ylabel('Severity (%)')
    ax3.set_xlabel('Date')
    ax3.grid(True, alpha=0.3)

    # Format x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # Demo
    from stocksimulator.data import MultiAssetDataLoader

    loader = MultiAssetDataLoader()
    sp500 = loader.load_asset('SP500', start_date=date(1950, 1, 1))

    print("Detecting market regimes...")
    detector = MarketRegimeDetector()
    regimes = detector.detect_regimes(sp500)

    print(f"\nTotal days: {len(regimes)}")
    print("\nRegime distribution:")
    print(regimes['Regime'].value_counts())

    print("\n\nMajor crisis periods detected:")
    periods = detector.get_regime_periods(regimes, min_duration_days=60)

    crisis_periods = [p for p in periods if p.regime == MarketRegime.CRISIS]
    for period in crisis_periods:
        print(f"\n{period.start_date} to {period.end_date}")
        print(f"  Duration: {(period.end_date - period.start_date).days} days")
        print(f"  Severity: {period.severity:.2f}")

        # Check against historical database
        crisis_name = HistoricalCrisisDatabase.is_crisis_period(period.start_date)
        if crisis_name:
            print(f"  Matches: {crisis_name}")
