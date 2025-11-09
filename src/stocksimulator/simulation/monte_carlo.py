"""
Monte Carlo Simulation

Run thousands of randomized scenarios to assess strategy robustness.
"""

from typing import Dict, List, Callable, Optional
from datetime import date, timedelta
import random
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.core.backtester import Backtester, BacktestResult
from stocksimulator.models.market_data import MarketData, OHLCV


class MonteCarloResult:
    """Result from Monte Carlo simulation."""

    def __init__(self, simulations: List[BacktestResult]):
        """
        Initialize Monte Carlo result.

        Args:
            simulations: List of backtest results from each simulation
        """
        self.simulations = simulations
        self.num_simulations = len(simulations)

    def get_statistics(self) -> Dict:
        """
        Get statistical summary of all simulations.

        Returns:
            Dictionary with percentiles and statistics
        """
        if not self.simulations:
            return {}

        # Extract metrics from all simulations
        returns = []
        sharpe_ratios = []
        max_drawdowns = []
        final_values = []

        for sim in self.simulations:
            summary = sim.get_performance_summary()
            returns.append(summary['total_return'])
            sharpe_ratios.append(summary['sharpe_ratio'])
            max_drawdowns.append(summary['max_drawdown'])
            final_values.append(sim.equity_curve[-1].value if sim.equity_curve else 0)

        returns.sort()
        sharpe_ratios.sort()
        max_drawdowns.sort()
        final_values.sort()

        n = len(returns)

        return {
            'num_simulations': n,
            'returns': {
                'mean': sum(returns) / n,
                'median': returns[n // 2],
                'p5': returns[int(n * 0.05)],
                'p25': returns[int(n * 0.25)],
                'p75': returns[int(n * 0.75)],
                'p95': returns[int(n * 0.95)],
                'min': returns[0],
                'max': returns[-1],
            },
            'sharpe_ratio': {
                'mean': sum(sharpe_ratios) / n,
                'median': sharpe_ratios[n // 2],
                'p5': sharpe_ratios[int(n * 0.05)],
                'p95': sharpe_ratios[int(n * 0.95)],
            },
            'max_drawdown': {
                'mean': sum(max_drawdowns) / n,
                'median': max_drawdowns[n // 2],
                'worst': max_drawdowns[-1],  # Worst drawdown
                'best': max_drawdowns[0],    # Best (smallest) drawdown
            },
            'final_value': {
                'mean': sum(final_values) / n,
                'median': final_values[n // 2],
                'p5': final_values[int(n * 0.05)],
                'p95': final_values[int(n * 0.95)],
            }
        }

    def get_percentile_result(self, percentile: float) -> Optional[BacktestResult]:
        """
        Get backtest result at specific percentile by total return.

        Args:
            percentile: Percentile (0-100)

        Returns:
            BacktestResult at that percentile
        """
        if not self.simulations:
            return None

        # Sort by total return
        sorted_sims = sorted(
            self.simulations,
            key=lambda s: s.get_performance_summary()['total_return']
        )

        idx = int(len(sorted_sims) * (percentile / 100))
        idx = max(0, min(idx, len(sorted_sims) - 1))

        return sorted_sims[idx]


class MonteCarloSimulator:
    """
    Monte Carlo simulation framework.

    Runs multiple randomized scenarios to test strategy robustness.
    """

    def __init__(self, backtester: Optional[Backtester] = None):
        """
        Initialize Monte Carlo simulator.

        Args:
            backtester: Backtester instance
        """
        self.backtester = backtester or Backtester(initial_cash=100000.0)

    def run_simulations(
        self,
        strategy_func: Callable,
        market_data: Dict[str, MarketData],
        num_simulations: int = 1000,
        simulation_method: str = 'bootstrap',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulations.

        Args:
            strategy_func: Strategy function
            market_data: Market data
            num_simulations: Number of simulations to run
            simulation_method: 'bootstrap' or 'shuffle_returns'
            start_date: Start date
            end_date: End date
            **kwargs: Additional parameters for strategy

        Returns:
            MonteCarloResult

        Example:
            >>> simulator = MonteCarloSimulator()
            >>> result = simulator.run_simulations(
            ...     strategy_func=my_strategy,
            ...     market_data={'SPY': spy_data},
            ...     num_simulations=1000,
            ...     simulation_method='bootstrap'
            ... )
            >>> stats = result.get_statistics()
            >>> print(f"Median return: {stats['returns']['median']:.2f}%")
            >>> print(f"95th percentile: {stats['returns']['p95']:.2f}%")
        """
        print("=" * 80)
        print("MONTE CARLO SIMULATION")
        print("=" * 80)
        print(f"Simulations: {num_simulations}")
        print(f"Method: {simulation_method}")
        print()

        simulations = []

        for i in range(num_simulations):
            if (i + 1) % 100 == 0:
                print(f"  Running simulation {i + 1}/{num_simulations}...")

            # Generate randomized data
            if simulation_method == 'bootstrap':
                randomized_data = self._bootstrap_data(market_data)
            elif simulation_method == 'shuffle_returns':
                randomized_data = self._shuffle_returns(market_data)
            else:
                raise ValueError(f"Unknown simulation method: {simulation_method}")

            # Run backtest
            try:
                result = self.backtester.run_backtest(
                    strategy_name=f"MC_Sim_{i + 1}",
                    market_data=randomized_data,
                    strategy_func=strategy_func,
                    start_date=start_date,
                    end_date=end_date
                )
                simulations.append(result)

            except Exception as e:
                print(f"  Warning: Simulation {i + 1} failed: {e}")

        print(f"\n✓ Completed {len(simulations)} simulations")
        print()

        return MonteCarloResult(simulations)

    def _bootstrap_data(self, market_data: Dict[str, MarketData]) -> Dict[str, MarketData]:
        """
        Bootstrap resample the market data.

        Creates new data series by randomly sampling with replacement.
        """
        bootstrapped = {}

        for symbol, data in market_data.items():
            # Sample with replacement
            sampled_points = random.choices(data.data, k=len(data.data))

            # Sort by original date order (maintain time series structure)
            sampled_points.sort(key=lambda x: x.date)

            bootstrapped[symbol] = MarketData(
                symbol=symbol,
                data=sampled_points,
                metadata={'source': 'bootstrap', 'original_size': len(data.data)}
            )

        return bootstrapped

    def _shuffle_returns(self, market_data: Dict[str, MarketData]) -> Dict[str, MarketData]:
        """
        Shuffle daily returns and reconstruct price series.

        Preserves return distribution but randomizes sequence.
        """
        shuffled = {}

        for symbol, data in market_data.items():
            if len(data.data) < 2:
                shuffled[symbol] = data
                continue

            # Calculate returns
            returns = []
            for i in range(1, len(data.data)):
                prev_close = data.data[i - 1].close
                curr_close = data.data[i].close
                ret = (curr_close - prev_close) / prev_close
                returns.append(ret)

            # Shuffle returns
            random.shuffle(returns)

            # Reconstruct price series
            new_data = [data.data[0]]  # Keep first point
            current_price = data.data[0].close

            for i, ret in enumerate(returns):
                new_price = current_price * (1 + ret)

                # Create new OHLCV (simplified - just use close for all)
                new_point = OHLCV(
                    date=data.data[i + 1].date,
                    open=new_price,
                    high=new_price,
                    low=new_price,
                    close=new_price,
                    volume=data.data[i + 1].volume,
                    adjusted_close=new_price
                )
                new_data.append(new_point)
                current_price = new_price

            shuffled[symbol] = MarketData(
                symbol=symbol,
                data=new_data,
                metadata={'source': 'shuffled_returns', 'original_size': len(data.data)}
            )

        return shuffled

    def run_parameter_uncertainty(
        self,
        strategy_class: type,
        param_ranges: Dict[str, tuple],
        market_data: Dict[str, MarketData],
        num_simulations: int = 500,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> MonteCarloResult:
        """
        Test parameter uncertainty by randomly sampling parameter space.

        Args:
            strategy_class: Strategy class
            param_ranges: Dict of param_name -> (min, max) ranges
            market_data: Market data
            num_simulations: Number of random parameter combinations
            start_date: Start date
            end_date: End date

        Returns:
            MonteCarloResult

        Example:
            >>> simulator = MonteCarloSimulator()
            >>> result = simulator.run_parameter_uncertainty(
            ...     strategy_class=MomentumStrategy,
            ...     param_ranges={'lookback_days': (30, 252)},
            ...     market_data={'SPY': spy_data},
            ...     num_simulations=500
            ... )
        """
        print("=" * 80)
        print("PARAMETER UNCERTAINTY ANALYSIS")
        print("=" * 80)
        print(f"Simulations: {num_simulations}")
        print(f"Parameters: {list(param_ranges.keys())}")
        print()

        simulations = []

        for i in range(num_simulations):
            if (i + 1) % 100 == 0:
                print(f"  Simulation {i + 1}/{num_simulations}...")

            # Random parameter values
            params = {}
            for param_name, (min_val, max_val) in param_ranges.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[param_name] = random.randint(min_val, max_val)
                else:
                    params[param_name] = random.uniform(min_val, max_val)

            # Instantiate strategy
            try:
                strategy = strategy_class(**params)

                result = self.backtester.run_backtest(
                    strategy_name=f"MC_Params_{i + 1}",
                    market_data=market_data,
                    strategy_func=strategy,
                    start_date=start_date,
                    end_date=end_date
                )
                simulations.append(result)

            except Exception as e:
                print(f"  Warning: Simulation {i + 1} failed with params {params}: {e}")

        print(f"\n✓ Completed {len(simulations)} simulations")
        print()

        return MonteCarloResult(simulations)
