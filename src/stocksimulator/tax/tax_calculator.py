"""
Tax Calculator

Calculate capital gains taxes and model tax-aware strategies.
"""

from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TaxTerm(Enum):
    """Tax term classification."""
    SHORT_TERM = "short_term"  # < 1 year
    LONG_TERM = "long_term"    # >= 1 year


@dataclass
class TaxLot:
    """
    Represents a tax lot (purchase of shares).

    Used for tracking cost basis and holding period.
    """
    symbol: str
    quantity: float
    purchase_price: float
    purchase_date: date

    @property
    def cost_basis(self) -> float:
        """Total cost basis of this lot."""
        return self.quantity * self.purchase_price


@dataclass
class CapitalGain:
    """Represents a realized capital gain/loss."""
    symbol: str
    quantity: float
    cost_basis: float
    sale_price: float
    sale_date: date
    purchase_date: date
    term: TaxTerm

    @property
    def gain_loss(self) -> float:
        """Gain or loss in dollars."""
        return (self.sale_price - (self.cost_basis / self.quantity)) * self.quantity

    @property
    def gain_loss_pct(self) -> float:
        """Gain or loss as percentage."""
        return ((self.sale_price * self.quantity) - self.cost_basis) / self.cost_basis * 100


class TaxCalculator:
    """
    Calculate taxes on investment gains.

    Supports:
    - Short-term vs long-term capital gains
    - FIFO, LIFO, or specific lot identification
    - Tax-loss harvesting
    - Wash sale rules
    """

    def __init__(
        self,
        short_term_rate: float = 0.24,  # 24% short-term rate
        long_term_rate: float = 0.15,   # 15% long-term rate
        lot_method: str = 'FIFO'        # FIFO, LIFO, or SpecID
    ):
        """
        Initialize tax calculator.

        Args:
            short_term_rate: Tax rate for short-term gains (< 1 year)
            long_term_rate: Tax rate for long-term gains (>= 1 year)
            lot_method: Method for identifying sold shares
        """
        self.short_term_rate = short_term_rate
        self.long_term_rate = long_term_rate
        self.lot_method = lot_method

        # Track tax lots for each symbol
        self.tax_lots: Dict[str, List[TaxLot]] = {}

        # Track realized gains
        self.realized_gains: List[CapitalGain] = []

    def record_purchase(
        self,
        symbol: str,
        quantity: float,
        price: float,
        purchase_date: date
    ):
        """
        Record a purchase (creates a tax lot).

        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Purchase price per share
            purchase_date: Date of purchase
        """
        if symbol not in self.tax_lots:
            self.tax_lots[symbol] = []

        lot = TaxLot(
            symbol=symbol,
            quantity=quantity,
            purchase_price=price,
            purchase_date=purchase_date
        )

        self.tax_lots[symbol].append(lot)

    def record_sale(
        self,
        symbol: str,
        quantity: float,
        price: float,
        sale_date: date
    ) -> List[CapitalGain]:
        """
        Record a sale and calculate capital gains.

        Args:
            symbol: Stock symbol
            quantity: Number of shares sold
            price: Sale price per share
            sale_date: Date of sale

        Returns:
            List of CapitalGain objects
        """
        if symbol not in self.tax_lots or not self.tax_lots[symbol]:
            # No lots available - shouldn't happen in proper backtest
            return []

        gains = []
        remaining_quantity = quantity

        # Select lots based on method
        if self.lot_method == 'FIFO':
            lots = self.tax_lots[symbol]  # First in, first out
        elif self.lot_method == 'LIFO':
            lots = list(reversed(self.tax_lots[symbol]))  # Last in, first out
        else:
            lots = self.tax_lots[symbol]

        # Process sale against lots
        lots_to_remove = []

        for lot in lots:
            if remaining_quantity <= 0:
                break

            # Determine how much to sell from this lot
            sell_qty = min(remaining_quantity, lot.quantity)

            # Determine holding period
            holding_days = (sale_date - lot.purchase_date).days
            term = TaxTerm.LONG_TERM if holding_days >= 365 else TaxTerm.SHORT_TERM

            # Create capital gain
            gain = CapitalGain(
                symbol=symbol,
                quantity=sell_qty,
                cost_basis=sell_qty * lot.purchase_price,
                sale_price=price,
                sale_date=sale_date,
                purchase_date=lot.purchase_date,
                term=term
            )

            gains.append(gain)
            self.realized_gains.append(gain)

            # Update lot
            lot.quantity -= sell_qty
            remaining_quantity -= sell_qty

            if lot.quantity <= 0.0001:  # Essentially zero
                lots_to_remove.append(lot)

        # Remove depleted lots
        for lot in lots_to_remove:
            self.tax_lots[symbol].remove(lot)

        return gains

    def calculate_taxes(
        self,
        year: Optional[int] = None
    ) -> Dict:
        """
        Calculate total taxes owed.

        Args:
            year: Tax year (None = all gains)

        Returns:
            Dictionary with tax breakdown
        """
        # Filter gains by year if specified
        if year:
            gains = [g for g in self.realized_gains if g.sale_date.year == year]
        else:
            gains = self.realized_gains

        # Separate short-term and long-term
        st_gains = [g for g in gains if g.term == TaxTerm.SHORT_TERM]
        lt_gains = [g for g in gains if g.term == TaxTerm.LONG_TERM]

        # Calculate total gains/losses
        st_total = sum(g.gain_loss for g in st_gains)
        lt_total = sum(g.gain_loss for g in lt_gains)

        # Calculate taxes (no tax on losses)
        st_tax = max(0, st_total * self.short_term_rate)
        lt_tax = max(0, lt_total * self.long_term_rate)

        return {
            'short_term_gains': st_total,
            'long_term_gains': lt_total,
            'total_gains': st_total + lt_total,
            'short_term_tax': st_tax,
            'long_term_tax': lt_tax,
            'total_tax': st_tax + lt_tax,
            'num_short_term_trades': len(st_gains),
            'num_long_term_trades': len(lt_gains),
            'effective_tax_rate': (st_tax + lt_tax) / (st_total + lt_total) if (st_total + lt_total) > 0 else 0
        }

    def get_unrealized_gains(
        self,
        current_prices: Dict[str, float],
        current_date: date
    ) -> Dict:
        """
        Calculate unrealized gains on current holdings.

        Args:
            current_prices: Current prices for each symbol
            current_date: Current date

        Returns:
            Dictionary with unrealized gains breakdown
        """
        unrealized_st = 0.0
        unrealized_lt = 0.0

        for symbol, lots in self.tax_lots.items():
            if symbol not in current_prices:
                continue

            current_price = current_prices[symbol]

            for lot in lots:
                holding_days = (current_date - lot.purchase_date).days
                gain = (current_price - lot.purchase_price) * lot.quantity

                if holding_days >= 365:
                    unrealized_lt += gain
                else:
                    unrealized_st += gain

        # Calculate potential tax liability
        potential_st_tax = max(0, unrealized_st * self.short_term_rate)
        potential_lt_tax = max(0, unrealized_lt * self.long_term_rate)

        return {
            'unrealized_short_term': unrealized_st,
            'unrealized_long_term': unrealized_lt,
            'total_unrealized': unrealized_st + unrealized_lt,
            'potential_short_term_tax': potential_st_tax,
            'potential_long_term_tax': potential_lt_tax,
            'total_potential_tax': potential_st_tax + potential_lt_tax
        }

    def find_tax_loss_harvest_opportunities(
        self,
        current_prices: Dict[str, float],
        current_date: date,
        min_loss: float = 1000.0
    ) -> List[Tuple[str, TaxLot, float]]:
        """
        Find opportunities for tax-loss harvesting.

        Args:
            current_prices: Current prices
            current_date: Current date
            min_loss: Minimum loss to consider

        Returns:
            List of (symbol, lot, unrealized_loss) tuples
        """
        opportunities = []

        for symbol, lots in self.tax_lots.items():
            if symbol not in current_prices:
                continue

            current_price = current_prices[symbol]

            for lot in lots:
                unrealized_loss = (current_price - lot.purchase_price) * lot.quantity

                # Check wash sale rule (simplified - 30 days)
                days_held = (current_date - lot.purchase_date).days

                if unrealized_loss < -min_loss and days_held >= 30:
                    opportunities.append((symbol, lot, unrealized_loss))

        # Sort by largest loss first
        opportunities.sort(key=lambda x: x[2])

        return opportunities

    def get_summary(self) -> Dict:
        """Get comprehensive tax summary."""
        tax_info = self.calculate_taxes()

        return {
            **tax_info,
            'total_trades': len(self.realized_gains),
            'total_lots_remaining': sum(len(lots) for lots in self.tax_lots.values())
        }
