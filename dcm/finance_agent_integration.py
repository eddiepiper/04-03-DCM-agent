from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.models.openai import OpenAIChat
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download required NLTK data
nltk.download('vader_lexicon')

@dataclass
class MarketInsights:
    """Container for market insights from FinanceAgent."""
    symbol: str
    current_price: float
    analyst_recommendations: List[Dict]
    company_info: Dict
    news_sentiment: str
    market_sentiment: str
    web_research: List[Dict]

class FinanceAgentIntegration:
    def __init__(self):
        """Initialize the Finance Agent Integration."""
        self.sia = SentimentIntensityAnalyzer()
        
        # Initialize Web Agent
        self.web_agent = Agent(
            name="Web Agent",
            role="Search the web for information",
            model=OpenAIChat(id="gpt-4o"),
            tools=[DuckDuckGoTools()],
            storage=SqliteAgentStorage(table_name="web_agent", db_file="agents.db"),
            add_history_to_messages=True,
            markdown=True,
        )
        
        # Initialize Finance Agent
        self.finance_agent = Agent(
            name="Finance Agent",
            role="Get financial data and insights",
            tools=[YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                company_info=True,
                company_news=True
            )],
            instructions=[
                "Always use tables to display financial data.",
                "When financial news is available, analyze its sentiment and classify it as Bullish, Bearish, or Neutral."
            ],
            storage=SqliteAgentStorage(table_name="finance_agent", db_file="agents.db"),
            add_history_to_messages=True,
            markdown=True,
        )

    async def get_market_insights(self, symbol: str) -> Optional[MarketInsights]:
        """Get comprehensive market insights for a symbol.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            MarketInsights object or None if data cannot be fetched
        """
        try:
            # Get financial data
            finance_data = await self.finance_agent.get_stock_data(symbol)
            
            # Get analyst recommendations
            recommendations = await self.finance_agent.get_analyst_recommendations(symbol)
            
            # Get company information
            company_info = await self.finance_agent.get_company_info(symbol)
            
            # Get company news and analyze sentiment
            news = await self.finance_agent.get_company_news(symbol)
            news_sentiment = self._analyze_news_sentiment(news)
            
            # Get market sentiment
            market_sentiment = self._analyze_market_sentiment(finance_data)
            
            # Get web research
            web_research = await self.web_agent.search(f"{symbol} stock market analysis")
            
            return MarketInsights(
                symbol=symbol,
                current_price=finance_data.get('current_price', 0.0),
                analyst_recommendations=recommendations,
                company_info=company_info,
                news_sentiment=news_sentiment,
                market_sentiment=market_sentiment,
                web_research=web_research
            )
            
        except Exception as e:
            print(f"Error getting market insights for {symbol}: {str(e)}")
            return None

    async def get_portfolio_insights(self, symbols: List[str]) -> Dict[str, MarketInsights]:
        """Get market insights for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to their market insights
        """
        insights = {}
        for symbol in symbols:
            insight = await self.get_market_insights(symbol)
            if insight:
                insights[symbol] = insight
        return insights

    def _analyze_news_sentiment(self, news: List[Dict]) -> str:
        """Analyze sentiment of company news."""
        if not news:
            return "Neutral"
            
        sentiments = []
        for article in news[:5]:  # Analyze last 5 news items
            if 'title' in article and 'content' in article:
                # Consider both title and content for sentiment
                title_sentiment = self.sia.polarity_scores(article['title'])
                content_sentiment = self.sia.polarity_scores(article['content'])
                # Average the compound scores
                avg_compound = (title_sentiment['compound'] + content_sentiment['compound']) / 2
                sentiments.append(avg_compound)
        
        if not sentiments:
            return "Neutral"
            
        avg_sentiment = sum(sentiments) / len(sentiments)
        if avg_sentiment >= 0.15:  # Adjusted threshold for bullish
            return "Bullish"
        elif avg_sentiment <= -0.15:  # Adjusted threshold for bearish
            return "Bearish"
        else:
            return "Neutral"

    def _analyze_market_sentiment(self, finance_data: Dict) -> str:
        """Analyze market sentiment based on technical indicators."""
        try:
            # Simple sentiment based on price momentum
            if finance_data.get('fifty_day_avg', 0) > finance_data.get('two_hundred_day_avg', 0):
                return "Bullish"
            elif finance_data.get('fifty_day_avg', 0) < finance_data.get('two_hundred_day_avg', 0):
                return "Bearish"
            else:
                return "Neutral"
        except:
            return "Neutral"

    def get_analyst_consensus(self, recommendations: List[Dict]) -> Tuple[str, float]:
        """Get analyst consensus from recommendations.
        
        Args:
            recommendations: List of analyst recommendations
            
        Returns:
            Tuple of (consensus, confidence_score)
        """
        if not recommendations:
            return "Neutral", 0.5
            
        # Map recommendation strings to numeric values
        recommendation_values = {
            "Strong Buy": 1.0,
            "Buy": 0.75,
            "Hold": 0.5,
            "Sell": 0.25,
            "Strong Sell": 0.0
        }
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for rec in recommendations:
            value = recommendation_values.get(rec.get('recommendation', 'Hold'), 0.5)
            weight = rec.get('weight', 1.0)
            weighted_sum += value * weight
            total_weight += weight
            
        if total_weight == 0:
            return "Neutral", 0.5
            
        avg_value = weighted_sum / total_weight
        
        # Map back to recommendation string with adjusted thresholds
        if avg_value >= 0.8:  # More conservative threshold for Strong Buy
            return "Strong Buy", avg_value
        elif avg_value >= 0.65:  # More conservative threshold for Buy
            return "Buy", avg_value
        elif avg_value >= 0.35:  # Wider range for Hold
            return "Hold", avg_value
        elif avg_value >= 0.2:  # More conservative threshold for Sell
            return "Sell", avg_value
        else:
            return "Strong Sell", avg_value 