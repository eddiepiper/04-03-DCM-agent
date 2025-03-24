import unittest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from data.portfolio_data import PortfolioDataManager, Portfolio, Holding
from agents.portfolio_analysis_agent import PortfolioAnalysisAgent, PortfolioAnalysis

class TestPortfolioAnalysisAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create a test portfolio
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
        self.analysis_agent = PortfolioAnalysisAgent(self.portfolio_manager)

    def test_analyze_portfolio(self):
        """Test portfolio analysis functionality."""
        analysis = self.analysis_agent.analyze_portfolio()
        
        # Verify result type
        self.assertIsInstance(analysis, PortfolioAnalysis)
        
        # Verify risk metrics
        self.assertIn('beta', analysis.risk_metrics)
        self.assertIn('volatility', analysis.risk_metrics)
        self.assertIn('sharpe_ratio', analysis.risk_metrics)
        self.assertIn('max_drawdown', analysis.risk_metrics)
        
        # Verify performance metrics
        self.assertIn('daily_return', analysis.performance_metrics)
        self.assertIn('weekly_return', analysis.performance_metrics)
        self.assertIn('monthly_return', analysis.performance_metrics)
        self.assertIn('year_to_date_return', analysis.performance_metrics)
        self.assertIn('annualized_return', analysis.performance_metrics)
        
        # Verify sector exposure
        self.assertEqual(analysis.sector_exposure['Technology'], 0.40)
        self.assertEqual(analysis.sector_exposure['Broad Market'], 0.25)
        self.assertEqual(analysis.sector_exposure['Government'], 0.15)
        self.assertEqual(analysis.sector_exposure['Corporate'], 0.10)
        
        # Verify asset allocation
        self.assertEqual(analysis.asset_allocation['Fixed Income'], 0.25)
        self.assertEqual(analysis.asset_allocation['Stocks'], 0.40)
        self.assertEqual(analysis.asset_allocation['ETF'], 0.25)
        
        # Verify diversification score
        self.assertGreaterEqual(analysis.diversification_score, 0)
        self.assertLessEqual(analysis.diversification_score, 1)

    def test_identify_concentration_risks(self):
        """Test concentration risk identification."""
        risks = self.analysis_agent._identify_concentration_risks(self.test_portfolio)
        
        # Verify risk list type
        self.assertIsInstance(risks, list)
        
        # Verify no concentration risks in test portfolio
        # (since all positions are within limits)
        self.assertEqual(len(risks), 0)

    def test_generate_insights(self):
        """Test insight generation."""
        insights = self.analysis_agent.generate_insights()
        
        # Verify insights list type
        self.assertIsInstance(insights, list)
        
        # Verify insights content
        # (test portfolio should not trigger any insights)
        self.assertEqual(len(insights), 0)

if __name__ == '__main__':
    unittest.main() 