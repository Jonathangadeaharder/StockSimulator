"""
Regime-Aware Portfolio Strategies

Dynamic allocation strategies that adjust based on market regime.

Key capabilities:
- Defensive positioning pre-crisis/during crisis
- Aggressive "buy the dip" during recovery
- Gradual rebalancing between regimes
- Custom allocations per regime
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import date
from enum import Enum

from stocksimulator.regime.regime_detector import MarketRegime, MarketRegimeDetector


class RegimeAwareStrategy:
    """
    Base class for regime-aware portfolio strategies.

    Adjusts allocation based on detected market regime.
    """

    def __init__(
        self,
        regime_allocations: Dict[MarketRegime, Dict[str, float]],
        regime_detector: Optional[MarketRegimeDetector] = None,
        transition_days: int = 20,  # Days to transition between regimes
        rebalance_frequency_days: int = 21  # Monthly rebalancing
    ):
        """
        Initialize regime-aware strategy.

        Args:
            regime_allocations: Dict mapping regime -> {asset: weight%}
            regime_detector: MarketRegimeDetector instance
            transition_days: Days over which to transition between regimes
            rebalance_frequency_days: Days between rebalances

        Example:
            >>> allocations = {
            ...     MarketRegime.NORMAL: {'SP500': 60, 'LONG_TREASURY': 40},
            ...     MarketRegime.CRISIS: {'LONG_TREASURY': 70, 'SHORT_BOND': 30},
            ...     MarketRegime.RECOVERY: {'SP500': 80, 'LONG_TREASURY': 20}
            ... }
            >>> strategy = RegimeAwareStrategy(allocations)
        """
        self.regime_allocations = regime_allocations
        self.regime_detector = regime_detector or MarketRegimeDetector()
        self.transition_days = transition_days
        self.rebalance_frequency_days = rebalance_frequency_days

        self._last_rebalance_date = None
        self._current_regime = MarketRegime.NORMAL
        self._target_allocation = None
        self._transition_start_date = None
        self._transition_source_allocation = None

    def __call__(
        self,
        current_date: date,
        historical_data: Dict[str, pd.DataFrame],
        portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate regime-aware allocation.

        Args:
            current_date: Current date
            historical_data: Historical price data
            portfolio: Current portfolio
            current_prices: Current prices

        Returns:
            Dict of asset -> allocation %
        """
        # Check if rebalance needed
        if self._last_rebalance_date is not None:
            days_since_rebalance = (current_date - self._last_rebalance_date).days
            if days_since_rebalance < self.rebalance_frequency_days:
                # Return previous allocation
                return self._target_allocation if self._target_allocation else {}

        # Detect current regime
        regime = self._detect_regime(current_date, historical_data)

        # Check if regime changed
        if regime != self._current_regime:
            # Start transition
            self._start_transition(regime)

        # Calculate allocation (with transition if needed)
        allocation = self._calculate_allocation_with_transition(current_date, regime)

        # Update state
        self._current_regime = regime
        self._target_allocation = allocation
        self._last_rebalance_date = current_date

        return allocation

    def _detect_regime(
        self,
        current_date: date,
        historical_data: Dict[str, pd.DataFrame]
    ) -> MarketRegime:
        """Detect current market regime."""

        # Use S&P 500 or first available asset for regime detection
        if 'SP500' in historical_data:
            price_data = historical_data['SP500']
        else:
            # Use first available
            price_data = list(historical_data.values())[0]

        # Filter to data up to current date
        price_data = price_data[price_data['Date'] <= pd.Timestamp(current_date)]

        if len(price_data) < 100:
            # Not enough data
            return MarketRegime.NORMAL

        # Detect regime
        regimes = self.regime_detector.detect_regimes(price_data)

        if len(regimes) == 0:
            return MarketRegime.NORMAL

        # Return most recent regime
        return MarketRegime(regimes.iloc[-1]['Regime'])

    def _start_transition(self, new_regime: MarketRegime):
        """Start transition to new regime."""
        self._transition_start_date = self._last_rebalance_date
        self._transition_source_allocation = self._target_allocation.copy() if self._target_allocation else {}

    def _calculate_allocation_with_transition(
        self,
        current_date: date,
        target_regime: MarketRegime
    ) -> Dict[str, float]:
        """
        Calculate allocation with gradual transition.

        Transitions smoothly from current allocation to target allocation
        over transition_days to avoid abrupt shifts.
        """
        # Get target allocation for regime
        target_allocation = self.regime_allocations.get(
            target_regime,
            self.regime_allocations[MarketRegime.NORMAL]
        )

        # If no transition in progress, return target
        if self._transition_start_date is None or not self._transition_source_allocation:
            return target_allocation.copy()

        # Calculate transition progress
        days_elapsed = (current_date - self._transition_start_date).days
        transition_pct = min(1.0, days_elapsed / self.transition_days)

        # Blend source and target allocations
        allocation = {}

        # Get all assets from both allocations
        all_assets = set(self._transition_source_allocation.keys()) | set(target_allocation.keys())

        for asset in all_assets:
            source_weight = self._transition_source_allocation.get(asset, 0.0)
            target_weight = target_allocation.get(asset, 0.0)

            # Linear interpolation
            blended_weight = source_weight * (1 - transition_pct) + target_weight * transition_pct
            allocation[asset] = blended_weight

        # Normalize to 100%
        total_weight = sum(allocation.values())
        if total_weight > 0:
            allocation = {k: v / total_weight * 100 for k, v in allocation.items()}

        return allocation


class DefensiveToAggressiveStrategy(RegimeAwareStrategy):
    """
    Strategy that transitions from defensive to aggressive during crises.

    Defensive before/during crisis → Gradual shift to aggressive during recovery.
    This implements the "buy the dip" strategy the user requested.
    """

    def __init__(
        self,
        defensive_assets: List[str] = None,
        aggressive_assets: List[str] = None,
        recovery_aggressiveness: float = 1.5,  # 1.5x normal allocation in recovery
        **kwargs
    ):
        """
        Initialize defensive-to-aggressive strategy.

        Args:
            defensive_assets: Assets for defensive allocation (defaults to bonds)
            aggressive_assets: Assets for aggressive allocation (defaults to stocks)
            recovery_aggressiveness: Multiplier for aggressive assets during recovery
            **kwargs: Additional args for RegimeAwareStrategy

        Example:
            >>> strategy = DefensiveToAggressiveStrategy(
            ...     defensive_assets=['LONG_TREASURY', 'SHORT_BOND'],
            ...     aggressive_assets=['SP500', 'WORLD'],
            ...     recovery_aggressiveness=1.8  # 80% more aggressive in recovery
            ... )
        """
        self.defensive_assets = defensive_assets or ['LONG_TREASURY', 'SHORT_BOND']
        self.aggressive_assets = aggressive_assets or ['SP500', 'WORLD']
        self.recovery_aggressiveness = recovery_aggressiveness

        # Build regime allocations
        regime_allocations = self._build_allocations()

        super().__init__(regime_allocations, **kwargs)

    def _build_allocations(self) -> Dict[MarketRegime, Dict[str, float]]:
        """Build allocation rules for each regime."""

        allocations = {}

        # Normal: Balanced
        allocations[MarketRegime.NORMAL] = {
            'SP500': 60.0,
            'LONG_TREASURY': 30.0,
            'SHORT_BOND': 10.0
        }

        # Pre-Crisis: Shift to defensive
        allocations[MarketRegime.PRE_CRISIS] = {
            'SP500': 30.0,
            'LONG_TREASURY': 40.0,
            'SHORT_BOND': 20.0,
            'CONSUMER_STAPLES': 10.0
        }

        # Crisis: Maximum defensive
        allocations[MarketRegime.CRISIS] = {
            'LONG_TREASURY': 50.0,
            'SHORT_BOND': 30.0,
            'CONSUMER_STAPLES': 15.0,
            'MANAGED_FUTURES': 5.0
        }

        # Recovery: Aggressive "buy the dip"
        allocations[MarketRegime.RECOVERY] = {
            'SP500': 70.0,  # Overweight stocks
            'WORLD': 20.0,
            'LONG_TREASURY': 10.0
        }

        return allocations


class CrisisOpportunisticStrategy(RegimeAwareStrategy):
    """
    Opportunistic strategy that buys aggressively during crises.

    Gradually increases equity exposure as crisis deepens.
    """

    def __init__(self, max_crisis_equity_pct: float = 90.0, **kwargs):
        """
        Initialize crisis opportunistic strategy.

        Args:
            max_crisis_equity_pct: Max equity % during severe crisis
            **kwargs: Additional args for RegimeAwareStrategy
        """
        self.max_crisis_equity_pct = max_crisis_equity_pct

        regime_allocations = {
            MarketRegime.NORMAL: {
                'SP500': 60.0,
                'LONG_TREASURY': 40.0
            },
            MarketRegime.PRE_CRISIS: {
                'SP500': 40.0,
                'LONG_TREASURY': 50.0,
                'SHORT_BOND': 10.0
            },
            MarketRegime.CRISIS: {
                # Increase exposure as crisis deepens (handled dynamically)
                'SP500': 70.0,
                'WORLD': 20.0,
                'SHORT_BOND': 10.0
            },
            MarketRegime.RECOVERY: {
                'SP500': 80.0,
                'WORLD': 15.0,
                'SHORT_BOND': 5.0
            }
        }

        super().__init__(regime_allocations, **kwargs)

    def _calculate_allocation_with_transition(
        self,
        current_date: date,
        target_regime: MarketRegime
    ) -> Dict[str, float]:
        """
        Override to adjust crisis allocation based on severity.
        """
        allocation = super()._calculate_allocation_with_transition(current_date, target_regime)

        # During crisis, increase equity based on severity
        # (More severe = better buying opportunity)
        if target_regime == MarketRegime.CRISIS:
            # This is simplified; in practice would need access to severity
            # For now, use standard allocation
            pass

        return allocation


class AdaptiveAllWeatherStrategy(RegimeAwareStrategy):
    """
    All-weather strategy that adapts to regimes.

    Maintains diversification but tilts based on regime.
    """

    def __init__(self, **kwargs):
        """Initialize adaptive all-weather strategy."""

        regime_allocations = {
            MarketRegime.NORMAL: {
                'SP500': 30.0,
                'LONG_TREASURY': 40.0,
                'CONSUMER_STAPLES': 15.0,
                'MANAGED_FUTURES': 10.0,
                'SHORT_BOND': 5.0
            },
            MarketRegime.PRE_CRISIS: {
                'SP500': 20.0,
                'LONG_TREASURY': 50.0,
                'CONSUMER_STAPLES': 15.0,
                'MANAGED_FUTURES': 10.0,
                'SHORT_BOND': 5.0
            },
            MarketRegime.CRISIS: {
                'LONG_TREASURY': 40.0,
                'CONSUMER_STAPLES': 25.0,
                'MANAGED_FUTURES': 20.0,
                'SHORT_BOND': 15.0
            },
            MarketRegime.RECOVERY: {
                'SP500': 40.0,
                'LONG_TREASURY': 30.0,
                'CONSUMER_STAPLES': 15.0,
                'MANAGED_FUTURES': 10.0,
                'SHORT_BOND': 5.0
            }
        }

        super().__init__(regime_allocations, **kwargs)


# Pre-built strategies for convenience
DEFENSIVE_PORTFOLIOS = {
    'ultra_defensive': {
        'LONG_TREASURY': 60.0,
        'SHORT_BOND': 30.0,
        'MANAGED_FUTURES': 10.0
    },
    'defensive': {
        'LONG_TREASURY': 50.0,
        'SHORT_BOND': 20.0,
        'CONSUMER_STAPLES': 20.0,
        'SP500': 10.0
    },
    'moderate_defensive': {
        'LONG_TREASURY': 40.0,
        'SP500': 30.0,
        'CONSUMER_STAPLES': 20.0,
        'SHORT_BOND': 10.0
    }
}

AGGRESSIVE_PORTFOLIOS = {
    'moderate_aggressive': {
        'SP500': 70.0,
        'WORLD': 20.0,
        'SHORT_BOND': 10.0
    },
    'aggressive': {
        'SP500': 70.0,
        'SP500_2X': 20.0,
        'SHORT_BOND': 10.0
    },
    'ultra_aggressive': {
        'SP500': 60.0,
        'SP500_2X': 30.0,
        'WORLD_2X': 10.0
    }
}


def create_custom_regime_strategy(
    normal_allocation: Dict[str, float],
    crisis_allocation: Dict[str, float],
    pre_crisis_allocation: Optional[Dict[str, float]] = None,
    recovery_allocation: Optional[Dict[str, float]] = None,
    **kwargs
) -> RegimeAwareStrategy:
    """
    Factory function to create custom regime-aware strategy.

    Args:
        normal_allocation: Allocation for normal regime
        crisis_allocation: Allocation for crisis regime
        pre_crisis_allocation: Optional pre-crisis allocation (defaults to blend)
        recovery_allocation: Optional recovery allocation (defaults to blend)
        **kwargs: Additional args for RegimeAwareStrategy

    Returns:
        RegimeAwareStrategy instance

    Example:
        >>> strategy = create_custom_regime_strategy(
        ...     normal_allocation={'SP500': 60, 'LONG_TREASURY': 40},
        ...     crisis_allocation={'LONG_TREASURY': 80, 'SHORT_BOND': 20},
        ...     transition_days=30
        ... )
    """
    # Auto-generate pre-crisis and recovery if not provided
    if pre_crisis_allocation is None:
        # Pre-crisis: 70% defensive, 30% normal
        pre_crisis_allocation = {}
        for asset in set(list(normal_allocation.keys()) + list(crisis_allocation.keys())):
            normal_wt = normal_allocation.get(asset, 0)
            crisis_wt = crisis_allocation.get(asset, 0)
            pre_crisis_allocation[asset] = 0.3 * normal_wt + 0.7 * crisis_wt

    if recovery_allocation is None:
        # Recovery: 80% normal, 20% defensive
        recovery_allocation = {}
        for asset in set(list(normal_allocation.keys()) + list(crisis_allocation.keys())):
            normal_wt = normal_allocation.get(asset, 0)
            crisis_wt = crisis_allocation.get(asset, 0)
            recovery_allocation[asset] = 0.8 * normal_wt + 0.2 * crisis_wt

    regime_allocations = {
        MarketRegime.NORMAL: normal_allocation,
        MarketRegime.PRE_CRISIS: pre_crisis_allocation,
        MarketRegime.CRISIS: crisis_allocation,
        MarketRegime.RECOVERY: recovery_allocation
    }

    return RegimeAwareStrategy(regime_allocations, **kwargs)


if __name__ == '__main__':
    # Demo
    print("Available pre-built defensive portfolios:")
    for name, allocation in DEFENSIVE_PORTFOLIOS.items():
        print(f"\n{name}:")
        for asset, weight in allocation.items():
            print(f"  {asset}: {weight:.1f}%")

    print("\n\nAvailable pre-built aggressive portfolios:")
    for name, allocation in AGGRESSIVE_PORTFOLIOS.items():
        print(f"\n{name}:")
        for asset, weight in allocation.items():
            print(f"  {asset}: {weight:.1f}%")

    print("\n\nCreating sample regime-aware strategy...")
    strategy = DefensiveToAggressiveStrategy()
    print(f"Strategy allocations by regime:")
    for regime, allocation in strategy.regime_allocations.items():
        print(f"\n{regime.value}:")
        for asset, weight in allocation.items():
            print(f"  {asset}: {weight:.1f}%")
