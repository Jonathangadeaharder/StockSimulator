"""
Portfolio Manager

Manages portfolio operations including allocation, rebalancing, and performance tracking.
"""

from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from stocksimulator.models.portfolio import Portfolio
from stocksimulator.models.position import Position
from stocksimulator.models.transaction import Transaction
from stocksimulator.models.market_data import MarketData


class PortfolioManager:
    """
    Manages portfolio operations and allocation strategies.

    This class provides high-level portfolio management capabilities including:
    - Portfolio creation and tracking
    - Allocation management
    - Rebalancing
    - Performance monitoring
    """

    def __init__(self):
        """Initialize portfolio manager."""
        self.portfolios: Dict[str, Portfolio] = {}

    def create_portfolio(
        self,
        portfolio_id: str,
        name: str,
        initial_cash: float = 100000.0
    ) -> Portfolio:
        """
        Create a new portfolio.

        Args:
            portfolio_id: Unique identifier
            name: Portfolio name
            initial_cash: Starting cash balance

        Returns:
            Created portfolio

        Raises:
            ValueError: If portfolio_id already exists
        """
        if portfolio_id in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} already exists")

        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            name=name,
            initial_cash=initial_cash
        )

        self.portfolios[portfolio_id] = portfolio
        return portfolio

    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        """Get portfolio by ID."""
        return self.portfolios.get(portfolio_id)

    def delete_portfolio(self, portfolio_id: str) -> bool:
        """Delete a portfolio."""
        if portfolio_id in self.portfolios:
            del self.portfolios[portfolio_id]
            return True
        return False

    def execute_trade(
        self,
        portfolio_id: str,
        symbol: str,
        shares: float,
        price: float,
        transaction_cost_bps: float = 2.0
    ) -> Optional[Transaction]:
        """
        Execute a trade (buy or sell).

        Args:
            portfolio_id: Portfolio identifier
            symbol: Stock symbol
            shares: Number of shares (positive=buy, negative=sell)
            price: Price per share
            transaction_cost_bps: Transaction cost in basis points

        Returns:
            Transaction object or None if insufficient funds
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return None

        # Calculate transaction cost
        trade_value = abs(shares * price)
        cost_pct = transaction_cost_bps / 10000
        transaction_cost = trade_value * cost_pct

        # Check if we have sufficient funds (for buys) or shares (for sells)
        if shares > 0:  # Buy
            total_cost = trade_value + transaction_cost
            if portfolio.cash < total_cost:
                return None  # Insufficient funds
        else:  # Sell
            position = portfolio.get_position(symbol)
            if not position or position.shares < abs(shares):
                return None  # Insufficient shares

        # Create transaction
        transaction = Transaction(
            transaction_id=f"trade_{symbol}_{datetime.utcnow().isoformat()}",
            portfolio_id=portfolio_id,
            symbol=symbol,
            transaction_type='BUY' if shares > 0 else 'SELL',
            shares=abs(shares),
            price=price,
            transaction_cost=transaction_cost
        )

        # Update portfolio
        portfolio.add_transaction(transaction)

        if shares > 0:  # Buy
            portfolio.cash -= (trade_value + transaction_cost)
            portfolio.add_position(Position(
                symbol=symbol,
                shares=shares,
                cost_basis=price
            ))
        else:  # Sell
            proceeds = trade_value - transaction_cost
            portfolio.cash += proceeds
            portfolio.add_position(Position(
                symbol=symbol,
                shares=shares,  # Negative
                cost_basis=price
            ))

        return transaction

    def rebalance_portfolio(
        self,
        portfolio_id: str,
        target_allocation: Dict[str, float],
        current_prices: Dict[str, float],
        transaction_cost_bps: float = 2.0
    ) -> List[Transaction]:
        """
        Rebalance portfolio to target allocation.

        Args:
            portfolio_id: Portfolio identifier
            target_allocation: Dictionary of symbol -> target percentage
            current_prices: Dictionary of symbol -> current price
            transaction_cost_bps: Transaction cost in basis points

        Returns:
            List of transactions executed
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return []

        return portfolio.rebalance(
            target_allocation,
            current_prices,
            transaction_cost_bps
        )

    def get_portfolio_performance(
        self,
        portfolio_id: str,
        current_prices: Dict[str, float]
    ) -> Optional[Dict]:
        """
        Get comprehensive portfolio performance metrics.

        Args:
            portfolio_id: Portfolio identifier
            current_prices: Dictionary of symbol -> current price

        Returns:
            Dictionary with performance metrics or None if portfolio not found
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return None

        returns = portfolio.get_returns(current_prices)
        allocation = portfolio.get_allocation(current_prices)
        total_value = portfolio.get_total_value(current_prices)

        # Calculate position-level performance
        positions_performance = {}
        for symbol, position in portfolio.positions.items():
            price = current_prices.get(symbol, position.cost_basis)
            pnl = position.get_unrealized_pnl(price)
            positions_performance[symbol] = pnl

        return {
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio.name,
            'total_value': total_value,
            'cash': portfolio.cash,
            'returns': returns,
            'allocation': allocation,
            'positions_performance': positions_performance,
            'num_positions': len(portfolio.positions),
            'num_transactions': len(portfolio.transactions),
            'created_at': portfolio.created_at.isoformat()
        }

    def get_all_portfolios_summary(self) -> List[Dict]:
        """Get summary of all portfolios."""
        return [
            {
                'portfolio_id': p.portfolio_id,
                'name': p.name,
                'num_positions': len(p.positions),
                'cash': p.cash,
                'initial_value': p.initial_value,
                'created_at': p.created_at.isoformat()
            }
            for p in self.portfolios.values()
        ]

    def calculate_optimal_allocation(
        self,
        symbols: List[str],
        market_data: Dict[str, MarketData],
        method: str = 'sharpe'
    ) -> Dict[str, float]:
        """
        Calculate optimal portfolio allocation.

        Args:
            symbols: List of symbols to include
            market_data: Dictionary of symbol -> MarketData
            method: Optimization method ('sharpe', 'min_variance', 'equal_weight')

        Returns:
            Dictionary of symbol -> allocation percentage
        """
        if method == 'equal_weight':
            # Equal weight allocation
            weight = 100.0 / len(symbols)
            return {symbol: weight for symbol in symbols}

        elif method == 'sharpe':
            # Maximum Sharpe ratio (simplified implementation)
            # In practice, this would use historical returns and covariance matrix
            # For now, return equal weight
            weight = 100.0 / len(symbols)
            return {symbol: weight for symbol in symbols}

        elif method == 'min_variance':
            # Minimum variance portfolio
            # Simplified: equal weight for now
            weight = 100.0 / len(symbols)
            return {symbol: weight for symbol in symbols}

        else:
            raise ValueError(f"Unknown optimization method: {method}")

    def __repr__(self) -> str:
        return f"PortfolioManager(portfolios={len(self.portfolios)})"
