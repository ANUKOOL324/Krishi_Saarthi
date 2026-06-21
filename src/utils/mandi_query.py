"""
Mandi price query module for KrishiSaarthi.

Queries a local CSV database of historical APMC Mandi prices for agricultural
commodities. Supports fuzzy commodity matching via an alias table (e.g.
"paddy" -> "rice", "chana" -> "chickpea") and automatic fallback routing
from district -> state -> national scope when local records are absent.
"""

import os
import pandas as pd

COMMODITY_ALIASES = {
    "paddy": "rice",
    "rice": "rice",
    "wheat": "wheat",
    "maize": "maize",
    "corn": "maize",
    "cotton": "cotton",
    "chickpea": "chickpea",
    "chana": "chickpea",
    "potato": "potato",
    "potatoes": "potato",
    "mustard": "mustard",
    "sarson": "mustard",
    "coffee": "coffee",
}

def get_mandi_price_data(commodity: str, state: str = None, district: str = None) -> list:
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    filepath = os.path.join(data_dir, "mandi_prices.csv")
    
    if not os.path.exists(filepath):
        from src.utils.generate_data import generate_mandi_data
        generate_mandi_data()
        
    df = pd.read_csv(filepath)
    
    commodity_clean = commodity.lower().strip()
    target_commodity = COMMODITY_ALIASES.get(commodity_clean, commodity_clean)
    
    df_filtered = df[df["commodity"].str.lower() == target_commodity]
    
    if state:
        state_clean = state.lower().strip()
        df_filtered = df_filtered[df_filtered["state"].str.lower() == state_clean]
        
    if district:
        district_clean = district.lower().strip()
        df_filtered = df_filtered[df_filtered["district"].str.lower() == district_clean]
        
    if df_filtered.empty:
        if district and state:
            return get_mandi_price_data(commodity, state=state, district=None)
        if state:
            return get_mandi_price_data(commodity, state=None, district=None)
        return []
        
    df_filtered = df_filtered.sort_values(by="date", ascending=False)
    return df_filtered.to_dict(orient="records")

def format_mandi_price_message(commodity: str, state: str = None, district: str = None) -> str:
    records = get_mandi_price_data(commodity, state, district)
    
    if not records:
        loc_str = f" in {district}, {state}" if district and state else (f" in {state}" if state else "")
        return f"No mandi price data found for '{commodity}'{loc_str}."
        
    seen_markets = set()
    latest_records = []
    for r in records:
        market_key = (r["state"], r["district"], r["market"])
        if market_key not in seen_markets:
            seen_markets.add(market_key)
            latest_records.append(r)
            if len(latest_records) >= 5:
                break
                
    response = [f"### Latest Mandi Prices for {commodity.capitalize()} (As of {latest_records[0]['date']})"]
    for r in latest_records:
        response.append(
            f"- **State**: {r['state']} | **District**: {r['district']} | **Mandi**: {r['market']}\n"
            f"  - Price Range: ₹{r['min_price']} - ₹{r['max_price']} per Quintal\n"
            f"  - Modal Price: **₹{r['modal_price']}** per Quintal"
        )
        
    return "\n".join(response)

if __name__ == "__main__":
    print(format_mandi_price_message("rice", "Punjab", "Amritsar"))
    print(format_mandi_price_message("wheat"))
