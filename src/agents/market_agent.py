"""
Market Agent — agricultural market analyst.

Queries APMC Mandi price databases for commodities of interest, analyzes
price variations across regional markets, and advises on optimal selling
locations and timing.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from src.utils.mandi_query import format_mandi_price_message
from src.agents.config import DEFAULT_MODEL

def fetch_mandi_price(commodity: str, state: str = None, district: str = None) -> str:
    return format_mandi_price_message(commodity, state, district)

market_tool = FunctionTool(fetch_mandi_price)

market_agent = LlmAgent(
    name="market_agent",
    model=DEFAULT_MODEL,
    instruction=(
        "You are an agricultural market analyst. Your role is to query mandi (market) prices "
        "for the crops of interest, analyze the price variations across regional markets, "
        "and advise the farmer on when/where to sell their produce for maximum profit. Highlight "
        "current price ranges (minimum, maximum, modal) and date records."
    ),
    tools=[market_tool]
)
