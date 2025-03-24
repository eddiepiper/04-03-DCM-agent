import unittest
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from data.portfolio_data import PortfolioDataManager
from agents.analysis_agent import PortfolioAnalysisAgent

class TestPortfolioAnalysisAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.portfolio_manager = PortfolioDataManager()
        self.analysis_agent = PortfolioAnalysisAgent(self.portfolio_manager)

    def test_analyze_portfolio(self):
        """Test portfolio analysis functionality."""
        analysis = self.analysis_agent.analyze_portfolio()
        
        # Verify analysis object has all required fields
        self.assertIsNotNone(analysis.asset_allocation)
        self.assertIsNotNone(analysis.sector_allocation)
        self.assertIsNotNone(analysis.risk_metrics)
        self.assertIsNotNone(analysis.performance_metrics)
        self.assertIsNotNone(analysis.total_value)
        self.assertIsNotNone(analysis.holdings_count)
        
        # Verify data types
        self.assertIsInstance(analysis.asset_allocation, dict)
        self.assertIsInstance(analysis.sector_allocation, dict)
        self.assertIsInstance(analysis.risk_metrics, dict)
        self.assertIsInstance(analysis.performance_metrics, dict)
        self.assertIsInstance(analysis.total_value, float)
        self.assertIsInstance(analysis.holdings_count, int)
        
        # Verify values are reasonable
        self.assertGreater(analysis.total_value, 0)
        self.assertGreater(analysis.holdings_count, 0)
        self.assertAlmostEqual(sum(analysis.asset_allocation.values()), 1.0, places=6)
        self.assertAlmostEqual(sum(analysis.sector_allocation.values()), 1.0, places=6)

    def test_get_holding_analysis(self):
        """Test holding analysis functionality."""
        # Test with existing holding
        aapl_analysis = self.analysis_agent.get_holding_analysis("AAPL")
        self.assertIsNotNone(aapl_analysis)
        
        # Verify holding analysis has all required fields
        required_fields = ['symbol', 'name', 'asset_type', 'sector', 'quantity', 
                         'current_price', 'total_value', 'weight']
        for field in required_fields:
            self.assertIn(field, aapl_analysis)
        
        # Verify data types
        self.assertIsInstance(aapl_analysis['symbol'], str)
        self.assertIsInstance(aapl_analysis['name'], str)
        self.assertIsInstance(aapl_analysis['asset_type'], str)
        self.assertIsInstance(aapl_analysis['sector'], str)
        self.assertIsInstance(aapl_analysis['quantity'], int)
        self.assertIsInstance(aapl_analysis['current_price'], float)
        self.assertIsInstance(aapl_analysis['total_value'], float)
        self.assertIsInstance(aapl_analysis['weight'], float)
        
        # Verify values are reasonable
        self.assertEqual(aapl_analysis['symbol'], "AAPL")
        self.assertGreater(aapl_analysis['quantity'], 0)
        self.assertGreater(aapl_analysis['current_price'], 0)
        self.assertGreater(aapl_analysis['total_value'], 0)
        self.assertGreaterEqual(aapl_analysis['weight'], 0)
        self.assertLessEqual(aapl_analysis['weight'], 1)
        
        # Test with non-existent holding
        invalid_analysis = self.analysis_agent.get_holding_analysis("INVALID")
        self.assertIsNone(invalid_analysis)

    def test_get_portfolio_summary(self):
        """Test portfolio summary functionality."""
        summary = self.analysis_agent.get_portfolio_summary()
        
        # Verify summary has all required fields
        required_fields = ['portfolio_id', 'total_value', 'currency', 'last_updated',
                         'holdings_count', 'asset_allocation', 'sector_allocation',
                         'risk_metrics', 'performance_metrics']
        for field in required_fields:
            self.assertIn(field, summary)
        
        # Verify data types
        self.assertIsInstance(summary['portfolio_id'], str)
        self.assertIsInstance(summary['total_value'], float)
        self.assertIsInstance(summary['currency'], str)
        self.assertIsInstance(summary['last_updated'], str)
        self.assertIsInstance(summary['holdings_count'], int)
        self.assertIsInstance(summary['asset_allocation'], dict)
        self.assertIsInstance(summary['sector_allocation'], dict)
        self.assertIsInstance(summary['risk_metrics'], dict)
        self.assertIsInstance(summary['performance_metrics'], dict)
        
        # Verify values are reasonable
        self.assertGreater(summary['total_value'], 0)
        self.assertGreater(summary['holdings_count'], 0)
        self.assertAlmostEqual(sum(summary['asset_allocation'].values()), 1.0, places=6)
        self.assertAlmostEqual(sum(summary['sector_allocation'].values()), 1.0, places=6)

if __name__ == '__main__':
    unittest.main() 