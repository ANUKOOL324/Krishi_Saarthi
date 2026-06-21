"""
Weather data module for KrishiSaarthi.

Resolves city names to coordinates via the Open-Meteo Geocoding API, fetches
daily weather forecasts from the Open-Meteo Forecast API, and formats the
results for consumption by the Weather Agent. Includes offline fallback
generators for 14 major Indian agricultural regions.
"""

import requests
import random
from datetime import datetime, timedelta

def get_coordinates(location_name: str) -> tuple:
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=1&language=en&format=json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return result["latitude"], result["longitude"], result.get("name", location_name)
    except Exception as e:
        print(f"Geocoding API failed: {e}. Falling back to mock coordinates.")
    
    region_fallback = {
        "amritsar": (31.63, 74.87, "Amritsar, Punjab"),
        "karnal": (29.68, 76.99, "Karnal, Haryana"),
        "lucknow": (26.85, 80.94, "Lucknow, Uttar Pradesh"),
        "indore": (22.71, 75.85, "Indore, Madhya Pradesh"),
        "dharwad": (15.45, 75.00, "Dharwad, Karnataka"),
        "patna": (25.59, 85.13, "Patna, Bihar"),
        "rajkot": (22.30, 70.80, "Rajkot, Gujarat"),
        "nagpur": (21.14, 79.08, "Nagpur, Maharashtra"),
        "bhopal": (23.25, 77.41, "Bhopal, Madhya Pradesh"),
        "latur": (18.40, 76.56, "Latur, Maharashtra"),
        "agra": (27.18, 78.00, "Agra, Uttar Pradesh"),
        "hooghly": (22.90, 88.39, "Hooghly, West Bengal"),
        "alwar": (27.56, 76.60, "Alwar, Rajasthan"),
        "chikmagalur": (13.31, 75.77, "Chikmagalur, Karnataka"),
    }
    
    key = location_name.lower().strip()
    for name, coords in region_fallback.items():
        if name in key:
            return coords[0], coords[1], coords[2]
            
    return 26.85, 80.94, f"{location_name} (Fallback Location)"

def get_weather_forecast(location: str, days: int = 7) -> dict:
    days = min(max(1, days), 14)
    lat, lon, resolved_name = get_coordinates(location)
    
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,rain_sum,showers_sum,snowfall_sum,precipitation_probability_max",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(weather_url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            daily = data.get("daily", {})
            
            forecast = {
                "location": resolved_name,
                "latitude": lat,
                "longitude": lon,
                "days": []
            }
            
            for i in range(days):
                if i < len(daily.get("time", [])):
                    forecast["days"].append({
                        "date": daily["time"][i],
                        "temp_max": daily["temperature_2m_max"][i],
                        "temp_min": daily["temperature_2m_min"][i],
                        "rain": daily["rain_sum"][i] + daily["showers_sum"][i],
                        "precipitation_probability": daily["precipitation_probability_max"][i]
                    })
            return forecast
    except Exception as e:
        print(f"Weather Forecast API failed: {e}. Falling back to mock weather generation.")
        
    forecast = {
        "location": resolved_name,
        "latitude": lat,
        "longitude": lon,
        "days": []
    }
    
    start_date = datetime.now()
    for i in range(days):
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        
        temp_min = round(random.uniform(18.0, 24.0), 1)
        temp_max = round(temp_min + random.uniform(8.0, 15.0), 1)
        
        is_rainy = random.random() > 0.7
        rain = round(random.uniform(2.0, 25.0), 1) if is_rainy else 0.0
        precip_prob = random.randint(40, 95) if is_rainy else random.randint(0, 20)
        
        forecast["days"].append({
            "date": date_str,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "rain": rain,
            "precipitation_probability": precip_prob
        })
        
    return forecast

def format_weather_message(location: str, days: int = 7) -> str:
    forecast = get_weather_forecast(location, days)
    
    msg = [
        f"### Weather Forecast for {forecast['location']}",
        f"**Coordinates**: Latitude {forecast['latitude']}, Longitude {forecast['longitude']}\n"
    ]
    
    for day in forecast["days"]:
        rain_info = f"Rain: {day['rain']}mm ({day['precipitation_probability']}% chance)" if day['rain'] > 0 else "Sunny / Dry"
        msg.append(
            f"- **Date**: {day['date']}\n"
            f"  - Temperature: Min {day['temp_min']}°C, Max {day['temp_max']}°C\n"
            f"  - Condition: {rain_info}"
        )
        
    return "\n".join(msg)

if __name__ == "__main__":
    print(format_weather_message("Amritsar", 3))
