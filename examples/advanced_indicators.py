# @structurelint:no-test
"""
Example: Advanced Technical Indicators

Demonstrates how to use advanced indicators like Ichimoku, VWAP, Supertrend.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from stocksimulator.data import load_from_csv
from stocksimulator.indicators import (
    IchimokuCloud, VWAP, Supertrend, DonchianChannels,
    MACD, RSI, BollingerBands
)


def main():
    """Demonstrate advanced technical indicators."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "ADVANCED TECHNICAL INDICATORS" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Load data
    print("Loading market data...")
    # Try both paths (running from root or examples dir)
    try:
        spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', 'historical_data')
    except FileNotFoundError:
        spy_data = load_from_csv('sp500_stooq_daily.csv', 'SPY', '../historical_data')
    print(f"✓ Loaded {len(spy_data.data)} data points")
    print()

    # Use recent data for examples
    recent_data = spy_data.data[-100:]  # Last 100 days
    current_price = recent_data[-1].close

    print(f"Current SPY Price: ${current_price:.2f}")
    print(f"Analyzing last {len(recent_data)} trading days...")
    print()

    # Example 1: Ichimoku Cloud
    print("=" * 80)
    print("ICHIMOKU CLOUD")
    print("=" * 80)
    print()
    print("Ichimoku is a comprehensive indicator showing support, resistance,")
    print("trend direction, and momentum all in one chart.")
    print()

    ichimoku = IchimokuCloud()
    ich_result = ichimoku.calculate(recent_data)
    ich_signal = ichimoku.get_signal(recent_data)

    print(f"Tenkan-sen (Conversion):    ${ich_result.tenkan_sen:.2f}")
    print(f"Kijun-sen (Base):           ${ich_result.kijun_sen:.2f}")
    print(f"Senkou Span A (Lead A):     ${ich_result.senkou_span_a:.2f}")
    print(f"Senkou Span B (Lead B):     ${ich_result.senkou_span_b:.2f}")
    print(f"Chikou Span (Lagging):      ${ich_result.chikou_span:.2f}")
    print()

    cloud_top = max(ich_result.senkou_span_a, ich_result.senkou_span_b)
    cloud_bottom = min(ich_result.senkou_span_a, ich_result.senkou_span_b)

    print(f"Cloud Range: ${cloud_bottom:.2f} - ${cloud_top:.2f}")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Price vs Cloud: ", end="")

    if current_price > cloud_top:
        print("Above cloud (Bullish)")
    elif current_price < cloud_bottom:
        print("Below cloud (Bearish)")
    else:
        print("Inside cloud (Neutral)")

    print(f"\nSignal: {ich_signal.upper()}")
    print()

    # Example 2: VWAP
    print("=" * 80)
    print("VWAP (Volume Weighted Average Price)")
    print("=" * 80)
    print()
    print("VWAP shows the average price weighted by volume.")
    print("Often used as a benchmark for intraday trades.")
    print()

    vwap = VWAP()
    vwap_value = vwap.calculate(recent_data, period=20)
    vwap_signal = vwap.get_signal(recent_data, period=20)

    print(f"20-day VWAP:     ${vwap_value:.2f}")
    print(f"Current Price:   ${current_price:.2f}")
    print(f"Difference:      ${current_price - vwap_value:+.2f} ({((current_price / vwap_value - 1) * 100):+.2f}%)")
    print(f"\nSignal: {vwap_signal.upper()}")
    print()

    if current_price > vwap_value:
        print("→ Price above VWAP suggests buying pressure")
    else:
        print("→ Price below VWAP suggests selling pressure")
    print()

    # Example 3: Supertrend
    print("=" * 80)
    print("SUPERTREND")
    print("=" * 80)
    print()
    print("Supertrend combines ATR and price to identify trend direction.")
    print("Simple and effective for trend-following strategies.")
    print()

    supertrend = Supertrend(period=10, multiplier=3.0)
    st_result = supertrend.calculate(recent_data)
    st_signal = supertrend.get_signal(recent_data)

    print(f"Supertrend Value:  ${st_result.supertrend:.2f}")
    print(f"Current Price:     ${current_price:.2f}")
    print(f"Direction:         {'UPTREND' if st_result.direction == 1 else 'DOWNTREND'}")
    print(f"\nSignal: {st_signal.upper()}")
    print()

    # Example 4: Donchian Channels
    print("=" * 80)
    print("DONCHIAN CHANNELS")
    print("=" * 80)
    print()
    print("Donchian Channels show the highest high and lowest low")
    print("over a period. Used for breakout strategies.")
    print()

    donchian = DonchianChannels(period=20)
    dc_result = donchian.calculate(recent_data)
    dc_signal = donchian.get_signal(recent_data)

    print(f"Upper Channel:     ${dc_result.upper:.2f}")
    print(f"Middle Line:       ${dc_result.middle:.2f}")
    print(f"Lower Channel:     ${dc_result.lower:.2f}")
    print(f"Current Price:     ${current_price:.2f}")
    print(f"\nSignal: {dc_signal.upper()}")
    print()

    channel_width = dc_result.upper - dc_result.lower
    price_position = (current_price - dc_result.lower) / channel_width * 100

    print(f"Channel Width:     ${channel_width:.2f}")
    print(f"Price Position:    {price_position:.1f}% of channel")
    print()

    # Example 5: Combining Multiple Indicators
    print("=" * 80)
    print("COMBINING INDICATORS FOR CONSENSUS")
    print("=" * 80)
    print()
    print("Using multiple indicators together can improve signal quality.")
    print()

    # Tally signals from advanced indicators
    signals = {
        'Ichimoku': ich_signal,
        'VWAP': vwap_signal,
        'Supertrend': st_signal,
        'Donchian': dc_signal,
    }

    print("Indicator Consensus:")
    print("-" * 80)
    for indicator, signal in signals.items():
        emoji = "🟢" if signal == 'bullish' else ("🔴" if signal == 'bearish' else "⚪")
        print(f"  {emoji} {indicator:<15} → {signal.upper()}")

    bullish_count = sum(1 for s in signals.values() if s == 'bullish')
    bearish_count = sum(1 for s in signals.values() if s == 'bearish')

    print()
    print(f"Bullish signals: {bullish_count}/{len(signals)}")
    print(f"Bearish signals: {bearish_count}/{len(signals)}")
    print()

    if bullish_count > bearish_count:
        print("→ OVERALL CONSENSUS: BULLISH")
    elif bearish_count > bullish_count:
        print("→ OVERALL CONSENSUS: BEARISH")
    else:
        print("→ OVERALL CONSENSUS: NEUTRAL/MIXED")
    print()

    print("=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print()
    print("1. Each indicator provides a different perspective:")
    print("   - Ichimoku: Comprehensive multi-faceted analysis")
    print("   - VWAP: Volume-weighted fair value")
    print("   - Supertrend: Clear trend direction")
    print("   - Donchian: Breakout opportunities")
    print()
    print("2. Use multiple indicators to confirm signals")
    print("3. Different timeframes may give different signals")
    print("4. No single indicator is perfect - combine with risk management")
    print()


if __name__ == '__main__':
    main()
