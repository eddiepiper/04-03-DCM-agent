import unittest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from data.portfolio_data import PortfolioDataManager, Portfolio, Holding
from agents.rebalance_strategy_agent import RebalanceStrategyAgent, RebalanceRecommendation

class TestRebalanceStrategyAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create a test portfolio with some concentration issues
        self.test_portfolio = Portfolio(
            portfolio_id="TEST001",
            currency="USD",
            last_updated="2024-03-23T12:00:00",
            holdings=[
                Holding(
                    symbol="VTI",
                    name="Vanguard Total Stock Market ETF",
                    current_price=217.80,
                    quantity=11,
                    total_value=2500.0,
                    weight=0.25,
                    asset_type="ETF",
                    sector="Broad Market"
                ),
                Holding(
                    symbol="BND",
                    name="Vanguard Total Bond Market ETF",
                    current_price=72.32,
                    quantity=20,
                    total_value=1500.0,
                    weight=0.15,
                    asset_type="Fixed Income",
                    sector="Government"
                ),
                Holding(
                    symbol="AGG",
                    name="iShares Core U.S. Aggregate Bond ETF",
                    current_price=98.70,
                    quantity=10,
                    total_value=1000.0,
                    weight=0.10,
                    asset_type="Fixed Income",
                    sector="Corporate"
                ),
                Holding(
                    symbol="AAPL",
                    name="Apple Inc.",
                    current_price=217.80,
                    quantity=9,
                    total_value=2000.0,
                    weight=0.20,
                    asset_type="Stock",
                    sector="Technology"
                ),
                Holding(
                    symbol="MSFT",
                    name="Microsoft Corporation",
                    current_price=217.80,
                    quantity=14,
                    total_value=2000.0,
                    weight=0.20,
                    asset_type="Stock",
                    sector="Technology"
                )
            ],
            total_value=10000.0,
            asset_allocation={
                "Fixed Income": 0.25,
                "Stocks": 0.40,
                "ETF": 0.25
            },
            sector_allocation={
                "Government": 0.15,
                "Corporate": 0.10,
                "Technology": 0.40,
                "Broad Market": 0.25
            },
            risk_metrics={
                "beta": 1.1,
                "volatility": 0.15,
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.25
            },
            performance_metrics={
                "daily_return": 0.002,
                "weekly_return": 0.015,
                "monthly_return": 0.045,
                "year_to_date_return": 0.085,
                "annualized_return": 0.12
            },
            constraints={
                "min_cash_balance": 0.05,
                "max_single_position": 0.25,
                "max_sector_exposure": 0.40,
                "min_bond_allocation": 0.15,
                "max_bond_allocation": 0.30
            }
        )
        
        # Create a test portfolio manager
        self.portfolio_manager = PortfolioDataManager()
        self.portfolio_manager.portfolio = self.test_portfolio
        self.rebalance_agent = RebalanceStrategyAgent(self.portfolio_manager)

    def test_generate_rebalance_recommendations(self):
        """Test generation of rebalancing recommendations."""
        recommendations = self.rebalance_agent.generate_rebalance_recommendations()
        
        # Verify result type
        self.assertIsInstance(recommendations, list)
        
        # Verify recommendation structure
        if recommendations:
            rec = recommendations[0]
            self.assertIsInstance(rec, RebalanceRecommendation)
            self.assertIsInstance(rec.symbol, str)
            self.assertIsInstance(rec.current_weight, float)
            self.assertIsInstance(rec.target_weight, float)
            self.assertIsInstance(rec.weight_change, float)
            self.assertIsInstance(rec.reason, str)
            self.assertIsInstance(rec.priority, int)
            
            # Verify priority range
            self.assertGreaterEqual(rec.priority, 1)
            self.assertLessEqual(rec.priority, 3)
            
            # Verify weight change calculation
            self.assertEqual(rec.weight_change, rec.target_weight - rec.current_weight)

    def test_validate_recommendations(self):
        """Test validation of rebalancing recommendations."""
        # Create some test recommendations
        recommendations = [
            RebalanceRecommendation(
                symbol="AAPL",
                current_weight=0.20,
                target_weight=0.15,
                weight_change=-0.05,
                reason="Test",
                priority=1
            ),
            RebalanceRecommendation(
                symbol="MSFT",
                current_weight=0.20,
                target_weight=0.15,
                weight_change=-0.05,
                reason="Test",
                priority=1
            )
        ]
        
        # Validate recommendations
        is_valid = self.rebalance_agent.validate_recommendations(recommendations)
        self.assertIsInstance(is_valid, bool)

    def test_recommendation_priorities(self):
        """Test that recommendations are properly prioritized."""
        recommendations = self.rebalance_agent.generate_rebalance_recommendations()
        
        if recommendations:
            # Verify recommendations are sorted by priority
            priorities = [rec.priority for rec in recommendations]
            self.assertEqual(priorities, sorted(priorities))

if __name__ == '__main__':
    unittest.main() 