import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from telegram import Update, Message, Chat, User, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes
from interface.telegram_bot import TelegramBot
from dcm.portfolio import Portfolio
from dcm.holdings import Holding
from decimal import Decimal

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
async def telegram_bot():
    """Create a mock telegram bot instance."""
    bot = TelegramBot("test_token")
    bot.application = AsyncMock()
    bot.dcm_engine = AsyncMock()
    bot.portfolio_manager = MagicMock()
    bot.alert_manager = MagicMock()
    return bot

@pytest.fixture
def mock_update():
    """Create a mock update object with async reply_text."""
    update = MagicMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    update.message.chat = MagicMock(spec=Chat)
    update.message.chat.id = 123456
    update.effective_user = MagicMock(spec=User)
    update.effective_user.first_name = "Test User"
    update.effective_user.id = 123456
    update.callback_query = AsyncMock()
    update.callback_query.message = AsyncMock(spec=Message)
    return update

@pytest.fixture
def mock_context():
    """Create a mock context object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.fixture
def sample_portfolio():
    """Create a sample portfolio for testing."""
    holdings = {
        "AAPL": Holding(
            symbol="AAPL",
            name="Apple Inc.",
            quantity=100,
            current_price=Decimal("150.0"),
            sector="Technology",
            weight=Decimal("0.3")
        ),
        "MSFT": Holding(
            symbol="MSFT",
            name="Microsoft Corp.",
            quantity=50,
            current_price=Decimal("300.0"),
            sector="Technology",
            weight=Decimal("0.3")
        ),
        "VTI": Holding(
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            quantity=200,
            current_price=Decimal("220.0"),
            sector="ETF",
            weight=Decimal("0.2")
        ),
        "BND": Holding(
            symbol="BND",
            name="Vanguard Total Bond Market ETF",
            quantity=100,
            current_price=Decimal("85.0"),
            sector="Bond",
            weight=Decimal("0.2")
        )
    }
    portfolio = Portfolio(holdings=holdings)
    portfolio.metrics = {
        'total_value': Decimal("69000.0"),
        'daily_return': Decimal("0.015"),
        'volatility': Decimal("0.12"),
        'sharpe_ratio': Decimal("1.5"),
        'sector_weights': {
            'Technology': Decimal("0.6"),
            'ETF': Decimal("0.2"),
            'Bond': Decimal("0.2")
        }
    }
    return portfolio

@pytest.mark.asyncio
async def test_start_command(telegram_bot, mock_update, mock_context):
    """Test the /start command handler."""
    await telegram_bot.start(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args, kwargs = mock_update.message.reply_text.call_args
    assert "Hi Test User!" in args[0]
    assert isinstance(kwargs['reply_markup'], InlineKeyboardMarkup)

@pytest.mark.asyncio
async def test_help_command(telegram_bot, mock_update, mock_context):
    """Test the /help command handler."""
    await telegram_bot.help(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Available commands" in args[0]

@pytest.mark.asyncio
async def test_portfolio_command(telegram_bot, mock_update, mock_context, sample_portfolio):
    """Test the /portfolio command handler."""
    telegram_bot.portfolio_manager.portfolio = sample_portfolio
    
    await telegram_bot.portfolio(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Portfolio Holdings" in args[0]
    assert "AAPL" in args[0]
    assert "MSFT" in args[0]

@pytest.mark.asyncio
async def test_risk_metrics_command(telegram_bot, mock_update, mock_context, sample_portfolio):
    """Test /risk command handling."""
    telegram_bot.portfolio_manager.portfolio = sample_portfolio
    
    await telegram_bot.risk(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Risk Metrics" in args[0]
    assert "Volatility" in args[0]
    assert "Sharpe Ratio" in args[0]

@pytest.mark.asyncio
async def test_performance_command(telegram_bot, mock_update, mock_context, sample_portfolio):
    """Test /performance command handling."""
    telegram_bot.portfolio_manager.portfolio = sample_portfolio
    
    await telegram_bot.performance(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Performance Metrics" in args[0]
    assert "Daily Return" in args[0]

@pytest.mark.asyncio
async def test_recommendations_command(telegram_bot, mock_update, mock_context):
    """Test /recommendations command handling."""
    telegram_bot.dcm_engine.evaluate_strategy = AsyncMock(return_value=(
        0.85,
        {
            "AAPL": 0.1,
            "MSFT": -0.05,
            "VTI": 0.02
        }
    ))
    
    await telegram_bot.recommendations(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Portfolio Recommendations" in args[0]
    assert "Strategy Score" in args[0]

@pytest.mark.asyncio
async def test_rebalance_command(telegram_bot, mock_update, mock_context, sample_portfolio):
    """Test the /rebalance command handler."""
    telegram_bot.portfolio_manager.portfolio = sample_portfolio
    telegram_bot.dcm_engine.evaluate_strategy = AsyncMock(return_value=(
        0.85,
        {
            "AAPL": 0.1,
            "MSFT": -0.05,
            "VTI": 0.02
        }
    ))
    telegram_bot.portfolio_manager.calculate_rebalancing_trades.return_value = [
        {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "value": 1500.0,
            "old_weight": 0.3,
            "new_weight": 0.4
        }
    ]
    
    await telegram_bot.rebalance(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Proposed Rebalancing Trades" in args[0]

@pytest.mark.asyncio
async def test_alerts_command(telegram_bot, mock_update, mock_context):
    """Test the /alerts command handler."""
    await telegram_bot.alerts(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args, kwargs = mock_update.message.reply_text.call_args
    assert "Alert Management" in args[0]
    assert isinstance(kwargs['reply_markup'], InlineKeyboardMarkup)

@pytest.mark.asyncio
async def test_strategies_command(telegram_bot, mock_update, mock_context):
    """Test the /strategies command handler."""
    telegram_bot.dcm_engine.strategies = {
        "risk_parity": MagicMock(
            name="Risk Parity",
            description="Equal risk contribution strategy",
            confidence_score=0.85,
            times_used=10,
            last_performance=0.12
        )
    }
    
    await telegram_bot.strategies(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Available Strategies" in args[0]

@pytest.mark.asyncio
async def test_error_handler(telegram_bot, mock_update, mock_context):
    """Test the error handler."""
    mock_context.error = Exception("Test error")
    
    await telegram_bot.error(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "error occurred" in args[0]

@pytest.mark.asyncio
async def test_unknown_command(telegram_bot, mock_update, mock_context):
    """Test handling of unknown commands."""
    mock_update.message.text = "/invalid"
    await telegram_bot.handle_message(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Unknown command" in args[0]

@pytest.mark.asyncio
async def test_button_callback(telegram_bot, mock_update, mock_context, sample_portfolio):
    """Test button callback handling."""
    mock_update.callback_query.data = "portfolio"
    telegram_bot.portfolio_manager.portfolio = sample_portfolio
    
    await telegram_bot.button_callback(mock_update, mock_context)
    
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.message.reply_text.assert_called_once()
    args = mock_update.callback_query.message.reply_text.call_args[0]
    assert "Portfolio Holdings" in args[0]

@pytest.mark.asyncio
async def test_message_formatting(telegram_bot, sample_portfolio):
    """Test message formatting functions."""
    # Test portfolio formatting
    portfolio_text = telegram_bot._format_portfolio_message(sample_portfolio)
    assert "Portfolio Holdings" in portfolio_text
    assert "AAPL" in portfolio_text
    assert "MSFT" in portfolio_text
    
    # Test risk metrics formatting
    risk_text = telegram_bot._format_risk_metrics_message(sample_portfolio)
    assert "Risk Metrics" in risk_text
    assert "Volatility" in risk_text
    assert "Sharpe Ratio" in risk_text
    
    # Test performance metrics formatting
    perf_text = telegram_bot._format_performance_metrics_message(sample_portfolio)
    assert "Performance Metrics" in perf_text
    assert "Daily Return" in perf_text
    assert "Total Value" in perf_text

@pytest.mark.asyncio
async def test_command_validation(telegram_bot, mock_update, mock_context):
    """Test command validation."""
    # Test invalid command
    mock_update.message.text = "/invalid"
    await telegram_bot.handle_message(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    args = mock_update.message.reply_text.call_args[0]
    assert "Unknown command" in args[0] 