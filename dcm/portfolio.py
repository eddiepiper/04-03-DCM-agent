from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from decimal import Decimal
from datetime import datetime
from .holdings import Holding

@dataclass
class Portfolio:
    portfolio_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"))
    holdings: Dict[str, Holding] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        'total_value': Decimal('0'),
        'sector_weights': {},
        'daily_return': Decimal('0'),
        'volatility': Decimal('0'),
        'sharpe_ratio': Decimal('0'),
        'risk_metrics': {
            'beta': Decimal('0'),
            'alpha': Decimal('0'),
            'tracking_error': Decimal('0'),
            'information_ratio': Decimal('0')
        }
    })
    currency: str = 'USD'
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    constraints: Dict[str, float] = field(default_factory=lambda: {
        'max_position_size': 0.4,
        'min_position_size': 0.1,
        'max_sector_exposure': 0.5
    })

    def __post_init__(self):
        """Validate portfolio data after initialization."""
        # Convert holdings to dictionary if needed
        if not isinstance(self.holdings, dict):
            if isinstance(self.holdings, (list, tuple)):
                self.holdings = {h.symbol: h for h in self.holdings if isinstance(h, Holding)}
            else:
                self.holdings = {}

        # Ensure all holdings have valid weights
        if self.holdings:
            self.calculate_metrics()

    def add_holding(self, holding: Holding) -> None:
        """Add a holding to the portfolio."""
        if holding is None:
            raise ValueError("Cannot add None holding")
        if not isinstance(holding, Holding):
            raise ValueError("Must provide a valid Holding object")
        if holding.symbol in self.holdings:
            raise ValueError(f"Holding {holding.symbol} already exists in portfolio")
        
        self.holdings[holding.symbol] = holding
        self.last_updated = datetime.now().isoformat()
        self.calculate_metrics()

    def remove_holding(self, symbol: str) -> None:
        """Remove a holding from the portfolio."""
        if not isinstance(symbol, str):
            raise ValueError("Symbol must be a string")
        if symbol not in self.holdings:
            raise KeyError(f"Holding {symbol} not found in portfolio")
        
        del self.holdings[symbol]
        self.last_updated = datetime.now().isoformat()
        self.calculate_metrics()

    def update_prices(self, prices: Dict[str, Union[Decimal, float]]) -> None:
        """Update prices for multiple holdings."""
        if not isinstance(prices, dict):
            raise ValueError("Prices must be provided as a dictionary")
        
        for symbol, price in prices.items():
            if symbol in self.holdings:
                if not isinstance(price, Decimal):
                    try:
                        price = Decimal(str(price))
                    except (TypeError, ValueError, ArithmeticError):
                        raise ValueError(f"Invalid price value for {symbol}: {price}")
                if price <= 0:
                    raise ValueError(f"Invalid price for {symbol}: {price}")
                self.holdings[symbol].update_price(price)
        
        self.last_updated = datetime.now().isoformat()
        self.calculate_metrics()

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate portfolio metrics."""
        if not self.holdings:
            self.metrics = {
                'total_value': Decimal('0'),
                'sector_weights': {},
                'daily_return': Decimal('0'),
                'volatility': Decimal('0'),
                'sharpe_ratio': Decimal('0'),
                'risk_metrics': {
                    'beta': Decimal('0'),
                    'alpha': Decimal('0'),
                    'tracking_error': Decimal('0'),
                    'information_ratio': Decimal('0')
                }
            }
            return self.metrics

        # Calculate total value
        total_value = sum(holding.total_value for holding in self.holdings.values())
        self.metrics['total_value'] = total_value

        # Calculate holding weights and update them
        if total_value > 0:
            for holding in self.holdings.values():
                weight = holding.total_value / total_value
                holding.update_weight(float(weight))

        # Calculate sector weights
        sector_weights = {}
        for holding in self.holdings.values():
            if holding.sector:
                sector_value = holding.total_value
                if total_value > 0:
                    weight = sector_value / total_value
                    sector_weights[holding.sector] = sector_weights.get(holding.sector, Decimal('0')) + weight

        # Update metrics
        self.metrics.update({
            'sector_weights': sector_weights,
            'daily_return': self.metrics.get('daily_return', Decimal('0')),
            'volatility': self.metrics.get('volatility', Decimal('0')),
            'sharpe_ratio': self.metrics.get('sharpe_ratio', Decimal('0')),
            'risk_metrics': self.metrics.get('risk_metrics', {
                'beta': Decimal('0'),
                'alpha': Decimal('0'),
                'tracking_error': Decimal('0'),
                'information_ratio': Decimal('0')
            })
        })

        return self.metrics

    def to_dict(self) -> dict:
        """Convert portfolio to dictionary format."""
        return {
            'portfolio_id': self.portfolio_id,
            'holdings': {
                symbol: holding.to_dict()
                for symbol, holding in self.holdings.items()
            },
            'metrics': {
                k: str(v) if isinstance(v, Decimal) else v
                for k, v in self.metrics.items()
            },
            'currency': self.currency,
            'last_updated': self.last_updated,
            'constraints': self.constraints
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Portfolio':
        """Create portfolio from dictionary format."""
        # Convert holdings data to Holding objects
        holdings = {}
        for symbol, holding_data in data.get('holdings', {}).items():
            try:
                holdings[symbol] = Holding.from_dict(holding_data)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to load holding {symbol}: {str(e)}")
                continue

        # Convert metrics values to Decimal where appropriate
        metrics = data.get('metrics', {})
        for key in ['total_value', 'daily_return', 'volatility', 'sharpe_ratio']:
            if key in metrics and isinstance(metrics[key], str):
                try:
                    metrics[key] = Decimal(metrics[key])
                except (TypeError, ValueError, ArithmeticError):
                    metrics[key] = Decimal('0')

        # Convert risk metrics to Decimal
        risk_metrics = metrics.get('risk_metrics', {})
        for key in ['beta', 'alpha', 'tracking_error', 'information_ratio']:
            if key in risk_metrics and isinstance(risk_metrics[key], str):
                try:
                    risk_metrics[key] = Decimal(risk_metrics[key])
                except (TypeError, ValueError, ArithmeticError):
                    risk_metrics[key] = Decimal('0')

        return cls(
            portfolio_id=data.get('portfolio_id', datetime.now().strftime("%Y%m%d%H%M%S")),
            holdings=holdings,
            metrics=metrics,
            currency=data.get('currency', 'USD'),
            last_updated=data.get('last_updated', datetime.now().isoformat()),
            constraints=data.get('constraints', {
                'max_position_size': 0.4,
                'min_position_size': 0.1,
                'max_sector_exposure': 0.5
            })
        )

class PortfolioManager:
    def __init__(self, portfolio: Optional[Portfolio] = None):
        """Initialize portfolio manager."""
        self.portfolio = portfolio or Portfolio()

    def add_holding(self, holding: Holding) -> None:
        """Add a holding to the portfolio."""
        self.portfolio.add_holding(holding)

    def remove_holding(self, symbol: str) -> None:
        """Remove a holding from the portfolio."""
        self.portfolio.remove_holding(symbol)

    def update_prices(self, prices: Dict[str, Union[Decimal, float]]) -> None:
        """Update prices for multiple holdings."""
        self.portfolio.update_prices(prices)

    def calculate_rebalancing_trades(self, target_weights: Dict[str, float]) -> List[Dict]:
        """Calculate trades needed to achieve target weights."""
        if not self.portfolio.holdings:
            return []

        trades = []
        total_value = self.portfolio.metrics['total_value']
        if total_value <= 0:
            return []

        # Validate target weights
        target_weight_sum = sum(Decimal(str(w)) for w in target_weights.values())
        if abs(target_weight_sum - Decimal('1.0')) > Decimal('0.0001'):
            raise ValueError("Target weights must sum to 1.0")

        # Calculate current weights and validate target weights
        current_weights = {
            symbol: float(holding.total_value / total_value)
            for symbol, holding in self.portfolio.holdings.items()
        }

        # Calculate trades for each holding
        for symbol, target_weight in target_weights.items():
            if symbol not in self.portfolio.holdings:
                continue

            holding = self.portfolio.holdings[symbol]
            current_weight = current_weights[symbol]
            target_weight_decimal = Decimal(str(target_weight))
            weight_diff = target_weight_decimal - Decimal(str(current_weight))

            # Only generate trades for significant weight differences (0.5% threshold)
            if abs(weight_diff) >= Decimal('0.005'):
                value_change = weight_diff * total_value
                price = holding.current_price
                if price > 0:
                    quantity = int(value_change / price)
                    if quantity != 0:
                        trades.append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'price': float(price),
                            'value': float(value_change),
                            'old_weight': current_weight,
                            'new_weight': float(target_weight_decimal)
                        })

        return trades

    def execute_rebalancing_trades(self, trades: List[Dict]) -> bool:
        """Execute rebalancing trades."""
        if not trades:
            return True

        try:
            # Validate trades before execution
            for trade in trades:
                symbol = trade['symbol']
                if symbol not in self.portfolio.holdings:
                    raise ValueError(f"Invalid trade: {symbol} not in portfolio")
                
                holding = self.portfolio.holdings[symbol]
                new_quantity = holding.quantity + trade['quantity']
                if new_quantity < 0:
                    raise ValueError(f"Invalid trade: {symbol} would result in negative quantity")

            # Execute trades
            for trade in trades:
                symbol = trade['symbol']
                holding = self.portfolio.holdings[symbol]
                
                # Update quantity
                new_quantity = holding.quantity + trade['quantity']
                if new_quantity == 0:
                    self.remove_holding(symbol)
                else:
                    holding.quantity = new_quantity
                    holding.update_weight(float(trade['new_weight']))

            # Recalculate portfolio metrics
            self.portfolio.calculate_metrics()
            return True

        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
            return False

    def to_dict(self) -> dict:
        """Convert portfolio manager to dictionary format."""
        return {
            'portfolio': self.portfolio.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PortfolioManager':
        """Create portfolio manager from dictionary format."""
        portfolio = Portfolio.from_dict(data.get('portfolio', {}))
        return cls(portfolio=portfolio) 