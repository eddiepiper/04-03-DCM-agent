from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from decimal import Decimal

@dataclass
class MarketData:
    """Base class for market data."""
    symbol: str
    current_price: Decimal
    volume: int
    market_cap: int
    beta: float
    volatility: float

@dataclass
class MarketInsights(MarketData):
    """Extended market data with sentiment and research insights."""
    market_sentiment: str = "Neutral"
    news_sentiment: str = "Neutral"
    analyst_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    web_research: List[Dict[str, str]] = field(default_factory=list)
    company_info: Dict[str, Any] = field(default_factory=dict)

class MarketDataManager:
    """Manager class for handling market data operations."""
    def __init__(self):
        self.market_data = {}

    async def get_portfolio_market_data(self, symbols: List[str]) -> Dict[str, MarketInsights]:
        """Get market data for a list of symbols."""
        # In a real implementation, this would fetch data from external sources
        # For testing, we'll return mock data
        mock_data = {}
        for symbol in symbols:
            mock_data[symbol] = MarketInsights(
                symbol=symbol,
                current_price=Decimal("100.0"),
                volume=1000000,
                market_cap=1000000000,
                beta=1.0,
                volatility=0.2,
                market_sentiment="Neutral",
                news_sentiment="Neutral",
                analyst_recommendations=[
                    {"recommendation": "Hold", "weight": 0.5}
                ],
                web_research=[
                    {"title": "Analysis", "content": "Stable outlook"}
                ]
            )
        return mock_data

    async def update_market_data(self, symbol: str, data: MarketInsights) -> None:
        """Update market data for a symbol."""
        self.market_data[symbol] = data

    async def get_market_data(self, symbol: str) -> Optional[MarketInsights]:
        """Get market data for a single symbol."""
        return self.market_data.get(symbol)

    async def get_sentiment_data(self, symbol: str) -> Dict[str, str]:
        """Get sentiment data for a symbol."""
        data = await self.get_market_data(symbol)
        if data:
            return {
                "market_sentiment": data.market_sentiment,
                "news_sentiment": data.news_sentiment
            }
        return {
            "market_sentiment": "Neutral",
            "news_sentiment": "Neutral"
        }

    async def get_research_data(self, symbol: str) -> Dict[str, Any]:
        """Get research data for a symbol."""
        data = await self.get_market_data(symbol)
        if data:
            return {
                "analyst_recommendations": data.analyst_recommendations,
                "web_research": data.web_research,
                "company_info": data.company_info
            }
        return {
            "analyst_recommendations": [],
            "web_research": [],
            "company_info": {}
        } 