import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import sys
import nltk
sys.path.append(str(Path(__file__).parent.parent))
from data.portfolio_data import PortfolioDataManager
from data.market_data import MarketDataManager, MarketData
from dcm.finance_agent_integration import FinanceAgentIntegration, MarketInsights
from nltk.sentiment import SentimentIntensityAnalyzer
from .portfolio import Portfolio, PortfolioManager

# Download VADER lexicon for sentiment analysis
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

@dataclass
class Strategy:
    name: str
    description: str
    confidence_score: float = 0.8
    times_used: int = 0
    last_performance: float = 0.0
    active: bool = True
    parameters: Dict = field(default_factory=lambda: {
        "rebalance_threshold": 0.05,
        "min_holdings": 3
    })

    def __post_init__(self):
        """Validate strategy attributes."""
        if not self.name:
            raise ValueError("Strategy name cannot be empty")
        if not self.description:
            raise ValueError("Strategy description cannot be empty")
        if not 0 <= self.confidence_score <= 1:
            raise ValueError("Confidence score must be between 0 and 1")
        if self.times_used < 0:
            raise ValueError("Times used cannot be negative")
        if self.parameters is None:
            self.parameters = {}

class DCMEngine:
    def __init__(self, capabilities_file: str = "dcm/capabilities.json"):
        self.capabilities_file = Path(capabilities_file)
        self.portfolio_manager = PortfolioDataManager()
        self.market_data_manager = MarketDataManager()
        self.finance_agent = FinanceAgentIntegration()
        self.sia = SentimentIntensityAnalyzer()
        self.capabilities = self._load_capabilities()
        self.strategies = self._initialize_strategies()

    def _load_capabilities(self) -> Dict:
        """Load capabilities data from JSON file."""
        if not self.capabilities_file.exists():
            raise FileNotFoundError(f"Capabilities file not found: {self.capabilities_file}")

        with open(self.capabilities_file, 'r') as f:
            return json.load(f)

    def _initialize_strategies(self) -> Dict[str, Strategy]:
        """Initialize strategy objects from capabilities data."""
        return {
            name: Strategy(**data)
            for name, data in self.capabilities['strategies'].items()
        }

    def save_capabilities(self) -> None:
        """Save current capabilities state to JSON file."""
        capabilities_dict = {
            'strategies': {
                name: {
                    'name': strategy.name,
                    'description': strategy.description,
                    'confidence_score': strategy.confidence_score,
                    'times_used': strategy.times_used,
                    'last_performance': strategy.last_performance,
                    'active': strategy.active,
                    'parameters': strategy.parameters
                }
                for name, strategy in self.strategies.items()
            },
            'performance_history': self.capabilities['performance_history'],
            'last_update': datetime.utcnow().isoformat()
        }

        with open(self.capabilities_file, 'w') as f:
            json.dump(capabilities_dict, f, indent=4)

    def evaluate_strategy(self, portfolio_manager: PortfolioManager) -> Tuple[float, Dict[str, float]]:
        """Evaluate strategy and generate recommendations."""
        try:
            portfolio = portfolio_manager.portfolio
            if not portfolio or not portfolio.holdings:
                return 0.0, {}

            # Get market data and insights
            market_data = self.market_data_manager.get_portfolio_market_data(portfolio)
            market_insights = {}
            for symbol in portfolio.holdings:
                try:
                    insights = self.finance_agent.get_market_insights_sync(symbol)
                    if insights:
                        market_insights[symbol] = insights
                except Exception as e:
                    print(f"Error getting market insights for {symbol}: {str(e)}")

            # Calculate scores
            analyst_score = self._calculate_analyst_score(market_insights)
            research_score = self._calculate_research_score(market_insights)
            risk_score = self._calculate_risk_metrics(portfolio, market_data)
            performance_score = self._calculate_performance_metrics(portfolio, market_data)
            sentiment_score = self._calculate_sentiment_score(market_insights)

            # Calculate overall score
            strategy_score = (
                analyst_score * 0.3 +
                research_score * 0.2 +
                risk_score * 0.2 +
                performance_score * 0.2 +
                sentiment_score * 0.1
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                portfolio,
                market_data,
                market_insights,
                strategy_score
            )

            return strategy_score, recommendations

        except Exception as e:
            print(f"Error in strategy evaluation: {str(e)}")
            return 0.0, {}

    def _calculate_analyst_score(self, market_insights: Dict[str, MarketInsights]) -> float:
        """Calculate score based on analyst recommendations."""
        if not market_insights:
            return 0.5

        total_score = 0.0
        count = 0
        for insights in market_insights.values():
            if insights.analyst_recommendations:
                recommendations = insights.analyst_recommendations
                score = sum(rec.get("weight", 0.0) for rec in recommendations)
                total_score += score
                count += 1

        return total_score / count if count > 0 else 0.5

    def _calculate_research_score(self, market_insights: Dict[str, MarketInsights]) -> float:
        """Calculate score based on research and news."""
        if not market_insights:
            return 0.5

        total_score = 0.0
        count = 0
        for insights in market_insights.values():
            if insights.web_research:
                # Simple sentiment analysis based on content
                score = 0.5  # Neutral by default
                for research in insights.web_research:
                    content = research.get("content", "").lower()
                    if "positive" in content or "bullish" in content:
                        score += 0.1
                    elif "negative" in content or "bearish" in content:
                        score -= 0.1
                total_score += max(0.0, min(1.0, score))
                count += 1

        return total_score / count if count > 0 else 0.5

    def _calculate_risk_metrics(self, portfolio: Portfolio, market_data: Dict) -> float:
        """Calculate risk metrics for the portfolio."""
        if not portfolio.holdings or not market_data:
            return 0.5

        # Calculate portfolio beta and volatility
        total_beta = 0.0
        total_volatility = 0.0
        for symbol, holding in portfolio.holdings.items():
            if symbol in market_data:
                data = market_data[symbol]
                total_beta += data.beta * holding.weight
                total_volatility += data.volatility * holding.weight

        # Normalize scores between 0 and 1
        risk_score = 1.0 - (total_beta * 0.5 + total_volatility * 0.5)
        return max(0.0, min(1.0, risk_score))

    def _calculate_performance_metrics(self, portfolio: Portfolio, market_data: Dict) -> float:
        """Calculate performance metrics for the portfolio."""
        if not portfolio.holdings or not market_data:
            return 0.5

        # Calculate returns and Sharpe ratio
        total_return = sum(
            market_data[symbol].current_price / holding.current_price - 1
            for symbol, holding in portfolio.holdings.items()
            if symbol in market_data
        )
        avg_return = total_return / len(portfolio.holdings)

        # Normalize score between 0 and 1
        performance_score = 0.5 + avg_return
        return max(0.0, min(1.0, performance_score))

    def _calculate_sentiment_score(self, market_insights: Dict[str, MarketInsights]) -> float:
        """Calculate sentiment score based on market and news sentiment."""
        if not market_insights:
            return 0.5

        sentiment_map = {
            "Bullish": 1.0,
            "Neutral": 0.5,
            "Bearish": 0.0
        }

        total_score = 0.0
        count = 0
        for insights in market_insights.values():
            market_score = sentiment_map.get(insights.market_sentiment, 0.5)
            news_score = sentiment_map.get(insights.news_sentiment, 0.5)
            total_score += (market_score + news_score) / 2
            count += 1

        return total_score / count if count > 0 else 0.5

    def _calculate_equal_weights(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calculate equal weights for all holdings."""
        if not portfolio.holdings:
            return {}
        weight = 1.0 / len(portfolio.holdings)
        return {symbol: weight for symbol in portfolio.holdings}

    def _calculate_risk_parity_weights(self, portfolio: Portfolio, market_data: Dict) -> Dict[str, float]:
        """Calculate risk parity weights based on volatility."""
        if not portfolio.holdings or not market_data:
            return self._calculate_equal_weights(portfolio)

        total_vol = sum(
            1.0 / market_data[symbol].volatility
            for symbol in portfolio.holdings
            if symbol in market_data
        )

        return {
            symbol: (1.0 / market_data[symbol].volatility) / total_vol
            for symbol in portfolio.holdings
            if symbol in market_data
        }

    def _generate_recommendations(
        self,
        portfolio: Portfolio,
        market_data: Dict,
        market_insights: Dict[str, MarketInsights],
        strategy_score: float
    ) -> Dict[str, float]:
        """Generate portfolio rebalancing recommendations."""
        if not portfolio.holdings:
            return {}

        # Choose weights calculation method based on strategy score
        if strategy_score > 0.7:
            target_weights = self._calculate_risk_parity_weights(portfolio, market_data)
        else:
            target_weights = self._calculate_equal_weights(portfolio)

        # Calculate weight changes
        current_weights = {symbol: holding.weight for symbol, holding in portfolio.holdings.items()}
        recommendations = {}
        for symbol in portfolio.holdings:
            if symbol in target_weights:
                weight_change = target_weights[symbol] - current_weights.get(symbol, 0.0)
                if abs(weight_change) >= 0.01:  # 1% minimum change threshold
                    recommendations[symbol] = weight_change

        return recommendations

    def get_best_strategy(self) -> Tuple[str, float, Dict[str, float]]:
        """Evaluate all strategies and return the best one."""
        best_score = -1
        best_strategy = None
        best_recommendations = None

        for strategy_name in self.strategies:
            if not self.strategies[strategy_name].active:
                continue

            score, recommendations = self.evaluate_strategy(self.portfolio_manager)
            if score > best_score:
                best_score = score
                best_strategy = strategy_name
                best_recommendations = recommendations

        return best_strategy, best_score, best_recommendations

    def update_strategy_performance(self, strategy_name: str, performance: float) -> None:
        """Update strategy performance metrics."""
        if strategy_name not in self.strategies:
            return

        strategy = self.strategies[strategy_name]
        strategy.times_used += 1
        strategy.last_performance = performance
        
        # Update confidence score based on performance
        alpha = 0.7  # Weight for historical confidence
        beta = 0.3   # Weight for new performance
        strategy.confidence_score = (
            alpha * strategy.confidence_score +
            beta * performance
        )

        # Update performance history
        self.capabilities['performance_history'].append({
            'strategy': strategy_name,
            'performance': performance,
            'timestamp': datetime.utcnow().isoformat()
        })

        self.save_capabilities() 