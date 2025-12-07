import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration for the Stock Portfolio Evaluation Agent"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-4-turbo-preview"
    
    # News API Configuration
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

    # LangSmith
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() in ("1", "true", "yes")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "stock-portfolio-evaluator")

    # Agent Configuration
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30
    
    # Analysis Configuration
    TECHNICAL_PERIOD_SHORT = 50  # days for short-term SMA
    TECHNICAL_PERIOD_LONG = 200   # days for long-term SMA
    RSI_PERIOD = 14
    NEWS_ARTICLES_LIMIT = 10

    BENCHMARK_INDEX = "^NSEI"  # Nifty50 Index for beta calculation
    
    # Stock Analysis Thresholds
    PE_RATIO_THRESHOLD_LOW = 15
    PE_RATIO_THRESHOLD_HIGH = 25
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    
#     @staticmethod
#     def validate_config():
#         """Validate that all required environment variables are set"""
#         required_vars = {
#             "OPENAI_API_KEY": Config.OPENAI_API_KEY,
#             "NEWS_API_KEY": Config.NEWS_API_KEY,
#         }
        
#         missing_vars = [var for var, value in required_vars.items() if not value]
        
#         if missing_vars:
#             raise ValueError(
#                 f"Missing required environment variables: {', '.join(missing_vars)}\n"
#                 f"Please create a .env file with these variables."
#             )
        
#         return True

# # Validate config on import
# try:
#     Config.validate_config()
# except ValueError as e:
#     print(f"Configuration Warning: {e}")