from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ConditionType(Enum):
    GT = "greater_than"
    LT = "less_than"
    EQ = "equal_to"
    NEQ = "not_equal_to"

@dataclass
class Condition:
    type: ConditionType
    metric: str
    threshold: float
    symbol: Optional[str] = None

    def evaluate(self, value: float) -> bool:
        """Evaluate the condition against a value."""
        if self.type == ConditionType.GT:
            return value > self.threshold
        elif self.type == ConditionType.LT:
            return value < self.threshold
        elif self.type == ConditionType.EQ:
            return abs(value - self.threshold) < 0.0001
        elif self.type == ConditionType.NEQ:
            return abs(value - self.threshold) >= 0.0001
        return False

    def __str__(self) -> str:
        """Return a string representation of the condition."""
        symbol_str = f" for {self.symbol}" if self.symbol else ""
        return f"{self.metric}{symbol_str} {self.type.value} {self.threshold}" 