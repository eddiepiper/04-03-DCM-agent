from typing import Dict, List, Optional
from dataclasses import dataclass
from data.portfolio_data import PortfolioDataManager

@dataclass
class PortfolioAnalysis:
    """Container for portfolio analysis results."""
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    sector_exposure: Dict[str, float]
    asset_allocation: Dict[str, float]
    concentration_risk: List[str]
    diversification_score: float

class PortfolioAnalysisAgent:
    def __init__(self, portfolio_manager: PortfolioDataManager):
        """Initialize the Portfolio Analysis Agent.
        
        Args:
            portfolio_manager: Instance of PortfolioDataManager for portfolio data access
        """
        self.portfolio_manager = portfolio_manager

    def analyze_portfolio(self) -> PortfolioAnalysis:
        """Perform comprehensive portfolio analysis.
        
        Returns:
            PortfolioAnalysis containing various analysis metrics
        """
        portfolio = self.portfolio_manager.portfolio
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(portfolio)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(portfolio)
        
        # Analyze sector exposure
        sector_exposure = self._analyze_sector_exposure(portfolio)
        
        # Analyze asset allocation
        asset_allocation = self._analyze_asset_allocation(portfolio)
        
        # Identify concentration risks
        concentration_risk = self._identify_concentration_risks(portfolio)
        
        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(portfolio)
        
        return PortfolioAnalysis(
            risk_metrics=risk_metrics,
            performance_metrics=performance_metrics,
            sector_exposure=sector_exposure,
            asset_allocation=asset_allocation,
            concentration_risk=concentration_risk,
            diversification_score=diversification_score
        )

    def _calculate_risk_metrics(self, portfolio) -> Dict[str, float]:
        """Calculate portfolio risk metrics."""
        # TODO: Implement risk calculation logic
        return {
            "beta": 1.1,
            "volatility": 0.15,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.25
        }

    def _calculate_performance_metrics(self, portfolio) -> Dict[str, float]:
        """Calculate portfolio performance metrics."""
        # TODO: Implement performance calculation logic
        return {
            "daily_return": 0.002,
            "weekly_return": 0.015,
            "monthly_return": 0.045,
            "year_to_date_return": 0.085,
            "annualized_return": 0.12
        }

    def _analyze_sector_exposure(self, portfolio) -> Dict[str, float]:
        """Analyze sector exposure in the portfolio."""
        sector_exposure = {}
        for holding in portfolio.holdings:
            sector_exposure[holding.sector] = sector_exposure.get(holding.sector, 0) + holding.weight
        return sector_exposure

    def _analyze_asset_allocation(self, portfolio) -> Dict[str, float]:
        """Analyze asset allocation in the portfolio."""
        asset_allocation = {}
        for holding in portfolio.holdings:
            asset_allocation[holding.asset_type] = asset_allocation.get(holding.asset_type, 0) + holding.weight
        return asset_allocation

    def _identify_concentration_risks(self, portfolio) -> List[str]:
        """Identify concentration risks in the portfolio."""
        risks = []
        constraints = self.portfolio_manager.get_constraints()
        
        # Check position concentration
        for holding in portfolio.holdings:
            if holding.weight > constraints['max_single_position'] * 0.8:  # 80% of max
                risks.append(f"High concentration in {holding.symbol} ({holding.weight:.2%})")
        
        # Check sector concentration
        sector_exposure = self._analyze_sector_exposure(portfolio)
        for sector, exposure in sector_exposure.items():
            if exposure > constraints['max_sector_exposure'] * 0.8:  # 80% of max
                risks.append(f"High sector concentration in {sector} ({exposure:.2%})")
        
        return risks

    def _calculate_diversification_score(self, portfolio) -> float:
        """Calculate portfolio diversification score (0-1)."""
        # TODO: Implement diversification scoring logic
        # For now, return a placeholder score
        return 0.85

    def generate_insights(self) -> List[str]:
        """Generate portfolio insights based on analysis."""
        analysis = self.analyze_portfolio()
        insights = []
        
        # Add insights based on risk metrics
        if analysis.risk_metrics['beta'] > 1.2:
            insights.append("Portfolio shows high market sensitivity")
        if analysis.risk_metrics['volatility'] > 0.2:
            insights.append("Portfolio volatility is above target range")
        
        # Add insights based on sector exposure
        for sector, exposure in analysis.sector_exposure.items():
            if exposure > 0.3:  # 30% threshold
                insights.append(f"High concentration in {sector} sector")
        
        # Add insights based on concentration risks
        insights.extend(analysis.concentration_risk)
        
        # Add insights based on diversification
        if analysis.diversification_score < 0.7:
            insights.append("Portfolio could benefit from increased diversification")
        
        return insights 