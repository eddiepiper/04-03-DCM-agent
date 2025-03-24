import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dcm.dcm_engine import DCMEngine
from dcm.portfolio import PortfolioManager
from dcm.alerts import AlertManager, AlertType
from dcm.conditions import Condition, ConditionType

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        """Initialize the bot with token and required components."""
        self.token = token
        self.application = Application.builder().token(token).build()
        self.dcm_engine = DCMEngine()
        self.portfolio_manager = PortfolioManager()
        self.alert_manager = AlertManager()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio))
        self.application.add_handler(CommandHandler("risk", self.risk))
        self.application.add_handler(CommandHandler("performance", self.performance))
        self.application.add_handler(CommandHandler("recommendations", self.recommendations))
        self.application.add_handler(CommandHandler("rebalance", self.rebalance))
        self.application.add_handler(CommandHandler("alerts", self.alerts))
        self.application.add_handler(CommandHandler("strategies", self.strategies))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        keyboard = [
            [
                InlineKeyboardButton("View Portfolio", callback_data="portfolio"),
                InlineKeyboardButton("Risk Metrics", callback_data="risk")
            ],
            [
                InlineKeyboardButton("Performance", callback_data="performance"),
                InlineKeyboardButton("Recommendations", callback_data="recommendations")
            ],
            [
                InlineKeyboardButton("Rebalance", callback_data="rebalance"),
                InlineKeyboardButton("Alerts", callback_data="alerts")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f'Hi {user.first_name}! I am your SmartPortfolio AI assistant. '
            'I can help you manage and optimize your investment portfolio.\n\n'
            'Use the buttons below or /help to see available commands.',
            reply_markup=reply_markup
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/portfolio - View your current portfolio
/risk - View portfolio risk metrics
/performance - View portfolio performance
/recommendations - Get portfolio recommendations
/rebalance - Rebalance your portfolio
/alerts - Manage portfolio alerts
/status - Check system status

You can also use the interactive buttons for easier navigation.
        """
        await update.message.reply_text(help_text)

    async def portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current portfolio holdings."""
        try:
            portfolio = self.portfolio_manager.portfolio
            if not portfolio or not portfolio.holdings:
                await update.message.reply_text("No portfolio data available.")
                return

            message = self._format_portfolio_message(portfolio)
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error displaying portfolio: {str(e)}")
            await update.message.reply_text("Sorry, there was an error displaying your portfolio.")

    async def risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show portfolio risk metrics."""
        try:
            portfolio = self.portfolio_manager.portfolio
            if not portfolio or not portfolio.holdings:
                await update.message.reply_text("No portfolio data available.")
                return

            message = self._format_risk_metrics_message(portfolio)
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error displaying risk metrics: {str(e)}")
            await update.message.reply_text("Sorry, there was an error displaying risk metrics.")

    async def performance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show portfolio performance metrics."""
        try:
            portfolio = self.portfolio_manager.portfolio
            if not portfolio or not portfolio.holdings:
                await update.message.reply_text("No portfolio data available.")
                return

            message = self._format_performance_metrics_message(portfolio)
            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error displaying performance metrics: {str(e)}")
            await update.message.reply_text("Sorry, there was an error displaying performance metrics.")

    async def recommendations(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show portfolio recommendations."""
        try:
            score, recommendations = await self.dcm_engine.evaluate_strategy(self.portfolio_manager)
            if not recommendations:
                await update.message.reply_text("No recommendations available at this time.")
                return

            message = "🔄 Portfolio Recommendations:\n\n"
            message += f"Strategy Score: {score:.2f}\n\n"
            for symbol, weight_change in recommendations.items():
                direction = "Increase" if weight_change > 0 else "Decrease"
                message += (
                    f"• {symbol}: {direction} weight by {abs(weight_change)*100:.1f}%\n"
                )

            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            await update.message.reply_text("Sorry, there was an error generating recommendations.")

    async def rebalance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Rebalance the portfolio based on target weights."""
        try:
            score, recommendations = await self.dcm_engine.evaluate_strategy(self.portfolio_manager)
            if not recommendations:
                await update.message.reply_text("No rebalancing recommendations available at this time.")
                return

            # Convert recommendations to target weights
            current_weights = {symbol: holding.weight for symbol, holding in self.portfolio_manager.portfolio.holdings.items()}
            target_weights = {
                symbol: current_weights.get(symbol, 0.0) + weight_change
                for symbol, weight_change in recommendations.items()
            }

            # Calculate rebalancing trades
            trades = self.portfolio_manager.calculate_rebalancing_trades(target_weights)
            if not trades:
                await update.message.reply_text("No rebalancing trades needed at this time.")
                return

            # Show proposed trades
            message = "🔄 Proposed Rebalancing Trades:\n\n"
            total_cost = 0
            for trade in trades:
                direction = "Buy" if trade['quantity'] > 0 else "Sell"
                message += (
                    f"• {direction} {abs(trade['quantity'])} shares of {trade['symbol']}\n"
                    f"  Price: ${trade['price']:.2f}\n"
                    f"  Value: ${abs(trade['value']):.2f}\n"
                    f"  Weight Change: {(trade['new_weight'] - trade['old_weight'])*100:.1f}%\n\n"
                )
                total_cost += abs(trade['value'])

            message += f"\nTotal Trading Cost: ${total_cost:.2f}"

            # Add confirmation buttons
            keyboard = [
                [
                    InlineKeyboardButton("Confirm", callback_data="confirm_rebalance"),
                    InlineKeyboardButton("Cancel", callback_data="cancel_rebalance")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Store trades in context for later use
            context.user_data['pending_trades'] = trades

            await update.message.reply_text(message, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error calculating rebalancing trades: {str(e)}")
            await update.message.reply_text("Sorry, there was an error calculating rebalancing trades.")

    async def alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manage portfolio alerts."""
        keyboard = [
            [
                InlineKeyboardButton("Add Price Alert", callback_data="add_price_alert"),
                InlineKeyboardButton("Add Risk Alert", callback_data="add_risk_alert")
            ],
            [
                InlineKeyboardButton("Add Performance Alert", callback_data="add_performance_alert"),
                InlineKeyboardButton("View Active Alerts", callback_data="view_alerts")
            ],
            [
                InlineKeyboardButton("View Rebalancing History", callback_data="rebalance_history"),
                InlineKeyboardButton("View Rebalancing Costs", callback_data="rebalance_costs")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔔 Alert Management\n\n"
            "Choose an option below:",
            reply_markup=reply_markup
        )

    async def strategies(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show available strategies and their performance."""
        try:
            message = "📊 Available Strategies:\n\n"
            for name, strategy in self.dcm_engine.strategies.items():
                message += (
                    f"• {strategy.name}\n"
                    f"  Description: {strategy.description}\n"
                    f"  Confidence Score: {strategy.confidence_score:.2f}\n"
                    f"  Times Used: {strategy.times_used}\n"
                    f"  Last Performance: {strategy.last_performance:.2f}\n\n"
                )

            await update.message.reply_text(message)
        except Exception as e:
            logger.error(f"Error displaying strategies: {str(e)}")
            await update.message.reply_text("Sorry, there was an error displaying strategies.")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks."""
        query = update.callback_query
        await query.answer()

        if query.data == "portfolio":
            message = self._format_portfolio_message(self.portfolio_manager.portfolio)
            await query.message.reply_text(message)
        elif query.data == "risk":
            message = self._format_risk_metrics_message(self.portfolio_manager.portfolio)
            await query.message.reply_text(message)
        elif query.data == "performance":
            message = self._format_performance_metrics_message(self.portfolio_manager.portfolio)
            await query.message.reply_text(message)
        elif query.data == "recommendations":
            await self.recommendations(update, context)
        elif query.data == "rebalance":
            await self.rebalance(update, context)
        elif query.data == "alerts":
            await self.alerts(update, context)
        elif query.data == "confirm_rebalance":
            await self._execute_rebalance(update, context)
        elif query.data == "cancel_rebalance":
            await query.message.reply_text("Rebalancing cancelled.")
            context.user_data.pop('pending_trades', None)

    async def _execute_rebalance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Execute pending rebalancing trades."""
        query = update.callback_query
        trades = context.user_data.get('pending_trades')
        
        if not trades:
            await query.message.reply_text("No pending trades to execute.")
            return

        try:
            # Execute trades
            self.portfolio_manager.execute_trades(trades)
            
            # Record rebalancing
            self.alert_manager.record_rebalance(trades)
            
            await query.message.reply_text("✅ Rebalancing completed successfully!")
        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
            await query.message.reply_text("❌ Error executing trades. Please try again.")
        finally:
            context.user_data.pop('pending_trades', None)

    def _format_portfolio_message(self, portfolio) -> str:
        """Format portfolio information into a readable message."""
        message = "📊 Portfolio Holdings:\n\n"
        for symbol, holding in portfolio.holdings.items():
            message += (
                f"• {symbol} ({holding.name})\n"
                f"  Quantity: {holding.quantity}\n"
                f"  Current Price: ${holding.current_price:.2f}\n"
                f"  Total Value: ${holding.total_value:.2f}\n"
                f"  Weight: {holding.weight*100:.1f}%\n"
                f"  Sector: {holding.sector or 'N/A'}\n\n"
            )
        message += f"\nTotal Portfolio Value: ${portfolio.metrics['total_value']:,.2f}"
        return message

    def _format_risk_metrics_message(self, portfolio) -> str:
        """Format risk metrics into a readable message."""
        metrics = portfolio.metrics
        message = "📈 Risk Metrics:\n\n"
        message += f"• Volatility: {metrics['volatility']*100:.1f}%\n"
        message += f"• Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n"
        message += "\nSector Weights:\n"
        for sector, weight in metrics['sector_weights'].items():
            message += f"• {sector}: {weight*100:.1f}%\n"
        return message

    def _format_performance_metrics_message(self, portfolio) -> str:
        """Format performance metrics into a readable message."""
        metrics = portfolio.metrics
        message = "📊 Performance Metrics:\n\n"
        message += f"• Daily Return: {metrics['daily_return']*100:.2f}%\n"
        message += f"• Total Value: ${metrics['total_value']:,.2f}\n"
        return message

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages."""
        if not update.message or not update.message.text:
            await update.message.reply_text("Please send a valid command.")
            return

        command = update.message.text.split()[0].lower()
        if command == "/start":
            await self.start(update, context)
        elif command == "/help":
            await self.help(update, context)
        elif command == "/portfolio":
            await self.portfolio(update, context)
        elif command == "/risk":
            await self.risk(update, context)
        elif command == "/performance":
            await self.performance(update, context)
        elif command == "/recommendations":
            await self.recommendations(update, context)
        elif command == "/rebalance":
            await self.rebalance(update, context)
        elif command == "/alerts":
            await self.alerts(update, context)
        elif command == "/strategies":
            await self.strategies(update, context)
        else:
            await update.message.reply_text("Unknown command. Use /help to see available commands.")

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log errors caused by updates."""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.message:
            await update.message.reply_text(
                "Sorry, an error occurred while processing your request."
            )

    def run(self):
        """Start the bot."""
        self.application.run_polling()

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("No token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    bot = TelegramBot(token)
    bot.run()

if __name__ == '__main__':
    main() 