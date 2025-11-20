"""
Market Regime Detection and Analysis

Tools for identifying market regimes and building regime-aware strategies.
"""

from .regime_detector import (
    MarketRegimeDetector,
    MarketRegime,
    RegimeInfo,
    HistoricalCrisisDatabase,
    visualize_regimes
)

from .regime_strategies import (
    RegimeAwareStrategy,
    DefensiveToAggressiveStrategy,
    CrisisOpportunisticStrategy,
    AdaptiveAllWeatherStrategy,
    create_custom_regime_strategy,
    DEFENSIVE_PORTFOLIOS,
    AGGRESSIVE_PORTFOLIOS
)

from .crisis_rebalancer import (
    CrisisRebalancer,
    RebalancingStrategy,
    RebalancingSchedule,
    TransitionResult,
    compare_rebalancing_strategies
)

__all__ = [
    # Regime Detection
    'MarketRegimeDetector',
    'MarketRegime',
    'RegimeInfo',
    'HistoricalCrisisDatabase',
    'visualize_regimes',

    # Regime Strategies
    'RegimeAwareStrategy',
    'DefensiveToAggressiveStrategy',
    'CrisisOpportunisticStrategy',
    'AdaptiveAllWeatherStrategy',
    'create_custom_regime_strategy',
    'DEFENSIVE_PORTFOLIOS',
    'AGGRESSIVE_PORTFOLIOS',

    # Crisis Rebalancing
    'CrisisRebalancer',
    'RebalancingStrategy',
    'RebalancingSchedule',
    'TransitionResult',
    'compare_rebalancing_strategies',
]
