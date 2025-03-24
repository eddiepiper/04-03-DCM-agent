import pytest
import asyncio

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Remove the custom event_loop fixture as it's deprecated
# The default event loop will be used with function scope

@pytest.fixture
def mock_portfolio():
    """Create a mock portfolio for testing."""
    from dcm.holdings import Holding
    from dcm.portfolio import Portfolio
    from decimal import Decimal

    holdings = {
        "AAPL": Holding(
            symbol="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10"),
            current_price=Decimal("150.0"),
            sector="Technology"
        ),
        "MSFT": Holding(
            symbol="MSFT",
            name="Microsoft Corp.",
            quantity=Decimal("15"),
            current_price=Decimal("300.0"),
            sector="Technology"
        )
    }
    return Portfolio(holdings=holdings)

@pytest.fixture
def mock_market_data():
    """Create mock market data for testing."""
    from dcm.market_data import MarketData
    return {
        "AAPL": MarketData(
            symbol="AAPL",
            current_price=150.0,
            beta=1.2,
            volatility=0.25,
            sentiment="Bullish",
            news_sentiment="Neutral"
        ),
        "MSFT": MarketData(
            symbol="MSFT",
            current_price=300.0,
            beta=1.1,
            volatility=0.2,
            sentiment="Neutral",
            news_sentiment="Bullish"
        )
    }

@pytest.fixture
def mock_market_insights():
    """Create mock market insights for testing."""
    return {
        "AAPL": {
            "analyst_recommendations": [
                {"rating": "Buy", "target_price": 180.0},
                {"rating": "Hold", "target_price": 160.0}
            ],
            "market_sentiment": "Bullish",
            "news_sentiment": "Neutral",
            "web_research": [
                {"content": "Positive outlook for iPhone sales"},
                {"content": "Strong performance in services"}
            ]
        },
        "MSFT": {
            "analyst_recommendations": [
                {"rating": "Strong Buy", "target_price": 350.0},
                {"rating": "Buy", "target_price": 320.0}
            ],
            "market_sentiment": "Neutral",
            "news_sentiment": "Bullish",
            "web_research": [
                {"content": "Cloud business growing rapidly"},
                {"content": "AI initiatives showing promise"}
            ]
        }
    } 