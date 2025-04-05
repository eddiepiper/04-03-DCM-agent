# 🧠 SmartPortfolio AI – A MCP - Driven Rebalancing Agent System

SmartPortfolio AI is a modular, intelligent AI agent system designed to manage and optimize investment portfolios using **Model Context Protocol (MCP)**.

This project showcases how an AI agent can **evaluate, evolve, and recommend investment strategies** dynamically, based on performance and policy constraints — while separating the **decision logic** (MCP) from **execution workflows**.

---

## 🎯 Project Purpose

To demonstrate **Model Context Protocol (MCP)** in action — where the AI system evolves internal capabilities (e.g., portfolio strategies) and adapts its behavior to changing conditions, user feedback, and performance results.

---

## 🧠 Core Concepts

- **Model Context Protocol (MCP):** Tracks and manages evolving capabilities (investment strategies), scoring them based on past outcomes and adapting over time.
- **Modular AI Agent Design:** Each agent performs a dedicated role in the portfolio rebalancing process.
- **Separation of Concerns:** MCP recommends the best strategy, but a lightweight controller orchestrates the execution.

---

## 🧱 Agent Architecture

### 🔁 System Flow

```text
User (Telegram)
     ↓
Conversational Agent
     ↓
→→→→→→→→→→→→→→→→→→
↓                 ↓
Calls Execution Controller    ←──────────────
(a lightweight orchestrator)                  |
     ↓                                         |
MCP Engine ⇄ Capability Manager Layer         |
     ↓                                         |
Sends recommendation:                         |
- Use "Risk Parity"                           |
- Deactivate "Equal Weight"                  ↑
     ↓                                        ↑
Execution Controller calls agents as needed:  ↑
- Portfolio Analysis                          ↑
- Bank Policy                                  ↑
- Rebalance Strategy                           ↑
- Trade Execution                              ↑
→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→→
```

---

## 👥 Agents in the System

| Agent | Role |
|-------|------|
| **Conversational Interface Agent** | Handles Telegram input/output and user interactions |
| **MCP Engine** | Recommends strategies based on historical performance & context |
| **Portfolio Analysis Agent** | Assesses portfolio structure and current asset distribution |
| **Bank Policy Agent** | Applies internal or regulatory constraints on strategies |
| **Rebalance Strategy Agent** | Executes chosen portfolio rebalancing logic |
| **Trade Execution Agent** | Simulates or dispatches trade instructions |

---

## 📂 Directory Structure

```bash
SmartPortfolioMCP/
├── agents/
│   ├── analysis_agent.py
│   ├── rebalance_agent.py
│   ├── bank_policy_agent.py
│   ├── trade_execution_agent.py
│   └── MCP_engine.py          # The brain – recommends & evolves strategy capabilities
│
├── MCP/
│   ├── capabilities.json      # Tracks all strategies, scores, and metadata
│   └── performance_log.json   # Logs real-world or simulated performance results
│
├── interface/
│   └── telegram_bot.py        # Telegram Conversational Agent
│
├── controller/
│   └── execution_controller.py # Orchestrates agents based on MCP output
│
├── data/
│   └── sample_portfolio.json
│
├── run.py                     # Main entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

1. User interacts via Telegram.
2. Conversational Agent parses the query and forwards to the Execution Controller.
3. The Controller calls the MCP Engine to get a recommended strategy.
4. The MCP Engine evaluates current capability states (via `capabilities.json`).
5. Based on recommendation, the Controller:
   - Calls Portfolio Analysis
   - Applies Bank Policies
   - Executes Strategy
   - Triggers Trade Execution
6. Results are fed back to the MCP Engine for scoring and capability adjustment.

---

## 🧪 Example Strategies (Capabilities)

- `equal_weight`
- `risk_parity`
- `volatility_weighted`
- `dividend_focus`

Each strategy has:
```json
{
  "confidence_score": 0.74,
  "times_used": 3,
  "last_performance": 0.021,
  "active": true
}
```

---

## ✅ Getting Started

```bash
git clone https://github.com/yourusername/SmartPortfolioMCP.git
cd SmartPortfolioMCP
pip install -r requirements.txt
python run.py
```

To start the Telegram bot, configure your bot token in `interface/telegram_bot.py` and run it.

---

## 🚀 Future Enhancements

- Real-time price feed via Alpha Vantage or Yahoo Finance
- Backtesting engine
- Real trade execution via Alpaca API
- Visual dashboard (Streamlit/Gradio)
- Capability graph visualization

---

## 🧠 Designed With MCP in Mind

This project keeps the **MCP Engine pure** — responsible only for **capability evaluation, evolution, and strategy recommendation**, not system control.

The **execution controller handles orchestration**, maintaining modularity and showcasing how **agent-based AI systems can be both adaptive and interpretable**.

---

# Dynamic Capital Management (MCP) Project

A sophisticated portfolio management system with AI-powered analysis and Telegram bot interface.

## Features

- **Portfolio Management**
  - Track holdings and positions
  - Calculate portfolio metrics
  - Monitor performance and risk metrics
  - Rebalancing suggestions

- **Market Analysis**
  - Real-time market data integration
  - Sentiment analysis
  - Technical indicators
  - News integration

- **Telegram Bot Interface**
  - View portfolio status
  - Get real-time alerts
  - Execute trades
  - Receive recommendations

## Project Structure

```
MCP-project/
├── agents/                 # AI agents for different analysis tasks
├── MCP/                   # Core MCP functionality
│   ├── alerts.py         # Portfolio alerts system
│   ├── conditions.py     # Alert conditions
│   ├── MCP_engine.py     # Main engine
│   ├── holdings.py       # Portfolio holdings
│   ├── market_data.py    # Market data integration
│   └── portfolio.py      # Portfolio management
├── interface/            # User interfaces
│   └── telegram_bot.py   # Telegram bot implementation
├── tests/               # Test suite
│   ├── agents/         # Agent tests
│   ├── MCP/           # Core functionality tests
│   └── interface/     # Interface tests
├── .env.example        # Example environment variables
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd MCP-project
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and configure your environment variables:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

## Running Tests

Run all tests:
```bash
python -m pytest
```

Run specific test files:
```bash
python -m pytest tests/interface/test_telegram_bot.py
```

## Usage

1. Start the Telegram bot:
```bash
python -m interface.telegram_bot
```

2. Available commands in Telegram:
- `/start` - Start the bot
- `/help` - Show help message
- `/portfolio` - View current portfolio
- `/risk` - View risk metrics
- `/performance` - View performance metrics
- `/recommendations` - Get recommendations
- `/rebalance` - Rebalance portfolio
- `/alerts` - Manage alerts
- `/strategies` - View available strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Financial data providers
- Open-source libraries
- Contributors and maintainers

---
