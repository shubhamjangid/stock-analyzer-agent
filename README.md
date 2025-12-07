# Stock Portfolio Evaluation AI Agent

A comprehensive Python-based AI agent for evaluating stock portfolios using LangChain, LangGraph, and OpenAI. The agent performs multi-dimensional analysis combining fundamental, technical, sentiment, and risk metrics to generate actionable investment verdicts.

## 🎯 Features

### Core Capabilities
- **Fundamental Analysis**: P/E ratio, P/S ratio, EPS, revenue, profitability metrics
- **Technical Analysis**: SMA 50/200, RSI, volume analysis, trend detection
- **Sentiment Analysis**: Real-time news fetching with sentiment scoring
- **Analyst Ratings**: Consensus ratings and price targets
- **Risk Assessment**: Volatility, beta, Sharpe ratio, value at risk
- **LLM-Powered Synthesis**: LLM generates detailed analysis and actionable recommendations

### Output Format
- **Verdict**: Clear BUY/HOLD/SELL recommendation
- **Summary Report**: Detailed markdown report with:
  - Executive summary
  - Valuation analysis
  - Technical analysis
  - Sentiment analysis
  - Risk assessment
  - Key catalysts
  - Recommendation justification

## 🛠 Architecture

### Workflow Nodes (LangGraph)
1. **Gather Data**: Collects all metrics from various sources
2. **Synthesize Analysis**: Prepares data for LLM processing
3. **Generate Verdict**: Uses a LLM to analyze and generate recommendations

## 🚀 Setup Instructions

### Step 1: Clone and Setup Project
### Step 2: Configure Environment Variables

Create a `.env` file in the project root:
Get the news API from (https://newsapi.org/);

```
OPENAI_API_KEY=API key here
NEWS_API_KEY=API key here
LANGSMITH_API_KEY=API key here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=stock-portfolio-evaluator
```

## 💻 Usage

### Basic Usage

#### Analyze Single or Multiple Stocks
```bash
# Analyze specific stocks
python main.py --tickers RELIANCE.NS TCS.NS
```

#### Save Report to File
```bash
# Save markdown report
python main.py --tickers RELIANCE.NS TCS.NS --output portfolio_report.md
```

**Note:** This project is provided as-is for educational and research purposes; Invest at your own risk.

**Happy analyzing!** 📈
