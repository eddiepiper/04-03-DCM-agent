import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from dcm.alerts import AlertManager, AlertType, Alert
from dcm.conditions import Condition, ConditionType
from dcm.portfolio import Portfolio, Holding

@pytest.fixture
def sample_portfolio():
    portfolio = Portfolio()
    portfolio.add_holding(Holding(
        symbol="AAPL",
        quantity=Decimal("10"),
        price=Decimal("150.0"),
        name="Apple Inc.",
        sector="Technology"
    ))
    portfolio.add_holding(Holding(
        symbol="MSFT",
        quantity=Decimal("15"),
        price=Decimal("300.0"),
        name="Microsoft Corp.",
        sector="Technology"
    ))
    return portfolio

@pytest.fixture
def alert_manager():
    """Create an alert manager instance."""
    return AlertManager()

def test_add_price_alert(alert_manager):
    """Test adding a price alert."""
    alert = alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("150.0"),
        condition=ConditionType.ABOVE,
        message="AAPL price above $150",
        auto_rebalance=False
    )
    assert isinstance(alert, Alert)
    assert alert.alert_type == AlertType.PRICE
    assert alert.symbol == "AAPL"
    assert alert.threshold == Decimal("150.0")
    assert alert.message == "AAPL price above $150"

def test_add_risk_alert(alert_manager):
    """Test adding a risk alert."""
    alert = alert_manager.add_risk_alert(
        symbol="AAPL",
        metric="volatility",
        threshold=Decimal("0.2"),
        condition=ConditionType.ABOVE,
        message="AAPL volatility above 20%",
        auto_rebalance=True
    )
    assert isinstance(alert, Alert)
    assert alert.alert_type == AlertType.RISK
    assert alert.symbol == "AAPL"
    assert alert.threshold == Decimal("0.2")
    assert alert.message == "AAPL volatility above 20%"

def test_add_performance_alert(alert_manager):
    """Test adding a performance alert."""
    alert = alert_manager.add_performance_alert(
        symbol="AAPL",
        metric="sharpe_ratio",
        threshold=Decimal("1.5"),
        condition=ConditionType.BELOW,
        message="AAPL Sharpe ratio below 1.5",
        auto_rebalance=False
    )
    assert isinstance(alert, Alert)
    assert alert.alert_type == AlertType.PERFORMANCE
    assert alert.symbol == "AAPL"
    assert alert.threshold == Decimal("1.5")
    assert alert.message == "AAPL Sharpe ratio below 1.5"

def test_add_compound_alert(alert_manager):
    """Test adding a compound alert with multiple conditions."""
    conditions = [
        Condition(ConditionType.GT, "price_AAPL", 150.0, "AAPL"),
        Condition(ConditionType.LT, "beta", 1.5)
    ]
    alert_manager.add_compound_alert(
        conditions=conditions,
        message="Compound Alert",
        alert_type=AlertType.RISK,
        auto_rebalance=True
    )
    alerts = alert_manager.get_active_alerts()[AlertType.RISK]
    assert len(alerts) == 1
    assert len(alerts[0].conditions) == 2
    assert alerts[0].auto_rebalance is True

def test_record_rebalance(alert_manager):
    """Test recording a rebalance operation."""
    alert_manager.record_rebalance(
        symbol="AAPL",
        price=Decimal("150.0"),
        value=Decimal("15000.0"),
        timestamp=datetime.now()
    )
    assert len(alert_manager.rebalance_history) == 1
    assert alert_manager.rebalance_history[0]["symbol"] == "AAPL"

def test_get_rebalancing_costs(alert_manager):
    """Test retrieving rebalancing costs."""
    # Record multiple trades
    alert_manager.record_rebalance("AAPL", 0.3, 0.4, 10, 150.0, 1500.0)
    alert_manager.record_rebalance("GOOGL", 0.2, 0.3, 5, 2500.0, 12500.0)
    
    costs = alert_manager.get_rebalancing_costs()
    assert len(costs) == 2
    assert costs[0]["cost"] == 1500.0
    assert costs[1]["cost"] == 12500.0
    
    total_cost = alert_manager.get_total_rebalancing_cost()
    assert total_cost == 14000.0

def test_check_alerts(alert_manager):
    """Test checking alert conditions."""
    # Add test alerts
    alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("150.0"),
        condition=ConditionType.ABOVE,
        message="AAPL price above $150",
        auto_rebalance=False
    )
    alert_manager.add_risk_alert(
        symbol="MSFT",
        metric="volatility",
        threshold=Decimal("0.2"),
        condition=ConditionType.ABOVE,
        message="MSFT volatility above 20%",
        auto_rebalance=True
    )
    
    # Test market data
    market_data = {
        "AAPL": {"price": Decimal("160.0")},
        "MSFT": {"price": Decimal("300.0"), "volatility": Decimal("0.25")}
    }
    
    triggered_alerts = alert_manager.check_alerts(market_data)
    assert len(triggered_alerts) == 2
    assert all(alert.is_triggered for alert in triggered_alerts)

def test_deactivate_alert(alert_manager):
    """Test deactivating an alert."""
    alert = alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("150.0"),
        condition=ConditionType.ABOVE,
        message="AAPL price above $150",
        auto_rebalance=False
    )
    
    alert_manager.deactivate_alert(alert)
    assert not alert.is_active

def test_auto_rebalancing(alert_manager):
    """Test auto-rebalancing functionality."""
    assert alert_manager.auto_rebalance_enabled is False
    
    alert_manager.enable_auto_rebalancing(True)
    assert alert_manager.auto_rebalance_enabled is True
    
    alert_manager.enable_auto_rebalancing(False)
    assert alert_manager.auto_rebalance_enabled is False

def test_alert_validation(alert_manager):
    """Test alert validation and error handling."""
    with pytest.raises(ValueError):
        alert_manager.add_price_alert("", Decimal("150.0"), ConditionType.ABOVE, "AAPL price above $150", False)  # Empty symbol
    
    with pytest.raises(ValueError):
        alert_manager.add_risk_alert("", "volatility", Decimal("0.2"), ConditionType.ABOVE, "AAPL volatility above 20%", True)  # Empty metric
    
    with pytest.raises(ValueError):
        alert_manager.add_performance_alert("", "sharpe_ratio", Decimal("1.5"), ConditionType.BELOW, "AAPL Sharpe ratio below 1.5", False)  # Empty metric

def test_alert_creation():
    """Test alert creation with different types."""
    # Price alert
    price_alert = Alert(
        type=AlertType.PRICE,
        symbol="AAPL",
        message="Price above threshold",
        threshold=Decimal("160.0"),
        current_value=Decimal("150.0")
    )
    assert price_alert.type == AlertType.PRICE
    assert not price_alert.is_triggered()
    
    # Risk alert
    risk_alert = Alert(
        type=AlertType.RISK,
        symbol="PORTFOLIO",
        message="Portfolio volatility high",
        threshold=Decimal("0.2"),
        current_value=Decimal("0.15")
    )
    assert risk_alert.type == AlertType.RISK
    assert not risk_alert.is_triggered()

def test_alert_manager_add_alerts(alert_manager):
    """Test adding different types of alerts."""
    # Add price alert
    alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("160.0"),
        message="AAPL price alert"
    )
    
    # Add risk alert
    alert_manager.add_risk_alert(
        threshold=Decimal("0.2"),
        message="Portfolio risk alert"
    )
    
    # Add performance alert
    alert_manager.add_performance_alert(
        threshold=Decimal("-0.05"),
        message="Performance alert"
    )
    
    assert len(alert_manager.get_active_alerts()) == 3

def test_alert_checking(alert_manager, sample_portfolio):
    """Test alert checking against portfolio data."""
    # Add price alert that should trigger
    alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("140.0"),
        message="AAPL price below 140"
    )
    
    # Add risk alert that should not trigger
    alert_manager.add_risk_alert(
        threshold=Decimal("0.3"),
        message="Risk above 30%"
    )
    
    portfolio_data = {
        "prices": {"AAPL": Decimal("135.0")},
        "risk_metrics": {"volatility": Decimal("0.25")},
        "performance": {"daily_return": Decimal("-0.02")}
    }
    
    triggered_alerts = alert_manager.check_alerts(portfolio_data)
    assert len(triggered_alerts) == 1
    assert triggered_alerts[0].symbol == "AAPL"

def test_alert_deactivation(alert_manager):
    """Test alert deactivation."""
    # Add an alert
    alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("160.0"),
        message="AAPL price alert"
    )
    
    initial_count = len(alert_manager.get_active_alerts())
    
    # Deactivate all alerts for AAPL
    alert_manager.deactivate_alerts(symbol="AAPL")
    
    assert len(alert_manager.get_active_alerts()) < initial_count
    assert not any(alert.symbol == "AAPL" for alert in alert_manager.get_active_alerts())

def test_rebalancing_alerts(alert_manager, sample_portfolio):
    """Test rebalancing alerts and history."""
    # Record a rebalancing trade
    trade = {
        "symbol": "AAPL",
        "quantity": Decimal("5"),
        "price": Decimal("150.0"),
        "action": "BUY"
    }
    
    alert_manager.record_rebalance(trade)
    
    # Check rebalancing history
    history = alert_manager.get_rebalancing_history()
    assert len(history) == 1
    assert history[0]["symbol"] == "AAPL"
    
    # Check rebalancing costs
    costs = alert_manager.get_rebalancing_costs()
    assert costs > 0

def test_alert_expiration(alert_manager):
    """Test alert expiration."""
    alert = alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("150.0"),
        condition=ConditionType.ABOVE,
        message="AAPL price above $150",
        auto_rebalance=False,
        expiration=datetime.now() - timedelta(days=1)  # Expired alert
    )
    
    triggered_alerts = alert_manager.check_alerts({"AAPL": {"price": Decimal("160.0")}})
    assert len(triggered_alerts) == 0
    assert not alert.is_active

def test_alert_conditions(alert_manager):
    """Test different alert conditions."""
    # Test ABOVE condition
    alert_above = alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("150.0"),
        condition=ConditionType.ABOVE,
        message="AAPL price above $150",
        auto_rebalance=False
    )
    
    # Test BELOW condition
    alert_below = alert_manager.add_price_alert(
        symbol="MSFT",
        threshold=Decimal("300.0"),
        condition=ConditionType.BELOW,
        message="MSFT price below $300",
        auto_rebalance=False
    )
    
    market_data = {
        "AAPL": {"price": Decimal("160.0")},
        "MSFT": {"price": Decimal("290.0")}
    }
    
    triggered_alerts = alert_manager.check_alerts(market_data)
    assert len(triggered_alerts) == 2
    assert all(alert.is_triggered for alert in triggered_alerts)

def test_error_handling(alert_manager):
    """Test error handling in alert management."""
    # Test invalid alert type
    with pytest.raises(ValueError):
        alert_manager.add_price_alert(
            symbol="",
            threshold=Decimal("0.0"),
            message=""
        )
    
    # Test invalid threshold
    with pytest.raises(ValueError):
        alert_manager.add_risk_alert(
            threshold=Decimal("-1.0"),
            message="Invalid threshold"
        )
    
    # Test missing portfolio data
    triggered_alerts = alert_manager.check_alerts({})
    assert len(triggered_alerts) == 0

def test_alert_serialization(alert_manager):
    """Test alert serialization and deserialization."""
    # Add some alerts
    alert_manager.add_price_alert(
        symbol="AAPL",
        threshold=Decimal("160.0"),
        message="AAPL price alert"
    )
    alert_manager.add_risk_alert(
        threshold=Decimal("0.2"),
        message="Risk alert"
    )
    
    # Convert to dictionary
    alerts_dict = alert_manager.to_dict()
    
    # Create new alert manager from dictionary
    new_manager = AlertManager.from_dict(alerts_dict)
    
    # Verify alerts are equal
    assert len(new_manager.get_active_alerts()) == len(alert_manager.get_active_alerts())
    
    original_alerts = alert_manager.get_active_alerts()
    new_alerts = new_manager.get_active_alerts()
    
    for orig, new in zip(original_alerts, new_alerts):
        assert orig.type == new.type
        assert orig.symbol == new.symbol
        assert orig.threshold == new.threshold 