"""
Trading strategies module

This module provides a comprehensive collection of trading strategies:

- **Base**: Abstract base class for all strategies
- **DCA/Fixed Allocation**: Dollar-cost averaging and fixed allocations
- **Momentum**: Trend-following strategies based on price momentum
- **Mean Reversion**: Contrarian strategies buying dips and selling rallies
- **Risk Parity**: Risk-balanced portfolios with equal risk contribution
- **Hierarchical Risk Parity**: Diversification using hierarchical clustering

Each strategy implements the BaseStrategy interface and can be used
directly with the Backtester for historical simulation.
"""

# Base strategy
from .base_strategy import BaseStrategy

# DCA and fixed allocation strategies
from .dca_strategy import (
    DCAStrategy,
    FixedAllocationStrategy,
    Balanced6040Strategy,
    AllWeatherStrategy
)

# Momentum strategies
from .momentum_strategy import (
    MomentumStrategy,
    DualMomentumStrategy,
    MovingAverageCrossoverStrategy
)

# Mean reversion strategies
from .mean_reversion_strategy import (
    MeanReversionStrategy,
    BollingerBandsStrategy,
    RSIMeanReversionStrategy
)

# Risk parity strategies
from .risk_parity_strategy import (
    RiskParityStrategy,
    VolatilityTargetingStrategy
)

# Hierarchical Risk Parity
from .hierarchical_risk_parity import HierarchicalRiskParityStrategy

__all__ = [
    # Base
    'BaseStrategy',

    # DCA/Fixed
    'DCAStrategy',
    'FixedAllocationStrategy',
    'Balanced6040Strategy',
    'AllWeatherStrategy',

    # Momentum
    'MomentumStrategy',
    'DualMomentumStrategy',
    'MovingAverageCrossoverStrategy',

    # Mean Reversion
    'MeanReversionStrategy',
    'BollingerBandsStrategy',
    'RSIMeanReversionStrategy',

    # Risk Parity
    'RiskParityStrategy',
    'VolatilityTargetingStrategy',

    # Hierarchical Risk Parity
    'HierarchicalRiskParityStrategy',
]
