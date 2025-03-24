from typing import Dict, List, Optional
from dataclasses import dataclass
from data.portfolio_data import PortfolioDataManager, Portfolio, Holding
from agents.portfolio_analysis_agent import PortfolioAnalysisAgent
from agents.bank_policy_agent import BankPolicyAgent

@dataclass
class RebalanceRecommendation:
    """Container for rebalancing recommendations."""
    symbol: str
    current_weight: float
    target_weight: float
    weight_change: float
    reason: str
    priority: int  # 1: High, 2: Medium, 3: Low

class RebalanceStrategyAgent:
    def __init__(self, portfolio_manager: PortfolioDataManager):
        """Initialize the Rebalance Strategy Agent.
        
        Args:
            portfolio_manager: Instance of PortfolioDataManager for portfolio data access
        """
        self.portfolio_manager = portfolio_manager
        self.analysis_agent = PortfolioAnalysisAgent(portfolio_manager)
        self.policy_agent = BankPolicyAgent(portfolio_manager)

    def generate_rebalance_recommendations(self) -> List[RebalanceRecommendation]:
        """Generate rebalancing recommendations based on portfolio analysis.
        
        Returns:
            List of RebalanceRecommendation objects
        """
        recommendations = []
        portfolio = self.portfolio_manager.portfolio
        analysis = self.analysis_agent.analyze_portfolio()
        constraints = self.portfolio_manager.get_constraints()
        
        # 1. Address concentration risks first
        concentration_recommendations = self._address_concentration_risks(
            portfolio, analysis, constraints
        )
        recommendations.extend(concentration_recommendations)
        
        # 2. Address sector exposure issues
        sector_recommendations = self._address_sector_exposure(
            portfolio, analysis, constraints
        )
        recommendations.extend(sector_recommendations)
        
        # 3. Address asset allocation issues
        allocation_recommendations = self._address_asset_allocation(
            portfolio, analysis, constraints
        )
        recommendations.extend(allocation_recommendations)
        
        # 4. Optimize for risk-adjusted returns
        optimization_recommendations = self._optimize_risk_adjusted_returns(
            portfolio, analysis
        )
        recommendations.extend(optimization_recommendations)
        
        # Sort recommendations by priority
        recommendations.sort(key=lambda x: x.priority)
        
        return recommendations

    def _address_concentration_risks(
        self, portfolio, analysis, constraints
    ) -> List[RebalanceRecommendation]:
        """Generate recommendations to address concentration risks."""
        recommendations = []
        
        # Check position concentration
        for holding in portfolio.holdings:
            if holding.weight > constraints['max_single_position'] * 0.8:
                target_weight = constraints['max_single_position'] * 0.7
                recommendations.append(RebalanceRecommendation(
                    symbol=holding.symbol,
                    current_weight=holding.weight,
                    target_weight=target_weight,
                    weight_change=target_weight - holding.weight,
                    reason="Reduce position concentration",
                    priority=1
                ))
        
        return recommendations

    def _address_sector_exposure(
        self, portfolio, analysis, constraints
    ) -> List[RebalanceRecommendation]:
        """Generate recommendations to address sector exposure issues."""
        recommendations = []
        
        # Check sector exposure
        for sector, exposure in analysis.sector_exposure.items():
            if exposure > constraints['max_sector_exposure'] * 0.8:
                # Find holdings in the sector
                sector_holdings = [
                    h for h in portfolio.holdings 
                    if h.sector == sector
                ]
                
                # Calculate target weight per holding
                target_weight = constraints['max_sector_exposure'] * 0.7 / len(sector_holdings)
                
                for holding in sector_holdings:
                    recommendations.append(RebalanceRecommendation(
                        symbol=holding.symbol,
                        current_weight=holding.weight,
                        target_weight=target_weight,
                        weight_change=target_weight - holding.weight,
                        reason=f"Reduce {sector} sector exposure",
                        priority=2
                    ))
        
        return recommendations

    def _address_asset_allocation(
        self, portfolio, analysis, constraints
    ) -> List[RebalanceRecommendation]:
        """Generate recommendations to address asset allocation issues."""
        recommendations = []
        
        # Check bond allocation
        bond_allocation = analysis.asset_allocation.get('Fixed Income', 0)
        if bond_allocation < constraints['min_bond_allocation']:
            # Find bond holdings
            bond_holdings = [
                h for h in portfolio.holdings 
                if h.asset_type.lower().replace(" ", "_") in ['bond', 'fixed_income']
            ]
            
            if bond_holdings:
                # Calculate target weight per bond holding
                target_weight = constraints['min_bond_allocation'] / len(bond_holdings)
                
                for holding in bond_holdings:
                    recommendations.append(RebalanceRecommendation(
                        symbol=holding.symbol,
                        current_weight=holding.weight,
                        target_weight=target_weight,
                        weight_change=target_weight - holding.weight,
                        reason="Increase bond allocation",
                        priority=2
                    ))
        
        return recommendations

    def _optimize_risk_adjusted_returns(
        self, portfolio, analysis
    ) -> List[RebalanceRecommendation]:
        """Generate recommendations to optimize risk-adjusted returns."""
        recommendations = []
        
        # Check risk metrics
        if analysis.risk_metrics['beta'] > 1.2:
            # Find high-beta holdings
            high_beta_holdings = [
                h for h in portfolio.holdings 
                if h.asset_type.lower() in ['stock', 'etf']
            ]
            
            for holding in high_beta_holdings:
                recommendations.append(RebalanceRecommendation(
                    symbol=holding.symbol,
                    current_weight=holding.weight,
                    target_weight=holding.weight * 0.9,  # Reduce by 10%
                    weight_change=holding.weight * -0.1,
                    reason="Reduce portfolio beta",
                    priority=3
                ))
        
        return recommendations

    def validate_recommendations(
        self, recommendations: List[RebalanceRecommendation]
    ) -> bool:
        """Validate that recommendations meet all constraints."""
        # Create a copy of the portfolio with proposed changes
        portfolio = self.portfolio_manager.portfolio
        proposed_weights = {
            holding.symbol: holding.weight 
            for holding in portfolio.holdings
        }
        
        # Apply recommendations
        for rec in recommendations:
            proposed_weights[rec.symbol] = rec.target_weight
        
        # Create a temporary portfolio with proposed weights
        temp_portfolio = Portfolio(
            portfolio_id="TEMP",
            currency=portfolio.currency,
            last_updated=portfolio.last_updated,
            holdings=[
                Holding(
                    symbol=h.symbol,
                    name=h.name,
                    current_price=h.current_price,
                    quantity=h.quantity,
                    total_value=h.total_value,
                    weight=proposed_weights[h.symbol],
                    asset_type=h.asset_type,
                    sector=h.sector
                )
                for h in portfolio.holdings
            ],
            total_value=portfolio.total_value,
            asset_allocation=portfolio.asset_allocation,
            sector_allocation=portfolio.sector_allocation,
            risk_metrics=portfolio.risk_metrics,
            performance_metrics=portfolio.performance_metrics,
            constraints=portfolio.constraints
        )
        
        # Validate the temporary portfolio
        temp_manager = PortfolioDataManager()
        temp_manager.portfolio = temp_portfolio
        policy_agent = BankPolicyAgent(temp_manager)
        result = policy_agent.validate_portfolio()
        
        return result.is_valid 