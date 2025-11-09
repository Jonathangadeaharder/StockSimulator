"""
Transaction data model

Represents a single transaction (buy, sell, dividend, etc.).
"""

from typing import Optional
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """Transaction type enumeration."""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    SPLIT = "SPLIT"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    FEE = "FEE"
    REBALANCE = "REBALANCE"


class Transaction:
    """
    A transaction record.

    Attributes:
        transaction_id: Unique transaction identifier
        portfolio_id: Associated portfolio ID
        symbol: Stock ticker symbol (None for cash transactions)
        transaction_type: Type of transaction
        shares: Number of shares (None for cash transactions)
        price: Price per share (None for cash transactions)
        amount: Transaction amount for cash transactions
        transaction_cost: Fees and costs
        timestamp: Transaction timestamp
        notes: Optional notes
    """

    def __init__(
        self,
        transaction_id: str,
        portfolio_id: str,
        symbol: Optional[str],
        transaction_type: str,
        shares: Optional[float] = None,
        price: Optional[float] = None,
        amount: Optional[float] = None,
        transaction_cost: float = 0.0,
        timestamp: Optional[datetime] = None,
        notes: Optional[str] = None
    ):
        """
        Initialize a transaction.

        Args:
            transaction_id: Unique identifier
            portfolio_id: Associated portfolio
            symbol: Stock symbol
            transaction_type: BUY, SELL, DIVIDEND, etc.
            shares: Number of shares
            price: Price per share
            amount: Dollar amount (for cash transactions)
            transaction_cost: Fees and costs
            timestamp: Transaction time (default: now)
            notes: Optional notes
        """
        self.transaction_id = transaction_id
        self.portfolio_id = portfolio_id
        self.symbol = symbol
        self.transaction_type = transaction_type
        self.shares = shares
        self.price = price
        self.amount = amount
        self.transaction_cost = transaction_cost
        self.timestamp = timestamp or datetime.utcnow()
        self.notes = notes

    def get_total_value(self) -> float:
        """Calculate total transaction value including costs."""
        if self.amount is not None:
            return self.amount + self.transaction_cost
        elif self.shares is not None and self.price is not None:
            base_value = abs(self.shares * self.price)
            if self.transaction_type in ['BUY', 'REBALANCE']:
                return base_value + self.transaction_cost
            else:  # SELL
                return base_value - self.transaction_cost
        return 0.0

    def get_net_cash_impact(self) -> float:
        """
        Calculate net impact on cash balance.

        Returns:
            Positive for cash inflows, negative for outflows
        """
        total_value = self.get_total_value()

        if self.transaction_type in ['BUY', 'FEE', 'WITHDRAWAL']:
            return -total_value  # Cash outflow
        elif self.transaction_type in ['SELL', 'DIVIDEND', 'DEPOSIT']:
            return total_value  # Cash inflow
        elif self.transaction_type == 'REBALANCE':
            # Rebalance can be buy or sell
            if self.shares and self.shares > 0:
                return -total_value  # Buy
            else:
                return total_value  # Sell

        return 0.0

    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            'transaction_id': self.transaction_id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'transaction_type': self.transaction_type,
            'shares': self.shares,
            'price': self.price,
            'amount': self.amount,
            'transaction_cost': self.transaction_cost,
            'total_value': self.get_total_value(),
            'net_cash_impact': self.get_net_cash_impact(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary."""
        timestamp = None
        if data.get('timestamp'):
            timestamp = datetime.fromisoformat(data['timestamp'])

        return cls(
            transaction_id=data['transaction_id'],
            portfolio_id=data['portfolio_id'],
            symbol=data.get('symbol'),
            transaction_type=data['transaction_type'],
            shares=data.get('shares'),
            price=data.get('price'),
            amount=data.get('amount'),
            transaction_cost=data.get('transaction_cost', 0.0),
            timestamp=timestamp,
            notes=data.get('notes')
        )

    def __repr__(self) -> str:
        if self.shares and self.price:
            return (f"Transaction({self.transaction_type} {self.shares:.2f} shares of "
                   f"{self.symbol} @ ${self.price:.2f})")
        elif self.amount:
            return f"Transaction({self.transaction_type} ${self.amount:.2f})"
        return f"Transaction({self.transaction_type})"
