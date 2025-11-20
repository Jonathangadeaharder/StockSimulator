"""
Covariance Matrix Shrinkage Estimation

Implements shrinkage estimators to reduce estimation error in
covariance matrices. Particularly valuable when the number of
observations is small relative to the number of assets.

Reference:
Ledoit, O., & Wolf, M. (2004). "Honey, I Shrunk the Sample Covariance Matrix."
Journal of Portfolio Management, 30(4), 110-119.
"""

import numpy as np
import pandas as pd
from typing import Optional


class CovarianceShrinkage:
    """
    Shrinkage estimators for covariance matrices.

    Reduces estimation error by shrinking sample covariance
    toward a structured target. This is especially important
    for optimization, where small errors in covariance can
    lead to large errors in optimal weights.
    """

    @staticmethod
    def ledoit_wolf(
        returns: pd.DataFrame,
        target: str = 'constant_correlation'
    ) -> np.ndarray:
        """
        Ledoit-Wolf optimal shrinkage estimator.

        Automatically determines the optimal shrinkage intensity
        that minimizes mean squared error.

        Args:
            returns: DataFrame of asset returns (rows = observations, cols = assets)
            target: Shrinkage target structure
                - 'constant_variance': Diagonal with average variance
                - 'constant_correlation': Constant correlation model
                - 'single_factor': Single factor model
                - 'identity': Identity matrix (decorrelation)

        Returns:
            Shrunk covariance matrix (numpy array)

        Example:
            >>> returns_df = pd.DataFrame({'SPY': spy_returns, 'AGG': agg_returns})
            >>> cov_shrunk = CovarianceShrinkage.ledoit_wolf(returns_df)
            >>> # Use in optimization for more stable results
        """
        # Sample covariance
        S = returns.cov().values
        n, p = returns.shape  # n observations, p assets

        # Choose shrinkage target
        F = CovarianceShrinkage._get_shrinkage_target(returns, S, target)

        # Calculate optimal shrinkage intensity (Ledoit-Wolf formula)
        delta = CovarianceShrinkage._calculate_shrinkage_intensity(returns, S, F)

        # Shrunk covariance: delta * F + (1 - delta) * S
        return delta * F + (1 - delta) * S

    @staticmethod
    def manual_shrinkage(
        returns: pd.DataFrame,
        shrinkage: float = 0.2,
        target: str = 'constant_correlation'
    ) -> np.ndarray:
        """
        Apply manual shrinkage intensity.

        Useful when you want to control the shrinkage amount
        or when you have prior knowledge about appropriate shrinkage.

        Args:
            returns: DataFrame of asset returns
            shrinkage: Shrinkage intensity (0 = no shrinkage, 1 = full shrinkage to target)
            target: Shrinkage target type (see ledoit_wolf for options)

        Returns:
            Shrunk covariance matrix

        Example:
            >>> # Apply 30% shrinkage toward constant correlation
            >>> cov_shrunk = CovarianceShrinkage.manual_shrinkage(
            ...     returns_df, shrinkage=0.3, target='constant_correlation'
            ... )
        """
        if not 0 <= shrinkage <= 1:
            raise ValueError("Shrinkage must be between 0 and 1")

        S = returns.cov().values
        F = CovarianceShrinkage._get_shrinkage_target(returns, S, target)

        return shrinkage * F + (1 - shrinkage) * S

    @staticmethod
    def oracle_approximating_shrinkage(returns: pd.DataFrame) -> np.ndarray:
        """
        Oracle Approximating Shrinkage (OAS) estimator.

        An alternative to Ledoit-Wolf that's more robust when
        the number of assets is large relative to observations.

        Args:
            returns: DataFrame of asset returns

        Returns:
            Shrunk covariance matrix

        Reference:
        Chen, Y., et al. (2009). "Shrinkage Algorithms for MMSE Covariance Estimation."
        """
        S = returns.cov().values
        n, p = returns.shape

        # OAS shrinkage target: scaled identity
        trace_S = np.trace(S)
        F = np.eye(p) * (trace_S / p)

        # OAS shrinkage intensity
        # Simplified formula (full formula is more complex)
        if n > p:
            rho = min((1 - 2/p) / (n + 1 - 2/p), 1)
        else:
            rho = 1  # Full shrinkage if n <= p

        return rho * F + (1 - rho) * S

    @staticmethod
    def _get_shrinkage_target(
        returns: pd.DataFrame,
        S: np.ndarray,
        target: str
    ) -> np.ndarray:
        """
        Compute shrinkage target matrix.

        Args:
            returns: DataFrame of asset returns
            S: Sample covariance matrix
            target: Target type

        Returns:
            Target matrix F
        """
        p = len(S)

        if target == 'constant_variance':
            # Target: diagonal with average variance
            avg_var = np.trace(S) / p
            F = np.diag(np.full(p, avg_var))

        elif target == 'constant_correlation':
            # Target: constant correlation model
            # All pairs have the same correlation
            std_devs = np.sqrt(np.diag(S))

            # Calculate average correlation
            corr_matrix = S / np.outer(std_devs, std_devs)
            avg_corr = (np.sum(corr_matrix) - p) / (p * (p - 1))

            # Ensure valid correlation
            avg_corr = max(-1, min(1, avg_corr))

            # Build target with constant correlation
            F = avg_corr * np.outer(std_devs, std_devs)
            np.fill_diagonal(F, np.diag(S))

        elif target == 'single_factor':
            # Target: single factor model (market model)
            # Cov[i,j] = beta[i] * beta[j] * var[market] + residual_var[i] if i==j

            # Use equal-weighted returns as market proxy
            market_returns = returns.mean(axis=1)
            var_market = np.var(market_returns)

            # Calculate betas for each asset
            betas = np.array([
                np.cov(returns.iloc[:, i], market_returns)[0, 1] / var_market
                for i in range(p)
            ])

            # Factor covariance structure
            F = var_market * np.outer(betas, betas)

            # Add residual variances to diagonal
            residual_vars = np.diag(S) - np.diag(F)
            residual_vars = np.maximum(residual_vars, 0)  # Ensure positive
            np.fill_diagonal(F, np.diag(S))

        elif target == 'identity':
            # Target: identity matrix (complete decorrelation)
            F = np.eye(p)

        else:
            raise ValueError(f"Unknown target: {target}")

        return F

    @staticmethod
    def _calculate_shrinkage_intensity(
        returns: pd.DataFrame,
        S: np.ndarray,
        F: np.ndarray
    ) -> float:
        """
        Calculate optimal shrinkage intensity using Ledoit-Wolf formula.

        Args:
            returns: DataFrame of asset returns
            S: Sample covariance matrix
            F: Target matrix

        Returns:
            Optimal shrinkage intensity delta (between 0 and 1)
        """
        n, p = returns.shape
        returns_arr = returns.values

        # Compute asymptotic variance of sample covariance (pi)
        pi = 0
        for t in range(n):
            r = returns_arr[t, :].reshape(-1, 1)
            # Outer product minus sample covariance
            deviation = r @ r.T - S
            pi += np.linalg.norm(deviation, 'fro') ** 2
        pi /= n

        # Compute misspecification (gamma)
        # This is the squared Frobenius norm of (S - F)
        gamma = np.linalg.norm(S - F, 'fro') ** 2

        # Compute diagonal contribution (rho)
        # This accounts for the variance of diagonal elements
        rho = 0
        for t in range(n):
            r = returns_arr[t, :].reshape(-1, 1)
            deviation = r @ r.T - S
            centered = (deviation - (F - S))
            rho += np.trace(centered.T @ centered)
        rho /= n

        # Optimal shrinkage intensity
        if gamma > 0:
            # kappa measures ratio of estimation error to misspecification
            kappa = (pi - rho) / gamma
            # Shrinkage intensity (bounded between 0 and 1)
            delta = max(0, min(1, kappa / n))
        else:
            # If F == S, no shrinkage needed
            delta = 0

        return delta


def estimate_covariance(
    returns: pd.DataFrame,
    method: str = 'ledoit_wolf',
    **kwargs
) -> np.ndarray:
    """
    Convenience function to estimate covariance matrix.

    Args:
        returns: DataFrame of asset returns
        method: Estimation method
            - 'sample': Standard sample covariance (no shrinkage)
            - 'ledoit_wolf': Ledoit-Wolf optimal shrinkage (default)
            - 'manual': Manual shrinkage (requires 'shrinkage' kwarg)
            - 'oas': Oracle Approximating Shrinkage
        **kwargs: Additional arguments for the chosen method

    Returns:
        Estimated covariance matrix

    Example:
        >>> # Ledoit-Wolf with constant correlation target
        >>> cov = estimate_covariance(returns_df, method='ledoit_wolf',
        ...                          target='constant_correlation')
        >>>
        >>> # Manual 20% shrinkage
        >>> cov = estimate_covariance(returns_df, method='manual',
        ...                          shrinkage=0.2, target='constant_correlation')
    """
    if method == 'sample':
        return returns.cov().values

    elif method == 'ledoit_wolf':
        target = kwargs.get('target', 'constant_correlation')
        return CovarianceShrinkage.ledoit_wolf(returns, target=target)

    elif method == 'manual':
        if 'shrinkage' not in kwargs:
            raise ValueError("Manual shrinkage requires 'shrinkage' parameter")
        shrinkage = kwargs['shrinkage']
        target = kwargs.get('target', 'constant_correlation')
        return CovarianceShrinkage.manual_shrinkage(returns, shrinkage, target)

    elif method == 'oas':
        return CovarianceShrinkage.oracle_approximating_shrinkage(returns)

    else:
        raise ValueError(f"Unknown method: {method}")


def shrinkage_diagnostics(returns: pd.DataFrame) -> dict:
    """
    Compare different shrinkage methods for diagnostic purposes.

    Args:
        returns: DataFrame of asset returns

    Returns:
        Dictionary with covariance matrices and diagnostic metrics

    Example:
        >>> diagnostics = shrinkage_diagnostics(returns_df)
        >>> print(f"Ledoit-Wolf shrinkage: {diagnostics['lw_intensity']:.2%}")
        >>> print(f"Condition number (sample): {diagnostics['condition_sample']:.1f}")
        >>> print(f"Condition number (shrunk): {diagnostics['condition_lw']:.1f}")
    """
    S = returns.cov().values
    S_lw = CovarianceShrinkage.ledoit_wolf(returns)
    S_oas = CovarianceShrinkage.oracle_approximating_shrinkage(returns)

    # Calculate condition numbers (measure of numerical stability)
    def condition_number(matrix):
        eigenvalues = np.linalg.eigvalsh(matrix)
        return eigenvalues.max() / eigenvalues.min()

    # Estimate shrinkage intensity for Ledoit-Wolf
    n, p = returns.shape
    F = CovarianceShrinkage._get_shrinkage_target(returns, S, 'constant_correlation')
    lw_intensity = CovarianceShrinkage._calculate_shrinkage_intensity(returns, S, F)

    return {
        'sample_cov': S,
        'ledoit_wolf_cov': S_lw,
        'oas_cov': S_oas,
        'lw_intensity': lw_intensity,
        'condition_sample': condition_number(S),
        'condition_lw': condition_number(S_lw),
        'condition_oas': condition_number(S_oas),
        'n_observations': n,
        'n_assets': p,
        'ratio_n_p': n / p
    }
