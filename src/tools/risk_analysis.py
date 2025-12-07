import logging
import yfinance as yf
from typing import Dict, Any
import numpy as np

from src.config import Config

logger = logging.getLogger(__name__)

def calculate_risk_metrics(ticker: str, period_days: int = 252) -> Dict[str, Any]:
    """
    Calculate risk metrics including volatility and beta.
    
    Args:
        ticker: Stock ticker symbol
        period_days: Number of days for analysis (252 = 1 year)
    
    Returns:
        Dictionary containing risk metrics
    """
    try:
        logger.info(f"Calculating risk metrics for {ticker}...")
        
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{period_days}d")
        
        if hist.empty or len(hist) < 2:
            raise ValueError(f"Insufficient data for {ticker}")
        
        # Calculate daily returns
        daily_returns = hist["Close"].pct_change().dropna()
        
        if daily_returns.empty:
            raise ValueError(f"Could not calculate returns for {ticker}")
        
        # Volatility (annualized)
        volatility = daily_returns.std() * np.sqrt(252)
        
        # Beta (vs benchmark index)
        benchmark = yf.Ticker(Config.BENCHMARK_INDEX)
        benchmark_hist = benchmark.history(period=f"{period_days}d")
        benchmark_returns = benchmark_hist["Close"].pct_change().dropna()
        
        beta = None
        if len(benchmark_returns) > 0:
            # Align dates
            common_dates = daily_returns.index.intersection(benchmark_returns.index)
            if len(common_dates) > 0:
                stock_ret = daily_returns[common_dates]
                market_ret = benchmark_returns[common_dates]
                covariance = np.cov(stock_ret, market_ret)[0][1]
                market_variance = np.var(market_ret)
                beta = covariance / market_variance if market_variance != 0 else None
        
        # Sharpe Ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02
        excess_returns = daily_returns.mean() * 252 - risk_free_rate
        sharpe_ratio = excess_returns / volatility if volatility != 0 else 0
        
        # Value at Risk (95% confidence)
        var_95 = daily_returns.quantile(0.05)
        
        risk_metrics = {
            "ticker": ticker,
            "volatility_annual": round(volatility, 4),
            "beta": round(beta, 2) if beta else None,
            "sharpe_ratio": round(sharpe_ratio, 2),
            "var_95": round(var_95, 4),
            "max_drawdown": round((daily_returns.cumsum().min()), 4),
            "volatility_assessment": get_volatility_assessment(volatility),
        }
        
        logger.info(f"Risk metrics calculation completed for {ticker}")
        return risk_metrics
    
    except Exception as e:
        logger.error(f"Error calculating risk metrics for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "error_type": "risk_calculation_failed"
        }


def get_volatility_assessment(volatility: float) -> str:
    """Assess volatility level"""
    if volatility < 0.2:
        return "Low Volatility"
    elif volatility < 0.35:
        return "Moderate Volatility"
    else:
        return "High Volatility"