import pytest
from decimal import Decimal
from dcm.portfolio import Portfolio, PortfolioManager
from dcm.holdings import Holding

@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio for testing."""
    holdings = {
        "AAPL": Holding(
            symbol="AAPL",
            name="Apple Inc.",
            quantity=100,
            current_price=Decimal("150.0"),
            sector="Technology",
            weight=0.3
        ),
        "MSFT": Holding(
            symbol="MSFT",
            name="Microsoft Corp.",
            quantity=50,
            current_price=Decimal("300.0"),
            sector="Technology",
            weight=0.3
        ),
        "VTI": Holding(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            quantity=200,
            current_price=Decimal("220.0"),
            sector="ETF",
            weight=0.3
        ),
        "BND": Holding(
            symbol="BND",
            name="Vanguard Total Bond Market ETF",
            quantity=100,
            current_price=Decimal("85.0"),
            sector="Bond",
            weight=0.1
        )
    }
    return Portfolio(holdings=holdings)

@pytest.fixture
def sample_holding():
    """Create a sample holding for testing."""
    return Holding(
        symbol="AAPL",
        name="Apple Inc.",
        quantity=10,
        current_price=Decimal("150.0"),
        sector="Technology",
        weight=0.3
    )

@pytest.fixture
def portfolio_manager(sample_portfolio):
    """Create a portfolio manager with sample portfolio."""
    return PortfolioManager(portfolio=sample_portfolio)

def test_portfolio_creation():
    """Test portfolio creation and initialization."""
    portfolio = Portfolio()
    assert isinstance(portfolio.holdings, dict)
    assert len(portfolio.holdings) == 0
    assert portfolio.metrics['total_value'] == Decimal('0')

def test_portfolio_validation(sample_portfolio):
    """Test portfolio validation."""
    assert len(sample_portfolio.holdings) == 4
    assert sample_portfolio.metrics['total_value'] > 0
    assert abs(sum(h.weight for h in sample_portfolio.holdings.values()) - 1.0) < 0.0001

def test_add_holding(portfolio_manager):
    """Test adding a holding to the portfolio."""
    holding = Holding(
        symbol="NVDA",
        name="NVIDIA Corporation",
        quantity=50,
        current_price=Decimal("400.0"),
        sector="Technology",
        weight=0.2
    )
    portfolio_manager.add_holding(holding)
    assert "NVDA" in portfolio_manager.portfolio.holdings
    assert portfolio_manager.portfolio.holdings["NVDA"].total_value == Decimal("20000.0")

def test_remove_holding(portfolio_manager):
    """Test removing a holding from the portfolio."""
    symbol = "AAPL"
    assert symbol in portfolio_manager.portfolio.holdings
    portfolio_manager.remove_holding(symbol)
    assert symbol not in portfolio_manager.portfolio.holdings

def test_update_prices(portfolio_manager):
    """Test updating holding prices."""
    new_prices = {
        "AAPL": Decimal("160.0"),
        "MSFT": Decimal("310.0")
    }
    portfolio_manager.update_prices(new_prices)
    assert portfolio_manager.portfolio.holdings["AAPL"].current_price == Decimal("160.0")
    assert portfolio_manager.portfolio.holdings["MSFT"].current_price == Decimal("310.0")

def test_portfolio_metrics(sample_portfolio):
    """Test portfolio metrics calculation."""
    metrics = sample_portfolio.metrics
    assert isinstance(metrics, dict)
    assert 'total_value' in metrics
    assert 'sector_weights' in metrics
    assert 'risk_metrics' in metrics
    assert metrics['total_value'] > 0

def test_portfolio_serialization(sample_portfolio):
    """Test portfolio serialization and deserialization."""
    data = sample_portfolio.to_dict()
    assert isinstance(data, dict)
    assert 'holdings' in data
    assert 'metrics' in data
    
    new_portfolio = Portfolio.from_dict(data)
    assert len(new_portfolio.holdings) == len(sample_portfolio.holdings)
    assert new_portfolio.metrics['total_value'] == sample_portfolio.metrics['total_value']

def test_portfolio_manager_rebalancing(portfolio_manager):
    """Test portfolio rebalancing calculations."""
    target_weights = {
        "AAPL": 0.25,
        "MSFT": 0.25,
        "VTI": 0.4,
        "BND": 0.1
    }
    trades = portfolio_manager.calculate_rebalancing_trades(target_weights)
    assert len(trades) > 0
    for trade in trades:
        assert 'symbol' in trade
        assert 'quantity' in trade
        assert 'price' in trade
        assert 'value' in trade
        assert 'old_weight' in trade
        assert 'new_weight' in trade

def test_portfolio_manager_trade_execution(portfolio_manager):
    """Test executing rebalancing trades."""
    initial_holdings = dict(portfolio_manager.portfolio.holdings)
    trades = [
        {
            'symbol': 'AAPL',
            'quantity': 50,
            'price': float(portfolio_manager.portfolio.holdings['AAPL'].current_price),
            'value': 7500.0,
            'old_weight': 0.3,
            'new_weight': 0.35
        }
    ]
    success = portfolio_manager.execute_rebalancing_trades(trades)
    assert success
    assert portfolio_manager.portfolio.holdings['AAPL'].quantity == initial_holdings['AAPL'].quantity + 50

def test_error_handling():
    """Test error handling in portfolio management."""
    portfolio = Portfolio()

    # Test adding invalid holding
    with pytest.raises(ValueError):
        portfolio.add_holding(None)

    # Test removing non-existent holding
    with pytest.raises(KeyError):
        portfolio.remove_holding("INVALID")

    # Test invalid price updates
    with pytest.raises(ValueError):
        portfolio.update_prices({"AAPL": Decimal("-100.0")})

    # Test invalid target weights
    portfolio_manager = PortfolioManager(portfolio)
    with pytest.raises(ValueError):
        portfolio_manager.calculate_rebalancing_trades({"AAPL": 0.5, "MSFT": 0.6})

def test_holding_creation(sample_holding):
    """Test holding creation and properties."""
    assert sample_holding.symbol == "AAPL"
    assert sample_holding.quantity == 10
    assert sample_holding.current_price == Decimal("150.0")
    assert sample_holding.name == "Apple Inc."
    assert sample_holding.sector == "Technology"
    assert sample_holding.weight == 0.3
    
    # Test value calculation
    assert sample_holding.total_value == Decimal("1500.0")

def test_portfolio_creation(sample_portfolio):
    """Test portfolio creation and basic properties."""
    assert len(sample_portfolio.holdings) == 4
    assert "AAPL" in sample_portfolio.holdings
    assert "MSFT" in sample_portfolio.holdings
    assert "VTI" in sample_portfolio.holdings
    assert "BND" in sample_portfolio.holdings
    
    # Test total value calculation
    expected_value = Decimal("1500.0") + Decimal("15000.0") + Decimal("44000.0") + Decimal("8500.0")  # AAPL + MSFT + VTI + BND
    assert sample_portfolio.metrics['total_value'] == expected_value

def test_portfolio_add_holding(sample_portfolio):
    """Test adding holdings to portfolio."""
    new_holding = Holding(
        symbol="NVDA",
        name="NVIDIA Corp.",
        quantity=5,
        current_price=Decimal("500.0"),
        sector="Technology"
    )
    
    initial_count = len(sample_portfolio.holdings)
    sample_portfolio.add_holding(new_holding)
    
    assert len(sample_portfolio.holdings) == initial_count + 1
    assert "NVDA" in sample_portfolio.holdings
    assert sample_portfolio.holdings["NVDA"].total_value == Decimal("2500.0")

def test_portfolio_remove_holding(sample_portfolio):
    """Test removing holdings from portfolio."""
    initial_count = len(sample_portfolio.holdings)
    sample_portfolio.remove_holding("AAPL")
    
    assert len(sample_portfolio.holdings) == initial_count - 1
    assert "AAPL" not in sample_portfolio.holdings
    assert "MSFT" in sample_portfolio.holdings

def test_portfolio_update_prices(sample_portfolio):
    """Test updating holding prices."""
    new_prices = {
        "AAPL": Decimal("160.0"),
        "MSFT": Decimal("310.0")
    }
    
    initial_value = sample_portfolio.metrics['total_value']
    sample_portfolio.update_prices(new_prices)
    
    assert sample_portfolio.holdings["AAPL"].current_price == Decimal("160.0")
    assert sample_portfolio.holdings["MSFT"].current_price == Decimal("310.0")
    assert sample_portfolio.metrics['total_value'] > initial_value

def test_portfolio_weights(sample_portfolio):
    """Test portfolio weight calculations."""
    total_value = sample_portfolio.metrics['total_value']
    
    aapl_weight = sample_portfolio.holdings["AAPL"].total_value / total_value
    msft_weight = sample_portfolio.holdings["MSFT"].total_value / total_value
    
    assert abs(aapl_weight + msft_weight - Decimal('1.0')) < Decimal('0.0001')

def test_portfolio_manager_rebalancing(portfolio_manager):
    """Test portfolio rebalancing calculations."""
    holding1 = Holding(
        symbol="AAPL",
        name="Apple Inc.",
        quantity=100,
        current_price=Decimal("150.0"),
        sector="Technology",
        weight=0.6
    )
    holding2 = Holding(
        symbol="MSFT",
        name="Microsoft Corp.",
        quantity=50,
        current_price=Decimal("300.0"),
        sector="Technology",
        weight=0.4
    )
    portfolio_manager.add_holding(holding1)
    portfolio_manager.add_holding(holding2)

    target_weights = {
        "AAPL": 0.5,
        "MSFT": 0.5
    }
    trades = portfolio_manager.calculate_rebalancing_trades(target_weights)
    assert len(trades) > 0
    assert all(isinstance(trade, dict) for trade in trades)
    assert all(key in trade for trade in trades for key in ['symbol', 'quantity', 'price', 'value', 'old_weight', 'new_weight'])

def test_portfolio_manager_trade_execution(portfolio_manager):
    """Test trade execution in portfolio manager."""
    holding = Holding(
        symbol="AAPL",
        name="Apple Inc.",
        quantity=10,
        current_price=Decimal("150.0"),
        sector="Technology",
        weight=0.3
    )
    portfolio_manager.add_holding(holding)
    
    trades = [
        {
            "symbol": "AAPL",
            "quantity": 5,
            "price": 150.0,
            "value": 750.0,
            "old_weight": 0.3,
            "new_weight": 0.35
        }
    ]
    
    success = portfolio_manager.execute_rebalancing_trades(trades)
    assert success
    assert portfolio_manager.portfolio.holdings["AAPL"].quantity == 15

def test_error_handling():
    """Test error handling in portfolio management."""
    portfolio = Portfolio()
    
    # Test adding invalid holding
    with pytest.raises(ValueError):
        portfolio.add_holding(None)
    
    # Test removing non-existent holding
    with pytest.raises(KeyError):
        portfolio.remove_holding("INVALID")
    
    # Test invalid price updates
    with pytest.raises(ValueError):
        portfolio.update_prices({"AAPL": Decimal("-100.0")}) 