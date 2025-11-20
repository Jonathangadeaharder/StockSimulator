"""
Hierarchical Risk Parity (HRP) Strategy

Implementation of Marcos Lopez de Prado's HRP algorithm.
Uses hierarchical clustering to build diversified portfolios
without requiring return forecasts.
"""

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
from typing import Dict, List, Optional
from datetime import date


class HierarchicalRiskParityStrategy:
    """
    Hierarchical Risk Parity strategy by Marcos Lopez de Prado.

    Uses clustering to build diversified portfolios based on
    correlation structure, avoiding need for return forecasts.

    Benefits over mean-variance:
    - More stable (no return forecasts needed)
    - Better out-of-sample performance
    - Natural diversification through hierarchical structure
    - Robust to estimation error in expected returns

    Reference:
    Lopez de Prado, M. (2016). "Building Diversified Portfolios that
    Outperform Out of Sample." Journal of Portfolio Management.
    """

    def __init__(
        self,
        lookback_days: int = 252,
        linkage_method: str = 'single',  # 'single', 'complete', 'average', 'ward'
        rebalance_frequency_days: int = 21  # Monthly rebalancing
    ):
        """
        Initialize HRP strategy.

        Args:
            lookback_days: Number of days of historical data to use
            linkage_method: Hierarchical clustering method
                - 'single': Minimum distance (more clusters)
                - 'complete': Maximum distance (fewer clusters)
                - 'average': Average distance (balanced)
                - 'ward': Minimizes within-cluster variance
            rebalance_frequency_days: Days between rebalances
        """
        self.lookback_days = lookback_days
        self.linkage_method = linkage_method
        self.rebalance_frequency_days = rebalance_frequency_days
        self._last_rebalance_date = None
        self._cached_allocation = None

    def __call__(
        self,
        current_date: date,
        historical_data: Dict[str, pd.DataFrame],
        portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate HRP allocation weights.

        Args:
            current_date: Current simulation date
            historical_data: Dict of symbol -> DataFrame with price history
            portfolio: Current portfolio state
            current_prices: Dict of symbol -> current price

        Returns:
            Dict of symbol -> allocation percentage (0-100)
        """
        # Check if we need to rebalance
        if self._cached_allocation is not None:
            if self._last_rebalance_date is not None:
                days_since_rebalance = (current_date - self._last_rebalance_date).days
                if days_since_rebalance < self.rebalance_frequency_days:
                    return self._cached_allocation

        # Calculate new allocation
        allocation = self._calculate_hrp_allocation(
            historical_data,
            current_date,
            list(current_prices.keys())
        )

        # Cache for next call
        self._cached_allocation = allocation
        self._last_rebalance_date = current_date

        return allocation

    def _calculate_hrp_allocation(
        self,
        historical_data: Dict[str, pd.DataFrame],
        current_date: date,
        symbols: List[str]
    ) -> Dict[str, float]:
        """Calculate HRP weights from historical data."""

        # Build returns matrix
        returns_data = {}
        for symbol in symbols:
            if symbol not in historical_data:
                continue

            df = historical_data[symbol]
            if len(df) < self.lookback_days:
                continue

            # Get recent returns
            recent_df = df.tail(self.lookback_days)
            returns = recent_df['close'].pct_change().dropna()

            if len(returns) > 0:
                returns_data[symbol] = returns.values

        if len(returns_data) < 2:
            # Need at least 2 assets for HRP - equal weight fallback
            equal_weight = 100.0 / len(returns_data) if returns_data else 0.0
            return {s: equal_weight for s in returns_data.keys()}

        # Create returns DataFrame (align lengths)
        min_length = min(len(v) for v in returns_data.values())
        aligned_returns = {k: v[-min_length:] for k, v in returns_data.items()}
        returns_df = pd.DataFrame(aligned_returns)

        if len(returns_df) < 20:  # Need minimum data for correlation
            equal_weight = 100.0 / len(returns_data)
            return {s: equal_weight for s in returns_data.keys()}

        # Calculate correlation matrix
        corr_matrix = returns_df.corr()

        # Convert correlation to distance: distance = sqrt(0.5 * (1 - correlation))
        # This ensures 0 <= distance <= 1
        dist_matrix = np.sqrt(0.5 * (1 - corr_matrix))

        # Hierarchical clustering
        condensed_dist = squareform(dist_matrix, checks=False)
        linkage_matrix = linkage(condensed_dist, method=self.linkage_method)

        # Get optimal leaf order
        sorted_indices = self._get_quasi_diag(linkage_matrix, len(returns_df.columns))

        # Reorder returns and correlation matrix
        sorted_columns = returns_df.columns[sorted_indices]
        sorted_returns = returns_df[sorted_columns]
        sorted_corr = corr_matrix.iloc[sorted_indices, sorted_indices]

        # Calculate HRP weights
        hrp_weights = self._get_recursive_bisection(sorted_returns, sorted_corr)

        # Convert to allocation percentages
        allocation = {}
        for i, symbol in enumerate(sorted_columns):
            allocation[symbol] = hrp_weights[i] * 100

        return allocation

    def _get_quasi_diag(self, linkage_matrix: np.ndarray, num_items: int) -> List[int]:
        """
        Get optimal ordering of assets based on hierarchical clustering.

        Reorganizes assets so similar assets are grouped together,
        forming a quasi-diagonal structure in the covariance matrix.

        Args:
            linkage_matrix: Scipy linkage matrix from hierarchical clustering
            num_items: Number of leaf nodes (assets)

        Returns:
            List of indices representing optimal asset order
        """
        link = linkage_matrix.astype(int)
        sort_ix = []

        def recursive_order(cluster_id):
            """Recursively traverse tree to get leaf order."""
            if cluster_id < num_items:
                # Leaf node (actual asset)
                sort_ix.append(cluster_id)
            else:
                # Internal node (merged cluster)
                left_child = int(link[cluster_id - num_items, 0])
                right_child = int(link[cluster_id - num_items, 1])
                recursive_order(left_child)
                recursive_order(right_child)

        # Start from root (last merged cluster)
        recursive_order(2 * num_items - 2)

        return sort_ix

    def _get_recursive_bisection(
        self,
        returns: pd.DataFrame,
        corr_matrix: pd.DataFrame
    ) -> np.ndarray:
        """
        Calculate HRP weights using recursive bisection.

        Divides portfolio hierarchically into clusters and allocates
        inversely to cluster variance at each split.

        Args:
            returns: DataFrame of asset returns (already sorted)
            corr_matrix: Correlation matrix (already sorted)

        Returns:
            Array of weights summing to 1.0
        """
        cov_matrix = returns.cov()

        def _get_cluster_var(items: List[str]) -> float:
            """Calculate variance of cluster with inverse-variance weighting."""
            cluster_cov = cov_matrix.loc[items, items]
            # Inverse-variance weighting within cluster
            inv_var = 1.0 / np.diag(cluster_cov)
            inv_var /= inv_var.sum()
            # Portfolio variance of cluster
            return np.dot(inv_var, np.dot(cluster_cov, inv_var))

        weights = pd.Series(1.0, index=returns.columns)
        clusters = [returns.columns.tolist()]

        while len(clusters) > 0:
            # Split each cluster in half
            new_clusters = []
            for cluster in clusters:
                if len(cluster) == 1:
                    continue  # Can't split single asset

                # Split at midpoint (relies on quasi-diagonal ordering)
                mid = len(cluster) // 2
                cluster_left = cluster[:mid]
                cluster_right = cluster[mid:]

                # Calculate cluster variances
                var_left = _get_cluster_var(cluster_left)
                var_right = _get_cluster_var(cluster_right)

                # Allocate inversely proportional to variance
                # Lower variance cluster gets more weight
                alpha = 1.0 - var_left / (var_left + var_right)

                # Update weights for this split
                weights[cluster_left] *= alpha
                weights[cluster_right] *= (1 - alpha)

                # Add new clusters for further splitting
                if len(cluster_left) > 1:
                    new_clusters.append(cluster_left)
                if len(cluster_right) > 1:
                    new_clusters.append(cluster_right)

            clusters = new_clusters

        # Normalize weights to sum to 1.0
        weights /= weights.sum()

        return weights.values

    def get_correlation_matrix(
        self,
        historical_data: Dict[str, pd.DataFrame],
        symbols: List[str]
    ) -> Optional[pd.DataFrame]:
        """
        Get correlation matrix for visualization/debugging.

        Returns:
            Correlation matrix DataFrame or None if insufficient data
        """
        returns_data = {}
        for symbol in symbols:
            if symbol not in historical_data:
                continue

            df = historical_data[symbol]
            if len(df) < self.lookback_days:
                continue

            recent_df = df.tail(self.lookback_days)
            returns = recent_df['close'].pct_change().dropna()

            if len(returns) > 0:
                returns_data[symbol] = returns.values

        if len(returns_data) < 2:
            return None

        min_length = min(len(v) for v in returns_data.values())
        aligned_returns = {k: v[-min_length:] for k, v in returns_data.items()}
        returns_df = pd.DataFrame(aligned_returns)

        if len(returns_df) < 20:
            return None

        return returns_df.corr()
