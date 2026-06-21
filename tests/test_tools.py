import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.weather_api import get_coordinates, get_weather_forecast
from src.utils.crop_model import predict_crop, init_model
from src.utils.mandi_query import get_mandi_price_data, COMMODITY_ALIASES

def test_get_coordinates():
    lat, lon, name = get_coordinates("Amritsar")
    assert lat is not None
    assert lon is not None
    assert "Amritsar" in name
    
    lat2, lon2, name2 = get_coordinates("UnknownCityXYZ")
    assert lat2 is not None
    assert lon2 is not None
    assert "UnknownCityXYZ" in name2

def test_get_weather_forecast():
    forecast = get_weather_forecast("Amritsar", days=3)
    assert forecast["location"] is not None
    assert len(forecast["days"]) == 3
    for d in forecast["days"]:
        assert "date" in d
        assert "temp_max" in d
        assert "temp_min" in d
        assert "rain" in d
        assert "precipitation_probability" in d

def test_predict_crop():
    init_model()
    recs = predict_crop(90, 42, 43, 25.5, 82.3, 6.2, 180.0)
    assert len(recs) > 0
    crop, conf = recs[0]
    assert isinstance(crop, str)
    assert 0.0 <= conf <= 1.0

def test_get_mandi_price_data():
    records = get_mandi_price_data("rice", "Punjab", "Amritsar")
    assert len(records) > 0
    assert records[0]["commodity"] == "rice"
    assert records[0]["state"] == "Punjab"
    assert "modal_price" in records[0]

def test_mandi_aliases():
    records_paddy = get_mandi_price_data("paddy", "Punjab", "Amritsar")
    records_rice = get_mandi_price_data("rice", "Punjab", "Amritsar")
    assert len(records_paddy) == len(records_rice)
