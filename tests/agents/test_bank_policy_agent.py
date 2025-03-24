import unittest
from pathlib import Path
import sys
import json
from dataclasses import dataclass
from typing import List, Dict
sys.path.append(str(Path(__file__).parent.parent))
from data.portfolio_data import PortfolioDataManager, Portfolio, Holding
from agents.bank_policy_agent import BankPolicyAgent, PolicyValidationResult

class TestBankPolicyAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create a test portfolio that meets all constraints
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
        self.policy_agent = BankPolicyAgent(self.portfolio_manager)

    def test_validate_portfolio(self):
        """Test portfolio validation functionality."""
        result = self.policy_agent.validate_portfolio()
        
        # Verify result type
        self.assertIsInstance(result, PolicyValidationResult)
        self.assertIsInstance(result.is_valid, bool)
        self.assertIsInstance(result.violations, list)
        self.assertIsInstance(result.warnings, list)
        
        # Verify portfolio constraints
        portfolio = self.portfolio_manager.portfolio
        constraints = self.portfolio_manager.get_constraints()
        
        # Check position sizes
        for holding in portfolio.holdings:
            self.assertLessEqual(holding.weight, constraints['max_single_position'])
        
        # Check sector exposure
        sector_exposure = {}
        for holding in portfolio.holdings:
            sector_exposure[holding.sector] = sector_exposure.get(holding.sector, 0) + holding.weight
        
        for sector, exposure in sector_exposure.items():
            self.assertLessEqual(exposure, constraints['max_sector_exposure'])
        
        # Check bond allocation
        bond_allocation = sum(
            h.weight for h in portfolio.holdings 
            if h.asset_type.lower().replace(" ", "_") in ['bond', 'fixed_income']
        )
        self.assertGreaterEqual(bond_allocation, constraints['min_bond_allocation'])
        self.assertLessEqual(bond_allocation, constraints['max_bond_allocation'])

    def test_validate_recommendations(self):
        """Test recommendation validation functionality."""
        # Test valid recommendations
        valid_recommendations = {
            'AAPL': 0.01,  # Small increase
            'MSFT': -0.01,  # Small decrease
            'VTI': 0.0,    # No change
            'BND': 0.0,    # No change
            'AGG': 0.0     # No change
        }
        
        result = self.policy_agent.validate_recommendations(valid_recommendations)
        self.assertIsInstance(result, PolicyValidationResult)
        self.assertTrue(result.is_valid)
        
        # Test invalid recommendations (exceeding position limits)
        invalid_recommendations = {
            'AAPL': 0.5,   # Would exceed max position size
            'MSFT': 0.0,
            'VTI': 0.0,
            'BND': 0.0,
            'AGG': 0.0
        }
        
        result = self.policy_agent.validate_recommendations(invalid_recommendations)
        self.assertIsInstance(result, PolicyValidationResult)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.violations), 0)
        
        # Test recommendations that would violate sector exposure
        sector_violation_recommendations = {
            'AAPL': 0.2,   # Large increase in tech sector
            'MSFT': 0.2,   # Another large increase in tech sector
            'VTI': -0.4,   # Decrease in other sectors
            'BND': 0.0,
            'AGG': 0.0
        }
        
        result = self.policy_agent.validate_recommendations(sector_violation_recommendations)
        self.assertIsInstance(result, PolicyValidationResult)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.violations), 0)
        
        # Test recommendations that would violate bond allocation
        bond_violation_recommendations = {
            'AAPL': 0.0,
            'MSFT': 0.0,
            'VTI': 0.0,
            'BND': 0.5,    # Would exceed max bond allocation
            'AGG': 0.0
        }
        
        result = self.policy_agent.validate_recommendations(bond_violation_recommendations)
        self.assertIsInstance(result, PolicyValidationResult)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.violations), 0)

    def test_warning_generation(self):
        """Test warning generation for near-violations."""
        # Create recommendations that would approach but not exceed limits
        warning_recommendations = {
            'AAPL': 0.03,   # Would approach max position size (0.20 + 0.03 = 0.23)
            'MSFT': 0.0,
            'VTI': 0.0,
            'BND': 0.0,
            'AGG': 0.0
        }
        
        result = self.policy_agent.validate_recommendations(warning_recommendations)
        self.assertIsInstance(result, PolicyValidationResult)
        self.assertTrue(result.is_valid)  # Should be valid (no violations)
        self.assertGreater(len(result.warnings), 0)  # Should have warnings

if __name__ == '__main__':
    unittest.main() 