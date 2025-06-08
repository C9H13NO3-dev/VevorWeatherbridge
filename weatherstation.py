from flask import Flask, request
import requests
from datetime import datetime
import pytz
import os

# Set these!
HOME_ASSISTANT_URL_BASE = os.environ.get("HA_URL", "http://xx.xx.xx.xx:8123/api/states/")
ACCESS_TOKEN = os.environ.get("HA_TOKEN", "YOUR_LONG_LIVED_ACCESS_TOKEN")
TIMEZONE = os.environ.get("TZ", "Europe/Berlin")

app = Flask(__name__)

def f_to_c(f): return round((float(f) - 32) * 5.0 / 9.0, 1)
def inhg_to_hpa(inhg): return round(float(inhg) * 33.8639, 1)
def mph_to_kmh(mph): return round(float(mph) * 1.60934, 1)
def inch_to_mm(inch): return round(float(inch) * 25.4, 1)

def safe_get(key): return request.args.get(key, None)

@app.route('/weatherstation/updateweatherstation.php')
def update():
    attributes = {
        "Barometric Pressure": {
            "value": inhg_to_hpa(safe_get('baromin')) if safe_get('baromin') else None,
            "unit": "hPa",
            "device_class": "atmospheric_pressure"
        },
        "Temperature": {
            "value": f_to_c(safe_get('tempf')) if safe_get('tempf') else None,
            "unit": "°C",
            "device_class": "temperature"
        },
        "Humidity": {
            "value": safe_get('humidity'),
            "unit": "%",
            "device_class": "humidity"
        },
        "Dew Point": {
            "value": f_to_c(safe_get('dewptf')) if safe_get('dewptf') else None,
            "unit": "°C",
            "device_class": "temperature"
        },
        "Rainfall": {
            "value": inch_to_mm(safe_get('rainin')) if safe_get('rainin') else None,
            "unit": "mm",
            "device_class": "precipitation"
        },
        "Daily Rainfall": {
            "value": inch_to_mm(safe_get('dailyrainin')) if safe_get('dailyrainin') else None,
            "unit": "mm",
            "device_class": "precipitation"
        },
        "Wind Direction": {
            "value": safe_get('winddir'),
            "unit": "°",
            "device_class": None
        },
        "Wind Speed": {
            "value": mph_to_kmh(safe_get('windspeedmph')) if safe_get('windspeedmph') else None,
            "unit": "km/h",
            "device_class": "wind_speed"
        },
        "Wind Gust Speed": {
            "value": mph_to_kmh(safe_get('windgustmph')) if safe_get('windgustmph') else None,
            "unit": "km/h",
            "device_class": "wind_speed"
        },
        "UV Index": {
            "value": safe_get('UV'),
            "unit": "index",
            "device_class": None
        },
        "Solar Radiation": {
            "value": safe_get('solarRadiation'),
            "unit": "W/m²",
            "device_class": "irradiance"
        }
    }

    dateutc = safe_get('dateutc')
    local_time = ""
    if dateutc:
        try:
            dt = datetime.strptime(dateutc, "%Y-%m-%d %H:%M:%S")
            dt = pytz.utc.localize(dt).astimezone(pytz.timezone(TIMEZONE))
            local_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            local_time = dateutc  # fallback

    # Post to Home Assistant for each sensor
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    for name, data in attributes.items():
        sensor_name = "sensor.weather_station_" + name.lower().replace(" ", "_")
        payload = {
            "state": data["value"],
            "attributes": {
                "friendly_name": name,
                "unit_of_measurement": data["unit"],
                "device_class": data["device_class"],
                "measured_on": local_time
            }
        }
        url = f"{HOME_ASSISTANT_URL_BASE}{sensor_name}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=2)
            resp.raise_for_status()
        except Exception as e:
            print(f"Error updating {sensor_name}: {e}")

    return "success", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
