import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    def __init__(self):
        # Dedalus API Key (required)
        self.dedalus_api_key = os.getenv("DEDALUS_API_KEY")
        if not self.dedalus_api_key:
            raise ValueError(
                "DEDALUS_API_KEY environment variable is required. "
                "Please add it to your .env file."
            )

        # Optional: User can bring their own API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        self.financial_model = "openai/gpt-5"
        self.market_model = "openai/gpt-5"
        self.sentiment_model = "openai/gpt-5"
        self.judge_models = ["openai/gpt-5", "anthropic/claude-sonnet-4-20250514"]

        # MCP servers
        self.brave_search_mcp = "windsor/brave-search-mcp"
        self.exa_mcp = "joerup/exa-mcp"
        self.sonar = "akakak/sonar"
        self.yahoo_finance_mcp = "aq_humor/yahoo-finance-mcp"

        # Logging
        self.debug = os.getenv("DEBUG", "false").lower() == "true"


config = Config()
