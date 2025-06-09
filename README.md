# Weather Station to Home Assistant Relay (Dockerized Python Version)

This project provides a lightweight, **Dockerized Python microservice** for ingesting weather data from a VEVOR 7-in-1 Wi-Fi Solar Self-Charging Weather Station (Model YT60234, or any station sending data in Weather Underground format) and forwarding it directly to Home Assistant via its REST API.

No PHP or web server needed&mdash;just Python and Flask!

---

## Features

- Accepts Weather Underground (WU) station GET requests (as sent by the VEVOR weather station)
- Converts all measurements to **metric units** (°C, hPa, mm, km/h, etc.)
- Pushes sensor data to Home Assistant as custom sensors via its REST API
- Dockerized for simple deployment anywhere
- Responds with `success` so the weather station doesn’t retry
- Optional relay of data to Weather Underground using Google DNS

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/C9H13NO3-dev/weatherstation-ha-relay.git
cd weatherstation-ha-relay
```

### 2. Configure the environment

Edit the `docker-compose.yml` file and set the following variables:

- `HA_URL`: Base URL to your Home Assistant API (e.g., `http://192.168.1.100:8123/api/states/`)
- `HA_TOKEN`: Your Home Assistant long-lived access token
- `WU_RELAY`: Set to `true` to also forward data to Weather Underground
- `WU_ID`: (Optional) Weather Underground station ID used when relaying
- `WU_PASSWORD`: (Optional) Weather Underground password/key for relaying

Example:

```yaml
environment:
  TZ: Europe/Berlin
  HA_URL: http://192.168.1.100:8123/api/states/
  HA_TOKEN: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  WU_RELAY: "true"
  WU_ID: YOUR_WU_ID
  WU_PASSWORD: YOUR_WU_PASSWORD
```

### 3. Build and run

```bash
docker-compose up --build -d
```

The service now listens on port `80` for requests to `/weatherstation/updateweatherstation.php`.

---

## Directory Structure

```
project-root/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── weatherstation.py
```

---

## Station Configuration

Redirect the weather station’s upload URL (`rtupdate.wunderground.com`) to the IP of your server running this container. The simplest way is using Pi-hole or custom DNS on your router.

Example DNS override:

```
rtupdate.wunderground.com    <your-server-ip>
```

On the weather station, enable Weather Underground uploads with any station ID/key.

---

## Endpoints

The service listens for GET requests at:

```
/weatherstation/updateweatherstation.php
```

With query parameters matching the WU format, e.g.:

```
http://<your-server-ip>/weatherstation/updateweatherstation.php?ID=XXXXX&PASSWORD=XXXXX&dateutc=xxxx-x-xx+xx:xx:xx&baromin=x&tempf=x&humidity=x&dewptf=x&rainin=x&dailyrainin=x&winddir=x&windspeedmph=x&windgustmph=x&UV=x&solarRadiation=x
```

---

## How it Works

1. The weather station uploads data to this endpoint.
2. The service converts all units to metric.
3. Each value is sent to Home Assistant via its REST API as individual sensors.
4. The endpoint returns `success` to acknowledge the update.

### Home Assistant Sensor Entities

The following sensors are created or updated:

- `sensor.weather_station_barometric_pressure` (hPa)
- `sensor.weather_station_temperature` (°C)
- `sensor.weather_station_humidity` (%)
- `sensor.weather_station_dew_point` (°C)
- `sensor.weather_station_rainfall` (mm)
- `sensor.weather_station_daily_rainfall` (mm)
- `sensor.weather_station_wind_direction` (°)
- `sensor.weather_station_wind_speed` (km/h)
- `sensor.weather_station_wind_gust_speed` (km/h)
- `sensor.weather_station_uv_index` (index)
- `sensor.weather_station_solar_radiation` (W/m²)

You can use these entities directly in your Home Assistant dashboards or automations.

---

## Code Overview

- **`weatherstation.py`** – Flask microservice listening on port 80. Parses GET parameters, converts to metric, posts to Home Assistant and responds with `success`.
- **`requirements.txt`** – Python dependencies: Flask, requests, pytz.
- **`Dockerfile`** – Uses `python:3.12-slim` as a base image, installs dependencies and runs the service.
- **`docker-compose.yml`** – Simple build/run configuration that passes environment variables for Home Assistant and timezone.

---

## Troubleshooting

- Ensure the container is reachable on port 80 from your network.
- Check that your DNS or Pi-hole setup correctly redirects the WU domain.
- Verify your Home Assistant URL and token.
- Review logs with:

```bash
docker-compose logs -f
```

Add logging or print statements to `weatherstation.py` for further debugging.

---

## License

This project is licensed under the [CC0 1.0 Universal](LICENSE).

---

## Acknowledgements

- Original Weather Underground relay script inspiration by [@vlovmx](https://github.com/vlovmx)
- Python rewrite and containerization by C9H13NO3-dev
