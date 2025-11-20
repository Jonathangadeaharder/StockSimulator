"""
Strategy Optimization

Tools for optimizing strategy parameters and testing robustness.
"""

from .optimizer import StrategyOptimizer, GridSearchOptimizer
from .walk_forward import WalkForwardAnalyzer
from .position_sizing import PositionSizer, KellyCriterion, FixedFractional
from .discrete_allocation import DiscreteAllocator
from .constrained_optimizer import ConstrainedOptimizer  # Phase 2
from .shrinkage import CovarianceShrinkage, estimate_covariance, shrinkage_diagnostics  # Phase 3
from .multi_period import MultiPeriodOptimizer, AdaptiveMultiPeriodOptimizer, compare_single_vs_multi_period  # Phase 3

__all__ = [
    'StrategyOptimizer',
    'GridSearchOptimizer',
    'WalkForwardAnalyzer',
    'PositionSizer',
    'KellyCriterion',
    'FixedFractional',
    'DiscreteAllocator',
    'ConstrainedOptimizer',  # Phase 2
    'CovarianceShrinkage',  # Phase 3
    'estimate_covariance',  # Phase 3
    'shrinkage_diagnostics',  # Phase 3
    'MultiPeriodOptimizer',  # Phase 3
    'AdaptiveMultiPeriodOptimizer',  # Phase 3
    'compare_single_vs_multi_period',  # Phase 3
]
