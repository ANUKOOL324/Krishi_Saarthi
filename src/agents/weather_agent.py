"""
Weather Agent — agricultural meteorology specialist.

Fetches weather forecasts and analyzes them for farming hazards such as
frost, heatwaves, and unseasonal rainfall. Exposes the get_weather tool
via Google ADK's FunctionTool interface.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from src.utils.weather_api import format_weather_message
from src.agents.config import DEFAULT_MODEL

def fetch_weather(location: str, days: int = 7) -> str:
    return format_weather_message(location, days)

weather_tool = FunctionTool(fetch_weather)

weather_agent = LlmAgent(
    name="weather_agent",
    model=DEFAULT_MODEL,
    instruction=(
        "You are an agricultural meteorology expert. Your role is to fetch weather forecast "
        "data for the farmer's location, analyze it for hazards (such as high heat, unexpected rain, "
        "or sudden frost), and provide actionable, weather-informed recommendations for crop care "
        "and field preparation for the upcoming week. Focus on highlighting warnings."
    ),
    tools=[weather_tool]
)
