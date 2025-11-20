"""
Sector and classification constraints.

Phase 2 Enhancement: Constraints based on asset classifications.
"""

from typing import List, Dict
import numpy as np

from .base_constraint import PortfolioConstraint, CVXPY_AVAILABLE

if CVXPY_AVAILABLE:
    import cvxpy as cp


class SectorConcentrationConstraint(PortfolioConstraint):
    """
    Limit exposure to any single sector.

    Phase 2 Enhancement: Diversification constraint by sector.

    Prevents over-concentration in any sector, promoting diversification
    across different parts of the market.

    Example:
        >>> # No sector > 30%
        >>> sector_map = {
        ...     'AAPL': 'Technology',
        ...     'GOOGL': 'Technology',
        ...     'JPM': 'Financials',
        ...     'XOM': 'Energy'
        ... }
        >>> constraint = SectorConcentrationConstraint(
        ...     sector_mapping=sector_map,
        ...     max_sector_weight=0.30
        ... )
    """

    def __init__(
        self,
        sector_mapping: Dict[str, str],
        max_sector_weight: float = 0.30
    ):
        """
        Initialize sector concentration constraint.

        Args:
            sector_mapping: Dict mapping symbol -> sector name
            max_sector_weight: Max weight in any sector (0.30 = 30%)
        """
        self.sector_mapping = sector_mapping
        self.max_sector_weight = max_sector_weight

    def apply(self, weights, symbols: List[str] = None, **kwargs) -> List:
        """
        Apply sector concentration constraint.

        Args:
            weights: CVXPY variable for portfolio weights
            symbols: List of symbols (in same order as weights) (required!)
            **kwargs: Additional context

        Returns:
            List of cvxpy constraints

        Raises:
            ValueError: If symbols not provided
        """
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        if symbols is None:
            raise ValueError("SectorConcentrationConstraint requires symbols parameter")

        # Group symbols by sector
        sectors = {}
        for i, symbol in enumerate(symbols):
            sector = self.sector_mapping.get(symbol, 'Unknown')
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(i)

        # Create constraint for each sector
        constraints = []
        for sector, indices in sectors.items():
            # Sum of weights in this sector
            sector_weight = cp.sum([weights[i] for i in indices])
            constraints.append(sector_weight <= self.max_sector_weight)

        return constraints

    def validate(self, weights: np.ndarray, symbols: List[str] = None, **kwargs) -> bool:
        """Validate sector exposures are within limits."""
        if symbols is None:
            return True

        # Calculate sector exposures
        sector_weights = {}
        for i, symbol in enumerate(symbols):
            sector = self.sector_mapping.get(symbol, 'Unknown')
            sector_weights[sector] = sector_weights.get(sector, 0.0) + weights[i]

        # Check all sectors are within limit
        for sector, weight in sector_weights.items():
            if weight > self.max_sector_weight + 1e-6:
                return False

        return True

    def __repr__(self) -> str:
        return (f"SectorConcentrationConstraint("
                f"sectors={len(set(self.sector_mapping.values()))}, "
                f"max_weight={self.max_sector_weight:.1%})")


class SectorNeutralConstraint(PortfolioConstraint):
    """
    Require sector exposures to match benchmark.

    Phase 2 Enhancement: Sector-neutral portfolio construction.

    Useful for long-short portfolios or when you want to isolate
    stock-picking alpha while maintaining sector neutrality.

    Example:
        >>> # Match S&P 500 sector weights
        >>> sector_map = {...}
        >>> benchmark_weights = {
        ...     'Technology': 0.28,
        ...     'Financials': 0.13,
        ...     'Healthcare': 0.14,
        ...     ...
        ... }
        >>> constraint = SectorNeutralConstraint(
        ...     sector_mapping=sector_map,
        ...     benchmark_sector_weights=benchmark_weights,
        ...     tolerance=0.05  # +/- 5%
        ... )
    """

    def __init__(
        self,
        sector_mapping: Dict[str, str],
        benchmark_sector_weights: Dict[str, float],
        tolerance: float = 0.05
    ):
        """
        Initialize sector neutral constraint.

        Args:
            sector_mapping: Dict mapping symbol -> sector name
            benchmark_sector_weights: Dict mapping sector -> benchmark weight
            tolerance: Allowed deviation from benchmark (0.05 = +/- 5%)
        """
        self.sector_mapping = sector_mapping
        self.benchmark_weights = benchmark_sector_weights
        self.tolerance = tolerance

    def apply(self, weights, symbols: List[str] = None, **kwargs) -> List:
        """Apply sector neutral constraint."""
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy required for optimization constraints")

        if symbols is None:
            raise ValueError("SectorNeutralConstraint requires symbols parameter")

        # Group symbols by sector
        sectors = {}
        for i, symbol in enumerate(symbols):
            sector = self.sector_mapping.get(symbol, 'Unknown')
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(i)

        # Create constraints for each sector
        constraints = []
        for sector, indices in sectors.items():
            # Target weight for this sector
            target_weight = self.benchmark_weights.get(sector, 0.0)

            # Actual weight in portfolio
            sector_weight = cp.sum([weights[i] for i in indices])

            # Require sector_weight ≈ target_weight (+/- tolerance)
            constraints.append(sector_weight >= target_weight - self.tolerance)
            constraints.append(sector_weight <= target_weight + self.tolerance)

        return constraints

    def validate(self, weights: np.ndarray, symbols: List[str] = None, **kwargs) -> bool:
        """Validate sector neutrality."""
        if symbols is None:
            return True

        # Calculate sector exposures
        sector_weights = {}
        for i, symbol in enumerate(symbols):
            sector = self.sector_mapping.get(symbol, 'Unknown')
            sector_weights[sector] = sector_weights.get(sector, 0.0) + weights[i]

        # Check all sectors are within tolerance of benchmark
        for sector in set(self.sector_mapping.values()):
            target = self.benchmark_weights.get(sector, 0.0)
            actual = sector_weights.get(sector, 0.0)
            if abs(actual - target) > self.tolerance + 1e-6:
                return False

        return True

    def __repr__(self) -> str:
        return (f"SectorNeutralConstraint("
                f"sectors={len(self.benchmark_weights)}, "
                f"tolerance={self.tolerance:.1%})")
