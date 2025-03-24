from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class Holding:
    symbol: str
    name: str
    quantity: int
    current_price: Decimal
    sector: Optional[str] = None
    weight: float = 0.0

    def __post_init__(self):
        """Validate holding data after initialization."""
        # Validate symbol
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            raise ValueError("Symbol must be a non-empty string")
        self.symbol = self.symbol.strip().upper()
        
        # Validate name
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Name must be a non-empty string")
        self.name = self.name.strip()
        
        # Validate quantity
        if not isinstance(self.quantity, int):
            try:
                self.quantity = int(self.quantity)
            except (TypeError, ValueError):
                raise ValueError("Quantity must be an integer")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        # Validate current_price
        if not isinstance(self.current_price, Decimal):
            try:
                self.current_price = Decimal(str(self.current_price))
            except (TypeError, ValueError, ArithmeticError):
                raise ValueError("Current price must be a valid decimal number")
        if self.current_price <= 0:
            raise ValueError("Current price must be positive")
        
        # Validate sector
        if self.sector is not None:
            if not isinstance(self.sector, str) or not self.sector.strip():
                raise ValueError("Sector must be a non-empty string or None")
            self.sector = self.sector.strip()
        
        # Validate weight
        if not isinstance(self.weight, (int, float)):
            try:
                self.weight = float(self.weight)
            except (TypeError, ValueError):
                raise ValueError("Weight must be a number")
        if not 0 <= self.weight <= 1:
            raise ValueError("Weight must be between 0 and 1")

    @property
    def total_value(self) -> Decimal:
        """Calculate the total value of the holding."""
        return self.current_price * Decimal(str(self.quantity))

    def update_price(self, new_price: Decimal) -> None:
        """Update the current price of the holding."""
        if not isinstance(new_price, Decimal):
            try:
                new_price = Decimal(str(new_price))
            except (TypeError, ValueError, ArithmeticError):
                raise ValueError("New price must be a valid decimal number")
        if new_price <= 0:
            raise ValueError("New price must be positive")
        self.current_price = new_price

    def update_weight(self, new_weight: float) -> None:
        """Update the weight of the holding."""
        if not isinstance(new_weight, (int, float)):
            try:
                new_weight = float(new_weight)
            except (TypeError, ValueError):
                raise ValueError("Weight must be a number")
        if not 0 <= new_weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        self.weight = new_weight

    def to_dict(self) -> dict:
        """Convert holding to dictionary format."""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "quantity": self.quantity,
            "current_price": str(self.current_price),
            "sector": self.sector,
            "weight": self.weight
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Holding':
        """Create holding from dictionary format."""
        required_fields = ["symbol", "name", "quantity", "current_price"]
        missing_fields = [field for field in required_fields if field not in data]
        
        # Handle price field compatibility
        if 'price' in data and 'current_price' not in data:
            data['current_price'] = data.pop('price')
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
        return cls(
            symbol=str(data["symbol"]),
            name=str(data["name"]),
            quantity=int(data["quantity"]),
            current_price=Decimal(str(data["current_price"])),
            sector=data.get("sector"),
            weight=float(data.get("weight", 0.0))
        ) 