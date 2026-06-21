"""
FastMCP tool server for KrishiSaarthi.

Exposes three Model Context Protocol (MCP) tools — get_weather, recommend_crop,
and get_mandi_price — as a standalone server process. This decouples data
retrieval logic from LLM agent reasoning.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import FastMCP
from src.utils.weather_api import format_weather_message
from src.utils.crop_model import predict_crop
from src.utils.mandi_query import format_mandi_price_message

mcp = FastMCP("KrishiSaarthi")

@mcp.tool
def get_weather(location: str, days: int = 7) -> str:
    """Get the weather forecast for a location for a specified number of days."""
    return format_weather_message(location, days)

@mcp.tool
def recommend_crop(N: float, P: float, K: float, temperature: float, humidity: float, ph: float, rainfall: float) -> str:
    """Recommend the most suitable crop based on soil and weather parameters."""
    recommendations = predict_crop(N, P, K, temperature, humidity, ph, rainfall)
    if not recommendations:
        return "No suitable crops could be determined for these parameters."
        
    res = ["### Crop Suitability Recommendations"]
    for idx, (crop, conf) in enumerate(recommendations, 1):
        percentage = conf * 100
        res.append(f"{idx}. **{crop.capitalize()}** (Confidence: {percentage:.1f}%)")
        
    return "\n".join(res)

@mcp.tool
def get_mandi_price(commodity: str, state: str = None, district: str = None) -> str:
    """Query mandi prices for agricultural commodities."""
    return format_mandi_price_message(commodity, state, district)

if __name__ == "__main__":
    print("Starting KrishiSaarthi MCP Server...")
    mcp.run()
