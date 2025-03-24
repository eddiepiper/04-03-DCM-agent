from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Callable

class AlertType(Enum):
    PRICE = "price"
    RISK = "risk"
    PERFORMANCE = "performance"
    REBALANCE = "rebalance"

class ConditionType(Enum):
    ABOVE = "above"
    BELOW = "below"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"

@dataclass
class Alert:
    alert_type: AlertType
    symbol: str
    threshold: Decimal
    message: str
    conditions: Optional[List[Dict]] = None
    auto_rebalance: bool = False
    expiration: Optional[datetime] = None
    is_triggered: bool = False
    is_active: bool = True
    metric: Optional[str] = None

    def __post_init__(self):
        """Validate alert data after initialization."""
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not isinstance(self.threshold, Decimal):
            self.threshold = Decimal(str(self.threshold))
        if not self.message:
            raise ValueError("Message cannot be empty")
        if self.expiration and self.expiration < datetime.now():
            raise ValueError("Expiration date cannot be in the past")
        if self.alert_type == AlertType.RISK and not self.metric:
            raise ValueError("Risk alerts must specify a metric")
        if self.alert_type == AlertType.PERFORMANCE and not self.metric:
            raise ValueError("Performance alerts must specify a metric")

    def check_conditions(self, current_value: Decimal) -> bool:
        """Check if alert conditions are met."""
        if not self.is_active or (self.expiration and self.expiration < datetime.now()):
            return False

        if self.alert_type == AlertType.PRICE:
            if self.conditions:
                for condition in self.conditions:
                    if condition["type"] == ConditionType.ABOVE and current_value <= condition["value"]:
                        return False
                    elif condition["type"] == ConditionType.BELOW and current_value >= condition["value"]:
                        return False
            else:
                if current_value <= self.threshold:
                    return False
        elif self.alert_type in [AlertType.RISK, AlertType.PERFORMANCE]:
            if current_value <= self.threshold:
                return False

        self.is_triggered = True
        return True

    def to_dict(self) -> Dict:
        """Convert alert to dictionary format."""
        return {
            "alert_type": self.alert_type.value,
            "symbol": self.symbol,
            "threshold": str(self.threshold),
            "message": self.message,
            "conditions": self.conditions,
            "auto_rebalance": self.auto_rebalance,
            "expiration": self.expiration.isoformat() if self.expiration else None,
            "is_triggered": self.is_triggered,
            "is_active": self.is_active,
            "metric": self.metric
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Create alert from dictionary format."""
        return cls(
            alert_type=AlertType(data["alert_type"]),
            symbol=data["symbol"],
            threshold=Decimal(data["threshold"]),
            message=data["message"],
            conditions=data.get("conditions"),
            auto_rebalance=data.get("auto_rebalance", False),
            expiration=datetime.fromisoformat(data["expiration"]) if data.get("expiration") else None,
            is_triggered=data.get("is_triggered", False),
            is_active=data.get("is_active", True),
            metric=data.get("metric")
        )

class AlertManager:
    def __init__(self):
        self.alerts: Dict[AlertType, List[Alert]] = {
            alert_type: [] for alert_type in AlertType
        }
        self.rebalance_history: List[Dict] = []
        self.rebalance_callback: Optional[Callable] = None

    def add_price_alert(
        self,
        symbol: str,
        threshold: Decimal,
        condition: ConditionType,
        message: str,
        auto_rebalance: bool = False,
        expiration: Optional[datetime] = None
    ) -> Alert:
        """Add a price alert."""
        alert = Alert(
            alert_type=AlertType.PRICE,
            symbol=symbol,
            threshold=threshold,
            message=message,
            conditions=[{"type": condition, "value": threshold}],
            auto_rebalance=auto_rebalance,
            expiration=expiration
        )
        self.alerts[AlertType.PRICE].append(alert)
        return alert

    def add_risk_alert(
        self,
        symbol: str,
        metric: str,
        threshold: Decimal,
        condition: ConditionType,
        message: str,
        auto_rebalance: bool = False,
        expiration: Optional[datetime] = None
    ) -> Alert:
        """Add a risk alert."""
        alert = Alert(
            alert_type=AlertType.RISK,
            symbol=symbol,
            threshold=threshold,
            message=message,
            conditions=[{"type": condition, "value": threshold}],
            auto_rebalance=auto_rebalance,
            expiration=expiration,
            metric=metric
        )
        self.alerts[AlertType.RISK].append(alert)
        return alert

    def add_performance_alert(
        self,
        symbol: str,
        metric: str,
        threshold: Decimal,
        condition: ConditionType,
        message: str,
        auto_rebalance: bool = False,
        expiration: Optional[datetime] = None
    ) -> Alert:
        """Add a performance alert."""
        alert = Alert(
            alert_type=AlertType.PERFORMANCE,
            symbol=symbol,
            threshold=threshold,
            message=message,
            conditions=[{"type": condition, "value": threshold}],
            auto_rebalance=auto_rebalance,
            expiration=expiration,
            metric=metric
        )
        self.alerts[AlertType.PERFORMANCE].append(alert)
        return alert

    def check_alerts(self, market_data: Dict) -> List[Alert]:
        """Check all alerts against current market data."""
        triggered_alerts = []
        
        for alert_type, alerts in self.alerts.items():
            for alert in alerts:
                if not alert.is_active:
                    continue
                    
                if alert_type == AlertType.PRICE:
                    if alert.symbol in market_data and "price" in market_data[alert.symbol]:
                        if alert.check_conditions(market_data[alert.symbol]["price"]):
                            triggered_alerts.append(alert)
                            if alert.auto_rebalance and self.rebalance_callback:
                                self.rebalance_callback(alert)
                elif alert_type == AlertType.RISK:
                    if alert.symbol in market_data and alert.metric in market_data[alert.symbol]:
                        if alert.check_conditions(market_data[alert.symbol][alert.metric]):
                            triggered_alerts.append(alert)
                            if alert.auto_rebalance and self.rebalance_callback:
                                self.rebalance_callback(alert)
                elif alert_type == AlertType.PERFORMANCE:
                    if alert.symbol in market_data and alert.metric in market_data[alert.symbol]:
                        if alert.check_conditions(market_data[alert.symbol][alert.metric]):
                            triggered_alerts.append(alert)
                            if alert.auto_rebalance and self.rebalance_callback:
                                self.rebalance_callback(alert)
        
        return triggered_alerts

    def deactivate_alert(self, alert: Alert) -> None:
        """Deactivate an alert."""
        alert.is_active = False

    def record_rebalance(self, symbol: str, price: Decimal, value: Decimal) -> None:
        """Record a rebalance operation."""
        self.rebalance_history.append({
            "symbol": symbol,
            "price": str(price),
            "value": str(value),
            "timestamp": datetime.now().isoformat()
        })

    def set_rebalance_callback(self, callback: Callable) -> None:
        """Set the callback function for auto-rebalancing."""
        self.rebalance_callback = callback

    def get_active_alerts(self) -> Dict[AlertType, List[Alert]]:
        """Get all active alerts."""
        return {
            alert_type: [alert for alert in alerts if alert.is_active]
            for alert_type, alerts in self.alerts.items()
        }

    def get_rebalancing_history(self) -> List[Dict]:
        """Get rebalancing history."""
        return self.rebalance_history

    def get_rebalancing_costs(self) -> Decimal:
        """Calculate total rebalancing costs."""
        return sum(Decimal(record["value"]) for record in self.rebalance_history) 