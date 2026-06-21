"""
Crop Agent — agronomy and soil-crop suitability specialist.

Matches soil chemistry indicators (NPK, pH) and climate parameters against
the crop recommendation dataset using a KNN classifier. Explains the agronomic
reasoning behind each recommendation.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from src.utils.crop_model import predict_crop
from src.agents.config import DEFAULT_MODEL

def recommend_suitable_crop(N: float, P: float, K: float, temp: float, hum: float, ph: float, rain: float) -> str:
    recs = predict_crop(N, P, K, temp, hum, ph, rain)
    if not recs:
        return "No suitable crops found."
    return "\n".join([f"- {crop.capitalize()} (Confidence: {conf*100:.1f}%)" for crop, conf in recs])

crop_tool = FunctionTool(recommend_suitable_crop)

crop_agent = LlmAgent(
    name="crop_agent",
    model=DEFAULT_MODEL,
    instruction=(
        "You are an agronomy and crop suitability specialist. Your role is to analyze the farmer's "
        "soil metrics (N, P, K, pH) and average weather conditions, call your crop recommendation tool "
        "to see which crops fit the profile, and explain to the farmer WHY these crops are suitable. "
        "Explain the nutritional and soil chemistry requirements for the top suggestions."
    ),
    tools=[crop_tool]
)
