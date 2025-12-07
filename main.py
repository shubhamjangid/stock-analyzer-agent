"""
Main entry point for the application.

Usage:
    python main.py --tickers RELIANCE.NS HDFCBANK.NS
    python main.py --tickers RELIANCE.NS HDFCBANK.NS --output report.md
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

from src.agent_graph import StockAnalysisAgent, generate_portfolio_summary

from src.utils import init_langsmith_tracing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LangSmith tracing (if enabled)
init_langsmith_tracing()

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Stock Portfolio Evaluation AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--tickers",
        nargs="+",
        help="Stock tickers to analyze (e.g., AAPL MSFT GOOGL)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for the report (default: print to console)"
    )
    
    return parser.parse_args()


def validate_tickers(tickers: List[str]) -> List[str]:
    """Validate and normalize ticker symbols"""
    if not tickers:
        logger.error("No tickers provided")
        sys.exit(1)
    
    # Normalize to uppercase and remove duplicates
    normalized = list(set(t.strip().upper() for t in tickers if t.strip()))
    
    if not normalized:
        logger.error("No valid tickers after normalization")
        sys.exit(1)
    
    return normalized


def main():
    """Main function"""
    
    # Parse arguments
    args = parse_arguments()
    
    # Get tickers
    if args.tickers:
        tickers = args.tickers
    else:
        # tickers = ["RELIANCE.NS"]
        logger.error("No tickers provided. Please specify tickers using --tickers.")
        sys.exit(1)
        
    tickers = validate_tickers(tickers)
    
    logger.info(f"Starting analysis for {len(tickers)} stock(s): {', '.join(tickers)}")
    
    try:
        # Initialize agent
        agent = StockAnalysisAgent()
        
        # Analyze portfolio
        results = agent.analyze_portfolio(tickers)
        
        # Generate summary report
        report = generate_portfolio_summary(results)
        
        # Output report
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report)
            logger.info(f"\nReport saved to: {output_path.absolute()}")
        else:
            print("\n" + "="*70)
            print(report)
            print("="*70)
    
    except KeyboardInterrupt:
        logger.info("\n\nAnalysis interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()