import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from dcm.dcm_engine import DCMEngine
from dcm.portfolio import Portfolio, PortfolioManager
from dcm.holdings import Holding
from dcm.market_data import MarketData, MarketInsights

class TestMarketDataIntegration:
    @pytest.fixture
    def test_portfolio(self):
        """Create a test portfolio."""
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
            )
        }
        return Portfolio(holdings=holdings)

    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data."""
        return {
            "AAPL": MarketInsights(
                symbol="AAPL",
                current_price=Decimal("155.0"),
                volume=1000000,
                market_cap=2500000000000,
                beta=1.2,
                volatility=0.25,
                market_sentiment="Bullish",
                news_sentiment="Bullish",
                analyst_recommendations=[
                    {"recommendation": "Strong Buy", "weight": 1.0}
                ],
                web_research=[
                    {"title": "Analysis", "content": "Very positive outlook"}
                ]
            ),
            "MSFT": MarketInsights(
                symbol="MSFT",
                current_price=Decimal("310.0"),
                volume=800000,
                market_cap=2200000000000,
                beta=1.1,
                volatility=0.22,
                market_sentiment="Neutral",
                news_sentiment="Bullish",
                analyst_recommendations=[
                    {"recommendation": "Buy", "weight": 0.8}
                ],
                web_research=[
                    {"title": "Analysis", "content": "Stable growth expected"}
                ]
            )
        }

    @pytest.fixture
    def dcm_engine(self):
        """Create DCM engine instance."""
        return DCMEngine()

    @patch('dcm.dcm_engine.MarketDataManager')
    def test_risk_metrics_calculation(self, mock_market_data_manager):
        """Test calculation of risk metrics using market data."""
        # Set up mock
        mock_market_data_manager.return_value.get_portfolio_market_data.return_value = self.mock_market_data

        # Calculate risk metrics
        risk_metrics = self.dcm_engine._calculate_risk_metrics(
            self.test_portfolio,
            self.mock_market_data
        )

        # Verify results
        assert isinstance(risk_metrics, float)
        assert 0.0 <= risk_metrics <= 1.0

    @patch('dcm.dcm_engine.MarketDataManager')
    def test_performance_metrics_calculation(self, mock_market_data_manager):
        """Test calculation of performance metrics using market data."""
        # Set up mock
        mock_market_data_manager.return_value.get_portfolio_market_data.return_value = self.mock_market_data

        # Calculate performance metrics
        performance_metrics = self.dcm_engine._calculate_performance_metrics(
            self.test_portfolio,
            self.mock_market_data
        )

        # Verify results
        assert isinstance(performance_metrics, float)
        assert 0.0 <= performance_metrics <= 1.0

    @patch('dcm.dcm_engine.MarketDataManager')
    def test_sentiment_score_calculation(self, mock_market_data_manager):
        """Test calculation of sentiment score using market data."""
        # Set up mock
        mock_market_data_manager.return_value.get_portfolio_market_data.return_value = self.mock_market_data

        # Calculate sentiment score
        sentiment_score = self.dcm_engine._calculate_sentiment_score(self.mock_market_data)

        # Verify results
        assert isinstance(sentiment_score, float)
        assert 0.0 <= sentiment_score <= 1.0

    @patch('dcm.dcm_engine.MarketDataManager')
    def test_risk_parity_weights_calculation(self, mock_market_data_manager):
        """Test calculation of risk parity weights using market data."""
        # Set up mock
        mock_market_data_manager.return_value.get_portfolio_market_data.return_value = self.mock_market_data

        # Calculate risk parity weights
        weights = self.dcm_engine._calculate_risk_parity_weights(
            self.test_portfolio,
            self.mock_market_data
        )

        # Verify results
        assert isinstance(weights, dict)
        assert all(isinstance(w, float) for w in weights.values())
        assert abs(sum(weights.values()) - 1.0) < 0.0001

    @patch('dcm.dcm_engine.MarketDataManager')
    def test_market_data_error_handling(self, mock_market_data_manager):
        """Test error handling for market data issues."""
        # Test missing market data
        mock_market_data_manager.return_value.get_portfolio_market_data.return_value = {}
        risk_metrics = self.dcm_engine._calculate_risk_metrics(
            self.test_portfolio,
            {}
        )
        assert risk_metrics == 0.5  # Default value for missing data

        # Test invalid market data
        mock_market_data_manager.return_value.get_portfolio_market_data.return_value = {
            "INVALID": None
        }
        risk_metrics = self.dcm_engine._calculate_risk_metrics(
            self.test_portfolio,
            {"INVALID": None}
        )
        assert risk_metrics == 0.5  # Default value for invalid data 