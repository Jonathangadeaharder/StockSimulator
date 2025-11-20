"""
Base Strategy Class

Abstract base class for all trading strategies.

Phase 2 Enhancement: Added lifecycle management, state tracking, and callbacks.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import date

from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.market_data import MarketData


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.

    Phase 2 Enhancement: Enhanced with lifecycle management inspired by btester.

    Lifecycle:
        1. __init__(): Configure strategy parameters
        2. init(): Initialize state before backtest starts (NEW)
        3. next()/calculate_allocation(): Called for each time step
        4. finalize(): Cleanup after backtest completes (NEW)

    All strategies must implement the calculate_allocation method which
    returns target portfolio allocations based on current market conditions.

    Attributes:
        name: Strategy name
        description: Strategy description
        parameters: Dictionary of strategy parameters
        _state: Internal state dictionary (NEW)
        _initialized: Whether strategy has been initialized (NEW)
    """

    def __init__(self, name: str, description: str = "", parameters: Optional[Dict] = None):
        """
        Initialize strategy.

        Args:
            name: Strategy name
            description: Strategy description
            parameters: Dictionary of strategy-specific parameters
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}

        # Phase 2: State management
        self._state = {}
        self._initialized = False

    def init(
        self,
        symbols: List[str],
        initial_cash: float,
        start_date: date,
        end_date: date
    ) -> None:
        """
        Initialize strategy state before backtest starts.

        Phase 2 Enhancement: Lifecycle method called once before first step.

        Override this method to set up any strategy-specific state or
        perform initialization that requires backtest context.

        Args:
            symbols: List of tradeable symbols
            initial_cash: Starting capital
            start_date: Backtest start date
            end_date: Backtest end date

        Example:
            >>> def init(self, symbols, initial_cash, start_date, end_date):
            ...     super().init(symbols, initial_cash, start_date, end_date)
            ...     self.set_state('last_rebalance', None)
            ...     self.set_state('trade_count', 0)
        """
        self._state['symbols'] = symbols
        self._state['initial_cash'] = initial_cash
        self._state['start_date'] = start_date
        self._state['end_date'] = end_date
        self._state['step'] = 0
        self._initialized = True

    @abstractmethod
    def calculate_allocation(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate target portfolio allocation.

        This is the core method that each strategy must implement.

        Args:
            current_date: Current simulation date
            market_data: Dictionary of symbol -> MarketData
            portfolio: Current portfolio state
            current_prices: Dictionary of symbol -> current price

        Returns:
            Dictionary of symbol -> target allocation percentage
            Must sum to <= 100.0 (remainder is cash)

        Example:
            {'SPY': 60.0, 'TLT': 40.0}  # 60% SPY, 40% TLT
            {'QQQ': 80.0}                # 80% QQQ, 20% cash
        """
        pass

    def next(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Optional[Dict[str, float]]:
        """
        Generate trading signal for current timestep.

        Phase 2 Enhancement: Alternative method name for calculate_allocation
        to match btester's lifecycle pattern.

        This method increments the step counter and delegates to
        calculate_allocation(). Override calculate_allocation() instead
        of this method.

        Args:
            current_date: Current simulation date
            market_data: Dictionary of symbol -> MarketData
            portfolio: Current portfolio state
            current_prices: Dictionary of symbol -> current price

        Returns:
            Target allocation dict or None for no rebalance
        """
        # Auto-initialize if not done
        if not self._initialized:
            # Get symbols from market_data
            symbols = list(market_data.keys()) if market_data else []
            self.init(symbols, 0, current_date, current_date)

        # Increment step counter
        self._state['step'] = self._state.get('step', 0) + 1

        # Delegate to calculate_allocation
        return self.calculate_allocation(current_date, market_data, portfolio, current_prices)

    def finalize(self, final_portfolio: Portfolio) -> None:
        """
        Cleanup after backtest completes.

        Phase 2 Enhancement: Lifecycle method called once after last step.

        Override this method to perform any cleanup, save state, or
        compute summary statistics.

        Args:
            final_portfolio: Final portfolio state

        Example:
            >>> def finalize(self, final_portfolio):
            ...     print(f"Total trades: {self.get_state('trade_count')}")
            ...     print(f"Final value: ${final_portfolio.get_total_value({}):,.2f}")
        """
        pass

    def on_trade(
        self,
        symbol: str,
        shares: float,
        price: float,
        transaction_type: str,
        cost: float
    ) -> None:
        """
        Callback when a trade is executed.

        Phase 2 Enhancement: Callback for trade tracking.

        Override this method to track trades, update internal state,
        or implement custom logic on trade execution.

        Args:
            symbol: Symbol traded
            shares: Number of shares
            price: Execution price
            transaction_type: 'BUY' or 'SELL'
            cost: Transaction cost paid

        Example:
            >>> def on_trade(self, symbol, shares, price, transaction_type, cost):
            ...     count = self.get_state('trade_count', 0)
            ...     self.set_state('trade_count', count + 1)
        """
        pass

    def on_rebalance(
        self,
        rebalance_date: date,
        old_weights: Dict[str, float],
        new_weights: Dict[str, float]
    ) -> None:
        """
        Callback when portfolio is rebalanced.

        Phase 2 Enhancement: Callback for rebalance tracking.

        Override this method to track rebalances or update strategy state
        based on portfolio changes.

        Args:
            rebalance_date: Date of rebalance
            old_weights: Weights before rebalance
            new_weights: Weights after rebalance

        Example:
            >>> def on_rebalance(self, date, old_weights, new_weights):
            ...     self.set_state('last_rebalance', date)
            ...     turnover = sum(abs(new_weights.get(s, 0) - old_weights.get(s, 0))
            ...                   for s in set(old_weights) | set(new_weights))
            ...     self.set_state('total_turnover',
            ...                   self.get_state('total_turnover', 0) + turnover)
        """
        pass

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get strategy state variable.

        Phase 2 Enhancement: State management helper.

        Args:
            key: State variable name
            default: Default value if key doesn't exist

        Returns:
            State value or default

        Example:
            >>> last_rebalance = self.get_state('last_rebalance')
            >>> trade_count = self.get_state('trade_count', 0)
        """
        return self._state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """
        Set strategy state variable.

        Phase 2 Enhancement: State management helper.

        Args:
            key: State variable name
            value: Value to store

        Example:
            >>> self.set_state('last_rebalance', current_date)
            >>> self.set_state('trade_count', 42)
        """
        self._state[key] = value

    def get_all_state(self) -> Dict[str, Any]:
        """
        Get all strategy state.

        Phase 2 Enhancement: State inspection helper.

        Returns:
            Copy of entire state dictionary
        """
        return self._state.copy()

    def validate_allocation(self, allocation: Dict[str, float]) -> bool:
        """
        Validate that allocation is valid.

        Args:
            allocation: Proposed allocation

        Returns:
            True if valid, False otherwise
        """
        if not allocation:
            return False

        total = sum(allocation.values())

        # Check total doesn't exceed 100%
        if total > 100.01:  # Small tolerance for floating point
            return False

        # Check all values are non-negative
        if any(v < 0 for v in allocation.values()):
            return False

        return True

    def get_lookback_data(
        self,
        market_data: MarketData,
        current_date: date,
        lookback_days: int
    ) -> List:
        """
        Get historical data for lookback period.

        Args:
            market_data: MarketData object
            current_date: Current date
            lookback_days: Number of days to look back

        Returns:
            List of OHLCV data points
        """
        all_data = sorted(market_data.data, key=lambda x: x.date)

        # Find current date index
        current_idx = None
        for i, d in enumerate(all_data):
            if d.date <= current_date:
                current_idx = i
            else:
                break

        if current_idx is None:
            return []

        start_idx = max(0, current_idx - lookback_days + 1)
        return all_data[start_idx:current_idx + 1]

    def calculate_moving_average(
        self,
        data: List,
        period: int,
        price_field: str = 'close'
    ) -> Optional[float]:
        """
        Calculate simple moving average.

        Args:
            data: List of OHLCV data points
            period: Moving average period
            price_field: Which price to use ('open', 'high', 'low', 'close')

        Returns:
            Moving average value or None if insufficient data
        """
        if len(data) < period:
            return None

        recent_data = data[-period:]
        prices = [getattr(d, price_field) for d in recent_data]

        return sum(prices) / len(prices)

    def calculate_returns(
        self,
        data: List,
        period: int = 1,
        price_field: str = 'close'
    ) -> List[float]:
        """
        Calculate period returns.

        Args:
            data: List of OHLCV data points
            period: Period for return calculation
            price_field: Which price to use

        Returns:
            List of returns
        """
        if len(data) < period + 1:
            return []

        returns = []
        for i in range(period, len(data)):
            current_price = getattr(data[i], price_field)
            previous_price = getattr(data[i - period], price_field)

            if previous_price > 0:
                ret = (current_price - previous_price) / previous_price
                returns.append(ret)

        return returns

    def calculate_volatility(
        self,
        returns: List[float],
        annualize: bool = True,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate volatility from returns.

        Args:
            returns: List of returns
            annualize: Whether to annualize
            periods_per_year: Periods per year for annualization

        Returns:
            Volatility (standard deviation)
        """
        if len(returns) < 2:
            return 0.0

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = variance ** 0.5

        if annualize:
            return std_dev * (periods_per_year ** 0.5)

        return std_dev

    def __call__(
        self,
        current_date: date,
        market_data: Dict[str, MarketData],
        portfolio: Portfolio,
        current_prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Callable interface for strategy.

        Allows using strategy as a function in backtests.
        """
        return self.calculate_allocation(current_date, market_data, portfolio, current_prices)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        return self.name
