from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from data.portfolio_data import PortfolioDataManager

@dataclass
class PolicyValidationResult:
    is_valid: bool
    violations: List[str]
    warnings: List[str]

class BankPolicyAgent:
    def __init__(self, portfolio_manager: PortfolioDataManager):
        """Initialize the Bank Policy Agent.
        
        Args:
            portfolio_manager: Instance of PortfolioDataManager for portfolio data access
        """
        self.portfolio_manager = portfolio_manager

    def validate_portfolio(self) -> PolicyValidationResult:
        """Validate the current portfolio against all policies.
        
        Returns:
            PolicyValidationResult containing validation status and any violations/warnings
        """
        violations = []
        warnings = []
        
        # Get current portfolio state
        portfolio = self.portfolio_manager.portfolio
        constraints = self.portfolio_manager.get_constraints()
        
        # Validate cash balance
        cash_balance = 1.0 - sum(h.weight for h in portfolio.holdings)
        if cash_balance < constraints['min_cash_balance']:
            violations.append(f"Cash balance ({cash_balance:.2%}) below minimum ({constraints['min_cash_balance']:.2%})")
        
        # Validate position sizes
        for holding in portfolio.holdings:
            if holding.weight > constraints['max_single_position']:
                violations.append(
                    f"Position size for {holding.symbol} ({holding.weight:.2%}) "
                    f"exceeds maximum ({constraints['max_single_position']:.2%})"
                )
        
        # Validate sector exposure
        sector_exposure = {}
        for holding in portfolio.holdings:
            sector_exposure[holding.sector] = sector_exposure.get(holding.sector, 0) + holding.weight
        
        for sector, exposure in sector_exposure.items():
            if exposure > constraints['max_sector_exposure']:
                violations.append(
                    f"Sector exposure for {sector} ({exposure:.2%}) "
                    f"exceeds maximum ({constraints['max_sector_exposure']:.2%})"
                )
        
        # Validate bond allocation
        bond_allocation = sum(
            h.weight for h in portfolio.holdings 
            if h.asset_type.lower().replace(" ", "_") in ['bond', 'fixed_income']
        )
        
        if bond_allocation < constraints['min_bond_allocation']:
            violations.append(
                f"Bond allocation ({bond_allocation:.2%}) "
                f"below minimum ({constraints['min_bond_allocation']:.2%})"
            )
        elif bond_allocation > constraints['max_bond_allocation']:
            violations.append(
                f"Bond allocation ({bond_allocation:.2%}) "
                f"exceeds maximum ({constraints['max_bond_allocation']:.2%})"
            )
        
        # Add warnings for near-violations
        for holding in portfolio.holdings:
            if holding.weight > constraints['max_single_position'] * 0.9:  # 90% of max
                warnings.append(
                    f"Position size for {holding.symbol} ({holding.weight:.2%}) "
                    f"approaching maximum ({constraints['max_single_position']:.2%})"
                )
        
        return PolicyValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings
        )

    def validate_recommendations(self, recommendations: Dict[str, float]) -> PolicyValidationResult:
        """Validate proposed portfolio changes against policies.
        
        Args:
            recommendations: Dictionary of symbol to weight change recommendations
            
        Returns:
            PolicyValidationResult containing validation status and any violations/warnings
        """
        violations = []
        warnings = []
        
        # Get current portfolio state
        portfolio = self.portfolio_manager.portfolio
        constraints = self.portfolio_manager.get_constraints()
        
        # Calculate proposed weights
        proposed_weights = {}
        for holding in portfolio.holdings:
            proposed_weights[holding.symbol] = holding.weight + recommendations.get(holding.symbol, 0)
        
        # Validate proposed position sizes
        for symbol, weight in proposed_weights.items():
            if weight > constraints['max_single_position']:
                violations.append(
                    f"Proposed position size for {symbol} ({weight:.2%}) "
                    f"exceeds maximum ({constraints['max_single_position']:.2%})"
                )
            elif weight > constraints['max_single_position'] * 0.9:
                warnings.append(
                    f"Proposed position size for {symbol} ({weight:.2%}) "
                    f"approaching maximum ({constraints['max_single_position']:.2%})"
                )
        
        # Validate proposed sector exposure
        proposed_sector_exposure = {}
        for holding in portfolio.holdings:
            symbol = holding.symbol
            sector = holding.sector
            proposed_sector_exposure[sector] = proposed_sector_exposure.get(sector, 0) + proposed_weights[symbol]
        
        for sector, exposure in proposed_sector_exposure.items():
            if exposure > constraints['max_sector_exposure']:
                violations.append(
                    f"Proposed sector exposure for {sector} ({exposure:.2%}) "
                    f"exceeds maximum ({constraints['max_sector_exposure']:.2%})"
                )
        
        # Validate proposed bond allocation
        proposed_bond_allocation = sum(
            proposed_weights[h.symbol] 
            for h in portfolio.holdings 
            if h.asset_type.lower().replace(" ", "_") in ['bond', 'fixed_income']
        )
        
        if proposed_bond_allocation < constraints['min_bond_allocation']:
            violations.append(
                f"Proposed bond allocation ({proposed_bond_allocation:.2%}) "
                f"below minimum ({constraints['min_bond_allocation']:.2%})"
            )
        elif proposed_bond_allocation > constraints['max_bond_allocation']:
            violations.append(
                f"Proposed bond allocation ({proposed_bond_allocation:.2%}) "
                f"exceeds maximum ({constraints['max_bond_allocation']:.2%})"
            )
        
        return PolicyValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings
        ) 