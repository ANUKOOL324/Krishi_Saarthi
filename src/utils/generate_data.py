"""
Synthetic data generators for KrishiSaarthi.

Creates crop_recommendation.csv (KNN training data with 8 crops x 40 samples)
and mandi_prices.csv (APMC market price records for 17 commodity-market pairs)
under the data/ directory. Dates are generated dynamically relative to today.
"""

import os
import csv
import random
from datetime import datetime, timedelta

def generate_crop_data():
    crops_profile = {
        "rice": (80, 120, 35, 55, 35, 45, 20, 35, 75, 95, 5.5, 7.0, 150, 300),
        "maize": (60, 100, 35, 55, 15, 30, 18, 30, 55, 75, 5.5, 7.5, 60, 120),
        "chickpea": (15, 35, 50, 70, 70, 90, 15, 25, 15, 35, 6.0, 8.0, 30, 60),
        "cotton": (90, 130, 35, 55, 15, 30, 22, 35, 70, 90, 6.5, 8.0, 60, 110),
        "wheat": (70, 100, 35, 60, 30, 50, 10, 25, 45, 70, 6.0, 7.5, 40, 90),
        "potato": (80, 120, 45, 65, 90, 130, 12, 22, 60, 80, 5.0, 6.5, 50, 100),
        "mustard": (45, 75, 25, 45, 20, 35, 12, 24, 55, 75, 6.0, 7.8, 25, 70),
        "coffee": (85, 115, 15, 35, 25, 40, 18, 28, 75, 95, 5.5, 6.8, 140, 220),
    }
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, "crop_recommendation.csv")
    
    headers = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall", "label"]
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for crop, limits in crops_profile.items():
            for _ in range(40):
                N = round(random.uniform(limits[0], limits[1]), 2)
                P = round(random.uniform(limits[2], limits[3]), 2)
                K = round(random.uniform(limits[4], limits[5]), 2)
                temp = round(random.uniform(limits[6], limits[7]), 2)
                hum = round(random.uniform(limits[8], limits[9]), 2)
                ph = round(random.uniform(limits[10], limits[11]), 2)
                rain = round(random.uniform(limits[12], limits[13]), 2)
                writer.writerow([N, P, K, temp, hum, ph, rain, crop])
                
    print(f"Generated {filepath} successfully.")

def generate_mandi_data():
    mandi_records = [
        ("rice", "Punjab", "Amritsar", "Amritsar Mandi", 2400),
        ("rice", "Haryana", "Karnal", "Karnal Mandi", 2450),
        ("rice", "Uttar Pradesh", "Lucknow", "Lucknow Main", 2200),
        ("wheat", "Punjab", "Amritsar", "Amritsar Mandi", 2250),
        ("wheat", "Uttar Pradesh", "Lucknow", "Lucknow Main", 2150),
        ("wheat", "Madhya Pradesh", "Indore", "Indore Choithram", 2300),
        ("maize", "Karnataka", "Dharwad", "Dharwad Mandi", 1900),
        ("maize", "Bihar", "Patna", "Patna Gola", 1850),
        ("cotton", "Gujarat", "Rajkot", "Rajkot Yard", 6800),
        ("cotton", "Maharashtra", "Nagpur", "Nagpur Kalamna", 6900),
        ("chickpea", "Madhya Pradesh", "Bhopal", "Karond Mandi", 4900),
        ("chickpea", "Maharashtra", "Latur", "Latur Market Yard", 5100),
        ("potato", "Uttar Pradesh", "Agra", "Agra Fatehabad", 1200),
        ("potato", "West Bengal", "Hooghly", "Sheoraphuly Mandi", 1400),
        ("mustard", "Rajasthan", "Alwar", "Alwar Mandi", 5400),
        ("mustard", "Haryana", "Karnal", "Karnal Mandi", 5350),
        ("coffee", "Karnataka", "Chikmagalur", "Chikmagalur APMC", 18000),
    ]
    
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, "mandi_prices.csv")
    
    headers = ["commodity", "state", "district", "market", "min_price", "max_price", "modal_price", "date"]
    
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for record in mandi_records:
            commodity, state, district, market, base = record
            base_date = datetime.now() - timedelta(days=7)
            for offset in range(7):
                date_str = (base_date + timedelta(days=offset)).strftime("%Y-%m-%d")
                variance = random.uniform(-0.05, 0.05)
                modal = int(base * (1 + variance))
                min_p = int(modal * 0.92)
                max_p = int(modal * 1.08)
                writer.writerow([commodity, state, district, market, min_p, max_p, modal, date_str])
                
    print(f"Generated {filepath} successfully.")

if __name__ == "__main__":
    generate_crop_data()
    generate_mandi_data()
