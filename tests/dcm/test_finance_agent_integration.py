import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dcm.dcm_engine import DCMEngine
from dcm.finance_agent_integration import FinanceAgentIntegration, MarketInsights
from data.portfolio_data import Portfolio, Holding
from data.market_data import MarketData

class AsyncTestCase(unittest.TestCase):
    """Base class for async tests."""
    def run_async(self, coro):
        return asyncio.run(coro)

class TestFinanceAgentIntegration(AsyncTestCase):
    def setUp(self):
        """Set up test environment."""
        self.finance_agent = FinanceAgentIntegration()
        
        # Create test market insights
        self.test_insights = {
            "AAPL": MarketInsights(
                symbol="AAPL",
                current_price=155.0,
                analyst_recommendations=[
                    {"recommendation": "Strong Buy", "weight": 1.0},
                    {"recommendation": "Buy", "weight": 0.8},
                    {"recommendation": "Hold", "weight": 0.5}
                ],
                company_info={
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "market_cap": 2500000000000
                },
                news_sentiment="Bullish",
                market_sentiment="Bullish",
                web_research=[
                    {"title": "Apple's Strong Growth", "content": "Positive analysis"},
                    {"title": "Market Outlook", "content": "Favorable conditions"}
                ]
            ),
            "MSFT": MarketInsights(
                symbol="MSFT",
                current_price=285.0,
                analyst_recommendations=[
                    {"recommendation": "Buy", "weight": 0.8},
                    {"recommendation": "Hold", "weight": 0.6},
                    {"recommendation": "Sell", "weight": 0.3}
                ],
                company_info={
                    "name": "Microsoft Corporation",
                    "sector": "Technology",
                    "market_cap": 2200000000000
                },
                news_sentiment="Neutral",
                market_sentiment="Neutral",
                web_research=[
                    {"title": "Microsoft's Cloud Growth", "content": "Mixed analysis"},
                    {"title": "Market Analysis", "content": "Stable outlook"}
                ]
            )
        }

    def test_get_market_insights(self):
        """Test getting market insights for a single symbol."""
        @patch('dcm.finance_agent_integration.Agent')
        async def async_test(mock_agent_class):
            # Set up mock agents
            mock_finance_agent = AsyncMock()
            mock_web_agent = AsyncMock()
            
            # Configure mock agent class to return our mock agents
            mock_agent_class.side_effect = [mock_web_agent, mock_finance_agent]
            
            # Set up mock methods
            mock_finance_agent.get_stock_data = AsyncMock(return_value={
                'current_price': 155.0,
                'fifty_day_avg': 150.0,
                'two_hundred_day_avg': 145.0
            })
            mock_finance_agent.get_analyst_recommendations = AsyncMock(return_value=[
                {"recommendation": "Strong Buy", "weight": 1.0}
            ])
            mock_finance_agent.get_company_info = AsyncMock(return_value={
                "name": "Apple Inc.",
                "sector": "Technology"
            })
            mock_finance_agent.get_company_news = AsyncMock(return_value=[
                {"title": "Positive News", "content": "Good performance"}
            ])
            mock_web_agent.search = AsyncMock(return_value=[
                {"title": "Market Analysis", "content": "Positive outlook"}
            ])
            
            # Create a new FinanceAgentIntegration instance to trigger agent creation
            finance_agent = FinanceAgentIntegration()
            
            # Get insights
            insights = await finance_agent.get_market_insights("AAPL")
            
            # Verify insights
            self.assertIsNotNone(insights)
            self.assertEqual(insights.symbol, "AAPL")
            self.assertEqual(insights.current_price, 155.0)
            self.assertEqual(len(insights.analyst_recommendations), 1)
            self.assertEqual(insights.news_sentiment, "Bullish")
            self.assertEqual(insights.market_sentiment, "Bullish")
            self.assertEqual(len(insights.web_research), 1)
            
        self.run_async(async_test())

    def test_get_portfolio_insights(self):
        """Test getting market insights for multiple symbols."""
        @patch('dcm.finance_agent_integration.Agent')
        async def async_test(mock_agent_class):
            # Set up mock agents
            mock_finance_agent = AsyncMock()
            mock_web_agent = AsyncMock()
            
            # Configure mock agent class to return our mock agents
            mock_agent_class.side_effect = [mock_web_agent, mock_finance_agent]
            
            # Set up mock methods
            mock_finance_agent.get_stock_data = AsyncMock(side_effect=[
                {'current_price': 155.0, 'fifty_day_avg': 150.0, 'two_hundred_day_avg': 145.0},
                {'current_price': 285.0, 'fifty_day_avg': 280.0, 'two_hundred_day_avg': 275.0}
            ])
            mock_finance_agent.get_analyst_recommendations = AsyncMock(side_effect=[
                [{"recommendation": "Strong Buy", "weight": 1.0}],
                [{"recommendation": "Buy", "weight": 0.8}]
            ])
            mock_finance_agent.get_company_info = AsyncMock(side_effect=[
                {"name": "Apple Inc.", "sector": "Technology"},
                {"name": "Microsoft Corporation", "sector": "Technology"}
            ])
            mock_finance_agent.get_company_news = AsyncMock(return_value=[
                {"title": "Positive News", "content": "Good performance"}
            ])
            mock_web_agent.search = AsyncMock(return_value=[
                {"title": "Market Analysis", "content": "Positive outlook"}
            ])
            
            # Create a new FinanceAgentIntegration instance to trigger agent creation
            finance_agent = FinanceAgentIntegration()
            
            # Get insights
            insights = await finance_agent.get_portfolio_insights(["AAPL", "MSFT"])
            
            # Verify insights
            self.assertEqual(len(insights), 2)
            self.assertIn("AAPL", insights)
            self.assertIn("MSFT", insights)
            self.assertEqual(insights["AAPL"].current_price, 155.0)
            self.assertEqual(insights["MSFT"].current_price, 285.0)
            
        self.run_async(async_test())

    def test_analyze_news_sentiment(self):
        """Test news sentiment analysis."""
        # Test bullish sentiment
        bullish_news = [
            {"title": "Strong Growth Expected", "content": "Positive outlook"},
            {"title": "Market Rally Continues", "content": "Bullish trend"}
        ]
        sentiment = self.finance_agent._analyze_news_sentiment(bullish_news)
        self.assertEqual(sentiment, "Bullish")
        
        # Test bearish sentiment
        bearish_news = [
            {"title": "Market Decline Expected", "content": "Negative outlook"},
            {"title": "Selling Pressure Mounts", "content": "Bearish trend"}
        ]
        sentiment = self.finance_agent._analyze_news_sentiment(bearish_news)
        self.assertEqual(sentiment, "Bearish")
        
        # Test neutral sentiment
        neutral_news = [
            {"title": "Market Stable", "content": "Mixed outlook"},
            {"title": "No Clear Direction", "content": "Uncertain trend"}
        ]
        sentiment = self.finance_agent._analyze_news_sentiment(neutral_news)
        self.assertEqual(sentiment, "Neutral")

    def test_analyze_market_sentiment(self):
        """Test market sentiment analysis."""
        # Test bullish sentiment
        bullish_data = {
            'fifty_day_avg': 150.0,
            'two_hundred_day_avg': 145.0
        }
        sentiment = self.finance_agent._analyze_market_sentiment(bullish_data)
        self.assertEqual(sentiment, "Bullish")
        
        # Test bearish sentiment
        bearish_data = {
            'fifty_day_avg': 145.0,
            'two_hundred_day_avg': 150.0
        }
        sentiment = self.finance_agent._analyze_market_sentiment(bearish_data)
        self.assertEqual(sentiment, "Bearish")
        
        # Test neutral sentiment
        neutral_data = {
            'fifty_day_avg': 150.0,
            'two_hundred_day_avg': 150.0
        }
        sentiment = self.finance_agent._analyze_market_sentiment(neutral_data)
        self.assertEqual(sentiment, "Neutral")

    def test_get_analyst_consensus(self):
        """Test analyst consensus calculation."""
        # Test strong buy consensus
        strong_buy_recs = [
            {"recommendation": "Strong Buy", "weight": 1.0},
            {"recommendation": "Buy", "weight": 0.8},
            {"recommendation": "Hold", "weight": 0.5}
        ]
        consensus, confidence = self.finance_agent.get_analyst_consensus(strong_buy_recs)
        self.assertEqual(consensus, "Strong Buy")
        self.assertGreater(confidence, 0.75)
        
        # Test sell consensus
        sell_recs = [
            {"recommendation": "Sell", "weight": 0.8},
            {"recommendation": "Strong Sell", "weight": 0.6},
            {"recommendation": "Hold", "weight": 0.3}
        ]
        consensus, confidence = self.finance_agent.get_analyst_consensus(sell_recs)
        self.assertEqual(consensus, "Sell")
        self.assertLess(confidence, 0.5)

class TestDCMEngineFinanceIntegration(AsyncTestCase):
    def setUp(self):
        """Set up test environment."""
        self.dcm_engine = DCMEngine()
        
        # Create test portfolio
        self.test_portfolio = Portfolio(
            portfolio_id="test_portfolio",
            total_value=54000.0,
            currency="USD",
            last_updated=datetime.now().isoformat(),
            holdings=[
                Holding(
                    symbol="AAPL",
                    name="Apple Inc.",
                    asset_type="Stock",
                    sector="Technology",
                    quantity=100,
                    current_price=150.0,
                    total_value=15000.0,
                    weight=0.4
                ),
                Holding(
                    symbol="MSFT",
                    name="Microsoft Corporation",
                    asset_type="Stock",
                    sector="Technology",
                    quantity=50,
                    current_price=280.0,
                    total_value=14000.0,
                    weight=0.3
                )
            ],
            asset_allocation={"Stocks": 1.0},
            sector_allocation={"Technology": 1.0},
            risk_metrics={
                "beta": 1.1,
                "volatility": 0.22,
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.25
            },
            performance_metrics={
                "daily_return": 0.02,
                "weekly_return": 0.05,
                "monthly_return": 0.08,
                "year_to_date_return": 0.15,
                "annualized_return": 0.20
            },
            constraints={
                "max_position_size": 0.4,
                "min_position_size": 0.1,
                "max_sector_exposure": 0.5
            }
        )

    def test_strategy_evaluation_with_insights(self):
        """Test strategy evaluation with market insights."""
        @patch('dcm.dcm_engine.MarketDataManager')
        @patch('dcm.dcm_engine.FinanceAgentIntegration')
        async def async_test(mock_finance_agent, mock_market_data):
            # Set up mocks
            mock_market_data.return_value.get_portfolio_market_data.return_value = {
                "AAPL": Mock(current_price=155.0, beta=1.2, volatility=0.25),
                "MSFT": Mock(current_price=285.0, beta=1.1, volatility=0.22)
            }
            
            mock_finance_agent.return_value.get_portfolio_insights.return_value = {
                "AAPL": Mock(
                    analyst_recommendations=[
                        {"recommendation": "Strong Buy", "weight": 1.0}
                    ],
                    news_sentiment="Bullish",
                    market_sentiment="Bullish"
                ),
                "MSFT": Mock(
                    analyst_recommendations=[
                        {"recommendation": "Buy", "weight": 0.8}
                    ],
                    news_sentiment="Neutral",
                    market_sentiment="Neutral"
                )
            }
            
            # Evaluate strategy
            score, recommendations = await self.dcm_engine.evaluate_strategy("risk_parity")
            
            # Verify results
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            self.assertIsInstance(recommendations, dict)
            self.assertAlmostEqual(sum(recommendations.values()), 0.0, places=4)
            
        self.run_async(async_test())

    def test_analyst_score_calculation(self):
        """Test analyst score calculation in strategy evaluation."""
        @patch('dcm.finance_agent_integration.Agent')
        async def async_test(mock_agent_class):
            # Set up mock agents
            mock_finance_agent = AsyncMock()
            mock_web_agent = AsyncMock()
            mock_agent_class.side_effect = [mock_web_agent, mock_finance_agent]
            
            # Create DCM engine instance
            dcm_engine = DCMEngine()
            
            # Test with valid recommendations
            market_insights = {
                "AAPL": MarketInsights(
                    symbol="AAPL",
                    current_price=150.0,
                    analyst_recommendations=[
                        {"recommendation": "Strong Buy", "weight": 1.0}
                    ],
                    company_info={},
                    news_sentiment="Bullish",
                    market_sentiment="Bullish",
                    web_research=[]
                )
            }
            
            score = await dcm_engine._calculate_analyst_score(market_insights)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
        self.run_async(async_test())

    def test_research_score_calculation(self):
        """Test research score calculation in strategy evaluation."""
        @patch('dcm.finance_agent_integration.Agent')
        async def async_test(mock_agent_class):
            # Set up mock agents
            mock_finance_agent = AsyncMock()
            mock_web_agent = AsyncMock()
            mock_agent_class.side_effect = [mock_web_agent, mock_finance_agent]
            
            # Create DCM engine instance
            dcm_engine = DCMEngine()
            
            # Test with valid web research
            market_insights = {
                "AAPL": MarketInsights(
                    symbol="AAPL",
                    current_price=150.0,
                    analyst_recommendations=[],
                    company_info={},
                    news_sentiment="Neutral",
                    market_sentiment="Neutral",
                    web_research=[
                        {"title": "Analysis", "content": "Very positive outlook for the company"}
                    ]
                )
            }
            
            score = await dcm_engine._calculate_research_score(market_insights)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
        self.run_async(async_test())

    def test_empty_portfolio_insights(self):
        """Test handling of empty portfolio insights."""
        @patch('dcm.dcm_engine.MarketDataManager')
        @patch('dcm.dcm_engine.FinanceAgentIntegration')
        async def async_test(mock_finance_agent, mock_market_data):
            # Set up mocks with empty data
            mock_market_data.return_value.get_portfolio_market_data.return_value = {}
            mock_finance_agent.return_value.get_portfolio_insights.return_value = {}
            
            # Test strategy evaluation with empty portfolio
            score, recommendations = await self.dcm_engine.evaluate_strategy("risk_parity")
            
            # Verify results
            self.assertEqual(score, 0.5)  # Should return neutral score for empty portfolio
            self.assertEqual(recommendations, {})  # Should return empty recommendations
            
        self.run_async(async_test())

    def test_missing_market_data(self):
        """Test handling of missing market data."""
        @patch('dcm.finance_agent_integration.Agent')
        async def async_test(mock_agent_class):
            # Set up mock agents
            mock_finance_agent = AsyncMock()
            mock_web_agent = AsyncMock()
            mock_agent_class.side_effect = [mock_web_agent, mock_finance_agent]
            
            # Create DCM engine instance
            dcm_engine = DCMEngine()
            dcm_engine.portfolio_manager.portfolio.holdings = [
                Holding(
                    symbol="AAPL",
                    name="Apple Inc.",
                    asset_type="Stock",
                    sector="Technology",
                    quantity=100,
                    current_price=150.0,
                    total_value=15000.0,
                    weight=1.0
                )
            ]
            
            # Mock get_market_insights to return None
            dcm_engine.finance_agent.get_market_insights = AsyncMock(return_value=None)
            
            # Evaluate strategy
            score, recommendations = await dcm_engine.evaluate_strategy(dcm_engine.portfolio_manager)
            
            # Verify missing data is handled gracefully
            self.assertEqual(score, 0.5, "Score should be neutral when data is missing")
            self.assertIn("AAPL", recommendations)
            self.assertEqual(recommendations["AAPL"], 0.0, "Should not recommend changes without data")
            
        self.run_async(async_test())

    def test_extreme_market_conditions(self):
        """Test handling of extreme market conditions."""
        @patch('dcm.finance_agent_integration.Agent')
        async def async_test(mock_agent_class):
            # Set up mock agents
            mock_finance_agent = AsyncMock()
            mock_web_agent = AsyncMock()
            mock_agent_class.side_effect = [mock_web_agent, mock_finance_agent]
            
            # Create DCM engine instance
            dcm_engine = DCMEngine()
            dcm_engine.portfolio_manager.portfolio.holdings = [
                Holding(
                    symbol="AAPL",
                    name="Apple Inc.",
                    asset_type="Stock",
                    sector="Technology",
                    quantity=100,
                    current_price=150.0,
                    total_value=15000.0,
                    weight=1.0
                )
            ]
            
            # Mock market insights with extreme negative conditions
            market_insights = {
                "AAPL": {
                    "symbol": "AAPL",
                    "current_price": 50.0,
                    "analyst_recommendations": [
                        {"recommendation": "Strong Sell", "weight": 1.0},
                        {"recommendation": "Sell", "weight": 1.0}
                    ],
                    "company_info": {
                        "name": "Apple Inc.",
                        "sector": "Technology"
                    },
                    "news_sentiment": "Bearish",
                    "market_sentiment": "Bearish",
                    "web_research": [
                        {"title": "Market Analysis", "content": "Extremely negative outlook"}
                    ]
                }
            }
            
            # Mock get_market_insights to return extreme negative insights
            dcm_engine.finance_agent.get_market_insights = AsyncMock(return_value=market_insights["AAPL"])
            
            # Mock get_analyst_consensus to return low score
            dcm_engine.finance_agent.get_analyst_consensus = AsyncMock(return_value=0.2)
            
            # Evaluate strategy
            score, recommendations = await dcm_engine.evaluate_strategy(dcm_engine.portfolio_manager)
            
            # Verify extreme conditions are handled appropriately
            self.assertLess(score, 0.3, "Score should be low in extreme negative conditions")
            self.assertIn("AAPL", recommendations)
            self.assertLess(recommendations["AAPL"], -0.1, "Should recommend reducing position")
            
        self.run_async(async_test())

    def test_api_errors(self):
        """Test handling of API errors during data fetching."""
        @patch('dcm.dcm_engine.MarketDataManager')
        @patch('dcm.dcm_engine.FinanceAgentIntegration')
        async def async_test(mock_finance_agent, mock_market_data):
            # Set up mocks to simulate API errors
            mock_market_data.return_value.get_portfolio_market_data.side_effect = Exception("API Error")
            mock_finance_agent.return_value.get_portfolio_insights.side_effect = Exception("API Error")
            
            try:
                # Test strategy evaluation with API errors
                score, recommendations = await self.dcm_engine.evaluate_strategy("risk_parity")
                
                # Verify graceful error handling
                self.assertEqual(score, 0.5)  # Should return neutral score on error
                self.assertEqual(recommendations, {})  # Should return empty recommendations
            except Exception as e:
                self.fail(f"Failed to handle API error gracefully: {str(e)}")
            
        self.run_async(async_test())

if __name__ == '__main__':
    unittest.main() 