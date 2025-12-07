import logging
from typing import TypedDict, Optional, List, Dict, Any
import json
from datetime import datetime


from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import Config

from src.prompts import system_prompt, user_prompt

from src.tools.fundamental_analysis import perform_fundamental_analysis
from src.tools.technical_analysis import get_technical_indicators  
from src.tools.news_analysis import fetch_realtime_news
from src.tools.analyst_rating import check_analyst_ratings
from src.tools.risk_analysis import calculate_risk_metrics

logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AnalysisState(TypedDict):
    """State management for stock analysis workflow"""
    ticker: str
    fundamentals: Optional[Dict[str, Any]]
    technical: Optional[Dict[str, Any]]
    news: Optional[Dict[str, Any]]
    analyst_ratings: Optional[Dict[str, Any]]
    risk_metrics: Optional[Dict[str, Any]]
    synthesis: Optional[str]
    verdict: Optional[str]
    report: Optional[str]
    errors: List[str]
    
    
# ============================================================================
# LLM Structured Output Definition
# ============================================================================

class StockDecision(BaseModel):
    verdict: str = Field(
        description='Final decision, one of: "BUY", "HOLD", "SELL".'
    )
    report: str = Field(
        description="Detailed markdown report justifying the verdict."
    )


# ============================================================================
# WORKFLOW NODES
# ============================================================================

def node_gather_data(state: AnalysisState) -> AnalysisState:
    """
    Step 1: Gather all available data for the stock.
    """
    ticker = state["ticker"]
    logger.info(f"\nSTEP 1: Gathering data for {ticker}...")
    
    try:
        state["fundamentals"] = perform_fundamental_analysis(ticker)
        logger.info(f"Fundamentals gathered")
    except Exception as e:
        logger.error(f"Fundamental analysis failed: {e}")
        state["errors"].append(f"Fundamental analysis: {e}")
    
    try:
        state["technical"] = get_technical_indicators(ticker)
        logger.info(f"Technical indicators calculated")
    except Exception as e:
        logger.error(f"Technical analysis failed: {e}")
        state["errors"].append(f"Technical analysis: {e}")
    
    try:
        state["news"] = fetch_realtime_news(ticker)
        logger.info(f"News fetched and analyzed")
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        state["errors"].append(f"News fetch: {e}")
    
    try:
        state["analyst_ratings"] = check_analyst_ratings(ticker)
        logger.info(f"Analyst ratings retrieved")
    except Exception as e:
        logger.error(f"Analyst ratings fetch failed: {e}")
        state["errors"].append(f"Analyst ratings: {e}")
    
    try:
        state["risk_metrics"] = calculate_risk_metrics(ticker)
        logger.info(f"Risk metrics calculated")
    except Exception as e:
        logger.error(f"Risk metrics calculation failed: {e}")
        state["errors"].append(f"Risk metrics: {e}")
    
    return state


def node_synthesize_analysis(state: AnalysisState) -> AnalysisState:
    """
    Step 2: Synthesize all gathered data into a holistic view.
    """
    logger.info(f"\nSTEP 2: Synthesizing analysis...")
    
    ticker = state["ticker"]
    
    # Prepare data summary for LLM
    data_summary = f"""
    Stock Analysis Summary for {ticker}
    
    Fundamentals:
    {json.dumps(state.get('fundamentals', {}), indent=2, default=str)}
    
    Technical Indicators:
    {json.dumps(state.get('technical', {}), indent=2, default=str)}
    
    News & Sentiment:
    {json.dumps(state.get('news', {}), indent=2, default=str)}
    
    Analyst Ratings:
    {json.dumps(state.get('analyst_ratings', {}), indent=2, default=str)}
    
    Risk Metrics:
    {json.dumps(state.get('risk_metrics', {}), indent=2, default=str)}
    """
    
    state["synthesis"] = data_summary
    logger.info("Data synthesis completed")
    return state


def node_generate_verdict_and_report(state: AnalysisState) -> AnalysisState:
    """
    Step 3: Generate final verdict and detailed report using LLM.
    """
    logger.info(f"\nSTEP 3: Generating verdict and report...")
    
    ticker = state["ticker"]
    
    try:
        # initialize LLM
        llm = ChatOpenAI(
            model_name=Config.OPENAI_MODEL,
            temperature=0.3,
            openai_api_key=Config.OPENAI_API_KEY,
        )
        
        # structured output setup
        structured_llm = llm.with_structured_output(StockDecision)

        # prompts for the analysis
        sys_msg = SystemMessage(content=system_prompt())
        usr_msg = HumanMessage(content=user_prompt(ticker, state))

        # invoke LLM
        result: StockDecision = structured_llm.invoke([sys_msg, usr_msg])

        verdict_raw = (result.verdict or "").upper().strip()
        if verdict_raw not in {"BUY", "HOLD", "SELL"}:
            # Fallback normalization
            if "BUY" in verdict_raw:
                verdict = "BUY"
            elif "SELL" in verdict_raw:
                verdict = "SELL"
            else:
                verdict = "HOLD"
        else:
            verdict = verdict_raw

        state["verdict"] = verdict
        state["report"] = result.report
        logger.info(f"Verdict generated: {verdict}")
        return state
    
    except Exception as e:
        logger.error(f"Error generating verdict: {e}")
        state["errors"].append(f"Verdict generation: {e}")
        state["verdict"] = ""
        state["report"] = f"Error generating report: {e}"
        return state


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def build_analysis_graph():
    """
    Construct the LangGraph workflow for stock analysis.
    """
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("gather_data", node_gather_data)
    workflow.add_node("synthesize_analysis", node_synthesize_analysis)
    workflow.add_node("generate_verdict", node_generate_verdict_and_report)
    
    # Add edges (workflow sequence)
    workflow.add_edge("gather_data", "synthesize_analysis")
    workflow.add_edge("synthesize_analysis", "generate_verdict")
    workflow.add_edge("generate_verdict", END)
    
    # Set entry point
    workflow.set_entry_point("gather_data")
    
    return workflow.compile()


# ============================================================================
# AGENT EXECUTION
# ============================================================================

class StockAnalysisAgent:
    """
    Main agent for stock portfolio evaluation.
    """
    
    def __init__(self):
        self.graph = build_analysis_graph()
    
    def analyze_stock(self, ticker: str) -> Dict[str, Any]:
        """
        Analyze a single stock and return verdict and report.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with verdict and report
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"ANALYZING: {ticker}".center(70))
        logger.info(f"{'='*70}")
        
        # Initialize state
        initial_state: AnalysisState = {
            "ticker": ticker,
            "fundamentals": None,
            "technical": None,
            "news": None,
            "analyst_ratings": None,
            "risk_metrics": None,
            "synthesis": None,
            "verdict": None,
            "report": None,
            "errors": [],
        }
        
        # Execute workflow
        final_state = self.graph.invoke(initial_state)
        
        return {
            "ticker": ticker,
            "verdict": final_state.get("verdict"),
            "report": final_state.get("report"),
            "errors": final_state.get("errors", []),
            "timestamp": datetime.now().isoformat(),
        }
    
    def analyze_portfolio(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple stocks in a portfolio.
        
        Args:
            tickers: List of stock ticker symbols
        
        Returns:
            List of analysis results
        """
        results = []
        
        logger.info(f"\n\n{'='*70}")
        logger.info(f"PORTFOLIO ANALYSIS: {len(tickers)} STOCKS".center(70))
        logger.info(f"Tickers: {', '.join(tickers)}".center(70))
        logger.info(f"{'='*70}")
        
        for ticker in tickers:
            result = self.analyze_stock(ticker)
            results.append(result)
        
        return results


# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_portfolio_summary(results: List[Dict[str, Any]]) -> str:
    """
    Generate a comprehensive portfolio summary report.
    """
    summary = f"""
# Stock Portfolio Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Portfolio Overview
- **Total Stocks Analyzed**: {len(results)}
- **BUY Recommendations**: {sum(1 for r in results if r['verdict'] == 'BUY')}
- **HOLD Recommendations**: {sum(1 for r in results if r['verdict'] == 'HOLD')}
- **SELL Recommendations**: {sum(1 for r in results if r['verdict'] == 'SELL')}

## Individual Stock Analysis

"""
    
    for i, result in enumerate(results, 1):
        summary += f"""
### {i}. {result['ticker']} - **{result['verdict']}**
{result.get('report', 'No report available')}

---

"""
    
    return summary