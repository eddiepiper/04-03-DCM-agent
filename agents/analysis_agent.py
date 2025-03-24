from typing import Dict, List, Optional
from dataclasses import dataclass
from data.portfolio_data import PortfolioDataManager

@dataclass
class PortfolioAnalysis:
    asset_allocation: Dict[str, float]
    sector_allocation: Dict[str, float]
    risk_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    total_value: float
    holdings_count: int

class PortfolioAnalysisAgent:
    def __init__(self, portfolio_manager: PortfolioDataManager):
        """Initialize the Portfolio Analysis Agent.
        
        Args:
            portfolio_manager: Instance of PortfolioDataManager for portfolio data access
        """
        self.portfolio_manager = portfolio_manager

    def analyze_portfolio(self) -> PortfolioAnalysis:
        """Analyze the current portfolio state.
        
        Returns:
            PortfolioAnalysis object containing portfolio metrics and analysis
        """
        portfolio = self.portfolio_manager.portfolio
        
        return PortfolioAnalysis(
            asset_allocation=portfolio.asset_allocation,
            sector_allocation=portfolio.sector_allocation,
            risk_metrics=portfolio.risk_metrics,
            performance_metrics=portfolio.performance_metrics,
            total_value=portfolio.total_value,
            holdings_count=len(portfolio.holdings)
        )

    def get_holding_analysis(self, symbol: str) -> Optional[Dict]:
        """Get detailed analysis for a specific holding.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dictionary containing holding analysis or None if not found
        """
        holding = self.portfolio_manager.get_holding(symbol)
        if not holding:
            return None
            
        return {
            'symbol': holding.symbol,
            'name': holding.name,
            'asset_type': holding.asset_type,
            'sector': holding.sector,
            'quantity': holding.quantity,
            'current_price': holding.current_price,
            'total_value': holding.total_value,
            'weight': holding.weight
        }

    def get_portfolio_summary(self) -> Dict:
        """Get a summary of the portfolio's current state.
        
        Returns:
            Dictionary containing portfolio summary metrics
        """
        portfolio = self.portfolio_manager.portfolio
        analysis = self.analyze_portfolio()
        
        return {
            'portfolio_id': portfolio.portfolio_id,
            'total_value': portfolio.total_value,
            'currency': portfolio.currency,
            'last_updated': portfolio.last_updated,
            'holdings_count': analysis.holdings_count,
            'asset_allocation': analysis.asset_allocation,
            'sector_allocation': analysis.sector_allocation,
            'risk_metrics': analysis.risk_metrics,
            'performance_metrics': analysis.performance_metrics
        } 