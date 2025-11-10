"""
Portfolio data model

Represents a portfolio containing multiple positions and tracking performance metrics.
"""

from typing import Dict, List, Optional
from datetime import datetime
from .position import Position
from .transaction import Transaction


class Portfolio:
    """
    Portfolio containing multiple positions with performance tracking.

    Attributes:
        portfolio_id: Unique identifier for the portfolio
        name: Portfolio name
        positions: Dictionary of symbol -> Position
        cash: Available cash balance
        initial_value: Initial portfolio value
        transactions: List of all transactions
        created_at: Portfolio creation timestamp
    """

    def __init__(
        self,
        portfolio_id: str,
        name: str,
        initial_cash: float = 100000.0,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a new portfolio.

        Args:
            portfolio_id: Unique identifier
            name: Portfolio name
            initial_cash: Starting cash balance (default: $100,000)
            created_at: Creation timestamp (default: now)
        """
        self.portfolio_id = portfolio_id
        self.name = name
        self.cash = initial_cash
        self.initial_value = initial_cash
        self.positions: Dict[str, Position] = {}
        self.transactions: List[Transaction] = []
        self.created_at = created_at or datetime.utcnow()

    def add_position(self, position: Position) -> None:
        """Add or update a position in the portfolio."""
        if position.symbol in self.positions:
            # Merge with existing position
            existing = self.positions[position.symbol]
            total_shares = existing.shares + position.shares
            if total_shares == 0:
                # Position closed
                del self.positions[position.symbol]
            else:
                # Update average cost basis
                total_cost = (existing.shares * existing.cost_basis +
                            position.shares * position.cost_basis)
                existing.shares = total_shares
                existing.cost_basis = total_cost / total_shares
        else:
            self.positions[position.symbol] = position

    def remove_position(self, symbol: str) -> Optional[Position]:
        """Remove and return a position."""
        return self.positions.pop(symbol, None)

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get a position by symbol."""
        return self.positions.get(symbol)

    def add_transaction(self, transaction: Transaction) -> None:
        """Record a transaction."""
        self.transactions.append(transaction)

    def get_total_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.

        Args:
            current_prices: Dictionary of symbol -> current price

        Returns:
            Total portfolio value (cash + positions)
        """
        positions_value = sum(
            pos.shares * current_prices.get(pos.symbol, pos.cost_basis)
            for pos in self.positions.values()
        )
        return self.cash + positions_value

    def get_allocation(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Get current allocation percentages.

        Args:
            current_prices: Dictionary of symbol -> current price

        Returns:
            Dictionary of symbol -> allocation percentage
        """
        total_value = self.get_total_value(current_prices)
        if total_value == 0:
            return {}

        allocation = {}
        for symbol, pos in self.positions.items():
            position_value = pos.shares * current_prices.get(symbol, pos.cost_basis)
            allocation[symbol] = (position_value / total_value) * 100

        # Add cash allocation
        allocation['CASH'] = (self.cash / total_value) * 100

        return allocation

    def get_returns(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate portfolio returns.

        Args:
            current_prices: Dictionary of symbol -> current price

        Returns:
            Dictionary with total_return, dollar_return, percent_return
        """
        current_value = self.get_total_value(current_prices)
        dollar_return = current_value - self.initial_value
        percent_return = (dollar_return / self.initial_value) * 100 if self.initial_value > 0 else 0

        return {
            'total_return': dollar_return,
            'dollar_return': dollar_return,
            'percent_return': percent_return,
            'current_value': current_value,
            'initial_value': self.initial_value
        }

    def rebalance(
        self,
        target_allocation: Dict[str, float],
        current_prices: Dict[str, float],
        transaction_cost_bps: float = 2.0
    ) -> List[Transaction]:
        """
        Rebalance portfolio to target allocation.

        Args:
            target_allocation: Dictionary of symbol -> target percentage
            current_prices: Dictionary of symbol -> current price
            transaction_cost_bps: Transaction cost in basis points

        Returns:
            List of transactions executed during rebalancing
        """
        total_value = self.get_total_value(current_prices)
        current_allocation = self.get_allocation(current_prices)
        rebalance_transactions = []

        # Calculate required trades
        for symbol, target_pct in target_allocation.items():
            if symbol == 'CASH':
                continue

            current_pct = current_allocation.get(symbol, 0)
            diff_pct = target_pct - current_pct

            if abs(diff_pct) < 0.01:  # Skip if difference < 0.01%
                continue

            target_value = total_value * (target_pct / 100)
            current_value = total_value * (current_pct / 100)
            trade_value = target_value - current_value

            price = current_prices.get(symbol)
            if price is None or price <= 0:
                continue

            shares = trade_value / price

            # Apply transaction costs
            cost_pct = transaction_cost_bps / 10000
            transaction_cost = abs(trade_value) * cost_pct

            # Create transaction
            transaction = Transaction(
                transaction_id=f"rebalance_{symbol}_{datetime.utcnow().isoformat()}",
                portfolio_id=self.portfolio_id,
                symbol=symbol,
                transaction_type='BUY' if shares > 0 else 'SELL',
                shares=abs(shares),
                price=price,
                transaction_cost=transaction_cost,
                timestamp=datetime.utcnow()
            )

            rebalance_transactions.append(transaction)
            self.add_transaction(transaction)

            # Update position
            if shares > 0:
                # Buy
                total_cost = shares * price + transaction_cost
                self.cash -= total_cost
                self.add_position(Position(
                    symbol=symbol,
                    shares=shares,
                    cost_basis=price
                ))
            else:
                # Sell
                proceeds = abs(shares) * price - transaction_cost
                self.cash += proceeds
                self.add_position(Position(
                    symbol=symbol,
                    shares=shares,  # Negative shares
                    cost_basis=price
                ))

        return rebalance_transactions

    def __repr__(self) -> str:
        return (f"Portfolio(id={self.portfolio_id}, name={self.name}, "
                f"positions={len(self.positions)}, cash=${self.cash:,.2f})")
