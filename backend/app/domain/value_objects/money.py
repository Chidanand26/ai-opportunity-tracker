from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """
    Stipend or compensation amount with currency.
    Using Decimal (not float) to avoid floating-point rounding issues.
    """

    amount: Decimal
    currency: str = "USD"   # ISO 4217 code

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError(f"Currency must be a 3-letter ISO code, got {self.currency!r}")

    def display(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"

    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        return cls(amount=Decimal("0"), currency=currency)
