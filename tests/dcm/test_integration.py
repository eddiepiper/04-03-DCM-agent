import unittest
from pathlib import Path
import json
import sys
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent))
from dcm.dcm_engine import DCMEngine, Strategy
from data.portfolio_data import PortfolioDataManager

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.dcm_engine = DCMEngine()
        self.portfolio_manager = self.dcm_engine.portfolio_manager

    def test_full_rebalancing_workflow(self):
        """Test complete portfolio rebalancing workflow."""
        print("\n=== Testing Full Rebalancing Workflow ===")
        
        # 1. Get initial portfolio state
        print("\nInitial Portfolio State:")
        portfolio = self.portfolio_manager.portfolio
        initial_holdings = {h.symbol: h.weight for h in portfolio.holdings}
        print(f"Initial Holdings Weights: {initial_holdings}")
        
        # 2. Get best strategy recommendation
        strategy, score, recommendations = self.dcm_engine.get_best_strategy()
        print(f"\nBest Strategy: {strategy}")
        print(f"Strategy Score: {score:.4f}")
        print("Recommended Changes:")
        for symbol, weight_change in recommendations.items():
            print(f"  {symbol}: {weight_change:+.4f}")
        
        # Verify strategy selection
        self.assertIsNotNone(strategy)
        self.assertGreater(score, 0)
        self.assertIsInstance(recommendations, dict)

        # 3. Test strategy-specific calculations
        print("\nTesting Strategy-Specific Calculations:")
        for strategy_name in ["equal_weight", "risk_parity", "volatility_weighted", "dividend_focus"]:
            score, recs = self.dcm_engine.evaluate_strategy(strategy_name)
            print(f"\n{strategy_name}:")
            print(f"  Score: {score:.4f}")
            print(f"  Number of Recommendations: {len(recs)}")
            
            # Verify strategy evaluation
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)
            self.assertIsInstance(recs, dict)

    def test_portfolio_updates_and_persistence(self):
        """Test portfolio updates and data persistence."""
        print("\n=== Testing Portfolio Updates and Persistence ===")
        
        # 1. Get initial state
        initial_total_value = self.portfolio_manager.get_total_value()
        print(f"\nInitial Portfolio Value: ${initial_total_value:,.2f}")
        
        # 2. Update a holding
        symbol = "AAPL"
        original_holding = self.portfolio_manager.get_holding(symbol)
        original_price = original_holding.current_price
        original_total_value = original_holding.total_value
        original_weight = original_holding.weight
        new_price = original_price * 1.1  # 10% increase
        
        print(f"\nUpdating {symbol} price from ${original_price:.2f} to ${new_price:.2f}")
        success = self.portfolio_manager.update_holding(symbol, current_price=new_price)
        self.assertTrue(success)
        
        # 3. Verify updates
        updated_holding = self.portfolio_manager.get_holding(symbol)
        print(f"New {symbol} Total Value: ${updated_holding.total_value:.2f}")
        print(f"New {symbol} Weight: {updated_holding.weight:.4f}")
        
        # Verify price update
        self.assertEqual(updated_holding.current_price, new_price)
        
        # Verify total value update (should be 10% higher)
        expected_new_total = original_total_value * 1.1
        self.assertAlmostEqual(updated_holding.total_value, expected_new_total, places=2)
        
        # Create a deep copy of the original holding for comparison
        original_holding_copy = {
            'price': original_price,
            'total_value': original_total_value,
            'weight': original_weight
        }
        
        # Verify all values have changed
        self.assertNotEqual(original_holding_copy['price'], updated_holding.current_price)
        self.assertNotEqual(original_holding_copy['total_value'], updated_holding.total_value)
        self.assertNotEqual(original_holding_copy['weight'], updated_holding.weight)
        
        # Verify portfolio total value has increased
        new_total_value = self.portfolio_manager.get_total_value()
        self.assertGreater(new_total_value, initial_total_value)

    def test_strategy_evolution(self):
        """Test strategy evolution and performance tracking."""
        print("\n=== Testing Strategy Evolution ===")
        
        strategy_name = "equal_weight"
        initial_state = {
            "confidence": self.dcm_engine.strategies[strategy_name].confidence_score,
            "times_used": self.dcm_engine.strategies[strategy_name].times_used,
            "performance": self.dcm_engine.strategies[strategy_name].last_performance
        }
        
        print(f"\nInitial {strategy_name} state:")
        print(f"  Confidence Score: {initial_state['confidence']:.4f}")
        print(f"  Times Used: {initial_state['times_used']}")
        print(f"  Last Performance: {initial_state['performance']:.4f}")
        
        # Simulate strategy usage and performance updates
        test_performances = [0.85, 0.92, 0.78]
        print("\nSimulating strategy usage:")
        
        for i, perf in enumerate(test_performances, 1):
            print(f"\nUpdate {i} - Performance: {perf:.4f}")
            self.dcm_engine.update_strategy_performance(strategy_name, perf)
            
            strategy = self.dcm_engine.strategies[strategy_name]
            print(f"  New Confidence Score: {strategy.confidence_score:.4f}")
            print(f"  Times Used: {strategy.times_used}")
            print(f"  Last Performance: {strategy.last_performance:.4f}")
            
            # Verify updates
            self.assertEqual(strategy.times_used, initial_state["times_used"] + i)
            self.assertEqual(strategy.last_performance, perf)

    def test_constraint_handling(self):
        """Test portfolio constraint handling."""
        print("\n=== Testing Constraint Handling ===")
        
        constraints = self.portfolio_manager.get_constraints()
        print("\nPortfolio Constraints:")
        for constraint, value in constraints.items():
            print(f"  {constraint}: {value:.4f}")
        
        # Test constraint validation in recommendations
        strategy = "equal_weight"
        score, recommendations = self.dcm_engine.evaluate_strategy(strategy)
        
        print(f"\nTesting {strategy} recommendations against constraints:")
        max_single_position = constraints.get("max_single_position", 1.0)
        
        for symbol, weight_change in recommendations.items():
            current_weight = self.portfolio_manager.get_holding(symbol).weight
            new_weight = current_weight + weight_change
            print(f"  {symbol}: Current {current_weight:.4f} -> New {new_weight:.4f}")
            
            # Verify position size constraint
            self.assertLessEqual(new_weight, max_single_position)

    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n=== Testing Error Handling ===")
        
        # 1. Test invalid strategy
        print("\nTesting invalid strategy handling:")
        with self.assertRaises(ValueError) as context:
            self.dcm_engine.evaluate_strategy("nonexistent_strategy")
        print(f"  Expected error raised: {context.exception}")
        
        # 2. Test invalid holding updates
        print("\nTesting invalid holding updates:")
        with self.assertRaises(Exception):
            self.portfolio_manager.update_holding("INVALID", current_price=100.0)
        print("  Expected error raised for invalid holding")
        
        # 3. Test negative prices
        print("\nTesting negative price handling:")
        symbol = "AAPL"
        success = self.portfolio_manager.update_holding(symbol, current_price=-100.0)
        self.assertFalse(success)
        print("  Successfully prevented negative price update")

if __name__ == '__main__':
    unittest.main(verbosity=2) 