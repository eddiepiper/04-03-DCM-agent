import unittest
from pathlib import Path
import json
import sys
sys.path.append(str(Path(__file__).parent.parent))
from dcm.dcm_engine import DCMEngine, Strategy
from dcm.portfolio import Portfolio, Holding
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

class TestDCMEngine(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.engine = DCMEngine()
        self.portfolio_manager = MagicMock()
        self.portfolio_manager.portfolio = Portfolio()
        self.portfolio_manager.portfolio.add_holding(
            Holding(
                symbol="AAPL",
                name="Apple Inc.",
                quantity=10,
                current_price=Decimal("150.0"),
                sector="Technology"
            )
        )
        self.portfolio_manager.portfolio.add_holding(
            Holding(
                symbol="MSFT",
                name="Microsoft Corp.",
                quantity=15,
                current_price=Decimal("300.0"),
                sector="Technology"
            )
        )

    def test_initialization(self):
        """Test DCM engine initialization."""
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.engine.portfolio_manager)
        self.assertIsNotNone(self.engine.capabilities)
        self.assertIsNotNone(self.engine.strategies)

    def test_strategy_loading(self):
        """Test strategy loading from capabilities file."""
        expected_strategies = {
            "equal_weight",
            "risk_parity",
            "volatility_weighted",
            "dividend_focus"
        }
        self.assertEqual(set(self.engine.strategies.keys()), expected_strategies)

    def test_strategy_evaluation(self):
        """Test strategy evaluation functionality."""
        # Test equal weight strategy
        score, recommendations = self.engine.evaluate_strategy("equal_weight")
        
        # Verify score is between 0 and 1
        assert 0 <= score <= 1
        
        # Verify recommendations format
        assert isinstance(recommendations, dict)
        assert all(isinstance(v, float) for v in recommendations.values())
        assert all(-1 <= v <= 1 for v in recommendations.values())

    def test_weight_calculations(self):
        """Test different weight calculation methods."""
        portfolio = self.portfolio_manager.portfolio
        
        # Test equal weights
        equal_weights = self.engine._calculate_equal_weights(portfolio)
        assert len(equal_weights) == len(portfolio.holdings)
        assert abs(sum(equal_weights.values()) - 1.0) < 1e-6
        assert all(0 <= w <= 1 for w in equal_weights.values())

    def test_strategy_scoring(self):
        """Test strategy scoring calculation."""
        portfolio = self.portfolio_manager.portfolio
        current_weights = {h.symbol: h.weight for h in portfolio.holdings}
        target_weights = self.engine._calculate_equal_weights(portfolio)
        
        score = self.engine._calculate_strategy_score(
            current_weights,
            target_weights,
            portfolio.risk_metrics,
            portfolio.performance_metrics,
            {},  # market_data
            {}   # market_insights
        )
        
        # Verify score is between 0 and 1
        assert 0 <= score <= 1

    def test_recommendation_generation(self):
        """Test trading recommendation generation."""
        portfolio = self.portfolio_manager.portfolio
        current_weights = {h.symbol: h.weight for h in portfolio.holdings}
        target_weights = self.engine._calculate_equal_weights(portfolio)
        
        recommendations = self.engine._generate_recommendations(
            portfolio.holdings,
            0.75  # High strategy score
        )
        
        # Verify recommendations format
        assert isinstance(recommendations, dict)
        assert all(isinstance(v, float) for v in recommendations.values())
        assert all(-1 <= v <= 1 for v in recommendations.values())

    def test_best_strategy_selection(self):
        """Test best strategy selection."""
        best_strategy, score, recommendations = self.engine.get_best_strategy()
        
        # Verify return values
        assert isinstance(best_strategy, str)
        assert 0 <= score <= 1
        assert isinstance(recommendations, dict)
        assert all(isinstance(v, float) for v in recommendations.values())
        assert all(-1 <= v <= 1 for v in recommendations.values())

    def test_strategy_performance_update(self):
        """Test strategy performance update functionality."""
        strategy_name = "equal_weight"
        initial_score = self.engine.strategies[strategy_name].confidence_score
        initial_times_used = self.engine.strategies[strategy_name].times_used

        self.engine.update_strategy_performance(strategy_name, 0.85)
        
        self.assertEqual(
            self.engine.strategies[strategy_name].times_used,
            initial_times_used + 1
        )
        self.assertNotEqual(
            self.engine.strategies[strategy_name].confidence_score,
            initial_score
        )

    def test_data_layer_integration(self):
        """Test integration with portfolio data layer."""
        # Get portfolio data
        portfolio = self.portfolio_manager.portfolio
        
        # Verify portfolio data is accessible
        self.assertIsNotNone(portfolio)
        self.assertIsNotNone(portfolio.holdings)
        self.assertGreater(len(portfolio.holdings), 0)
        
        # Test portfolio metrics
        self.assertIsNotNone(portfolio.risk_metrics)
        self.assertIsNotNone(portfolio.performance_metrics)
        self.assertIsNotNone(portfolio.constraints)

    def test_capabilities_persistence(self):
        """Test capabilities data persistence."""
        # Modify a strategy
        strategy_name = "equal_weight"
        initial_score = self.engine.strategies[strategy_name].confidence_score
        
        # Update performance
        self.engine.update_strategy_performance(strategy_name, 0.90)
        
        # Create new engine instance
        new_engine = DCMEngine()
        
        # Verify changes persisted
        self.assertNotEqual(
            new_engine.strategies[strategy_name].confidence_score,
            initial_score
        )

@pytest.fixture
def dcm_engine():
    return DCMEngine()

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
def market_insights():
    return {
        "AAPL": {
            "web_research": "Strong performance in services and wearables.",
            "market_sentiment": 0.8,
            "news_sentiment": 0.7
        },
        "MSFT": {
            "web_research": "Cloud business growth remains robust.",
            "market_sentiment": 0.75,
            "news_sentiment": 0.8
        }
    }

def test_dcm_engine_initialization(dcm_engine):
    """Test DCM engine initialization."""
    assert dcm_engine is not None
    assert hasattr(dcm_engine, 'strategies')
    assert len(dcm_engine.strategies) > 0

@pytest.mark.asyncio
async def test_strategy_evaluation(dcm_engine, sample_portfolio, market_insights):
    """Test strategy evaluation with market insights."""
    recommendations = await dcm_engine.evaluate_strategy(sample_portfolio, market_insights)
    
    assert isinstance(recommendations, list)
    assert len(recommendations) == 2  # One for each holding
    
    for rec in recommendations:
        assert "symbol" in rec
        assert "recommendation" in rec
        assert "weight_adjustment" in rec
        assert "current_weight" in rec
        assert "target_weight" in rec
        assert 0 <= rec["target_weight"] <= 1

def test_research_score_calculation(dcm_engine):
    """Test research score calculation."""
    insights = {
        "web_research": "Very positive outlook for the company",
        "market_sentiment": 0.8,
        "news_sentiment": 0.7
    }
    
    score = dcm_engine._calculate_research_score(insights)
    assert 0 <= score <= 1
    
    # Test with negative sentiment
    insights["web_research"] = "Poor performance and declining metrics"
    score_negative = dcm_engine._calculate_research_score(insights)
    assert score_negative < score

def test_analyst_score_calculation(dcm_engine):
    """Test analyst score calculation."""
    score = dcm_engine._calculate_analyst_score("AAPL")
    assert 0 <= score <= 1

def test_strategy_performance_update(dcm_engine):
    """Test strategy performance update."""
    strategy_name = "equal_weight"
    initial_score = dcm_engine.strategies[strategy_name].confidence_score
    initial_uses = dcm_engine.strategies[strategy_name].times_used
    
    dcm_engine.update_strategy_performance(strategy_name, 0.9)
    
    updated_strategy = dcm_engine.strategies[strategy_name]
    assert updated_strategy.times_used == initial_uses + 1
    assert updated_strategy.confidence_score != initial_score

def test_best_strategy_selection(dcm_engine):
    """Test best strategy selection."""
    # Update performance for different strategies
    dcm_engine.update_strategy_performance("equal_weight", 0.8)
    dcm_engine.update_strategy_performance("risk_parity", 0.9)
    dcm_engine.update_strategy_performance("volatility_weighted", 0.7)
    
    best_strategy, confidence, recommendations = dcm_engine.get_best_strategy()
    
    assert isinstance(best_strategy, str)
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1
    assert isinstance(recommendations, dict)

def test_recommendation_generation(dcm_engine, sample_portfolio):
    """Test recommendation generation with different strategy scores."""
    # Test with positive market sentiment
    recommendations_positive = dcm_engine._generate_recommendations(sample_portfolio, 0.8)
    assert all(rec["weight_adjustment"] > 0 for rec in recommendations_positive)
    
    # Test with negative market sentiment
    recommendations_negative = dcm_engine._generate_recommendations(sample_portfolio, 0.2)
    assert all(rec["weight_adjustment"] < 0 for rec in recommendations_negative)
    
    # Test with neutral market sentiment
    recommendations_neutral = dcm_engine._generate_recommendations(sample_portfolio, 0.5)
    assert all(abs(rec["weight_adjustment"]) < 0.1 for rec in recommendations_neutral)

def test_error_handling(dcm_engine):
    """Test error handling in DCM engine."""
    # Test with empty portfolio
    empty_portfolio = Portfolio()
    recommendations = dcm_engine._generate_recommendations(empty_portfolio, 0.5)
    assert len(recommendations) == 0
    
    # Test with invalid strategy name
    with pytest.raises(KeyError):
        dcm_engine.update_strategy_performance("invalid_strategy", 0.5)
    
    # Test with invalid market insights
    invalid_insights = {"AAPL": None}
    score = dcm_engine._calculate_research_score(invalid_insights)
    assert score == 0.5  # Should return neutral score on error

if __name__ == '__main__':
    unittest.main() 