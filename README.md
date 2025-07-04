# Weather Station to Home Assistant Relay (Dockerized Python Version)

This project provides a lightweight, **Dockerized Python microservice** for ingesting weather data from a VEVOR 7-in-1 Wi-Fi Solar Self-Charging Weather Station (Model YT60234, or any station sending data in Weather Underground format) and forwarding it to Home Assistant via **MQTT**.

---

## Features

- Accepts Weather Underground (WU) station GET requests (as sent by the VEVOR weather station)
- Converts measurements to **metric** or **imperial** units based on the `UNITS` environment variable
- Publishes sensor data to Home Assistant via MQTT using the auto-discovery format
- All sensors appear under one device in Home Assistant
- Dockerized for simple deployment anywhere
- Responds with `success` so the weather station doesn’t retry

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/C9H13NO3-dev/weatherstation-ha-relay.git
cd weatherstation-ha-relay
```

### 2. Configure the environment

Edit the `docker-compose.yml` file and set the following variables:

- `MQTT_HOST`: Hostname or IP of your MQTT broker
- `MQTT_PORT`: Broker port (default `1883`)
- `MQTT_USER` / `MQTT_PASSWORD`: Credentials if required
- `DEVICE_ID`: Unique identifier for the weather station device (default `weather_station`)
- `DEVICE_NAME`: Display name for the device in Home Assistant (default `Weather Station`)
- `DEVICE_MANUFACTURER`: (optional) Manufacturer name shown in Home Assistant (default `VEVOR`)
- `DEVICE_MODEL`: (optional) Model name (default `7-in-1 Weather Station`)
- `UNITS`: `metric` (default) or `imperial`
- `WU_FORWARD`: Set to `true` to also forward data to Weather Underground (default `false`)
- `WU_USERNAME` / `WU_PASSWORD`: Credentials for Weather Underground (optional)

Example:

```yaml
environment:
  TZ: Europe/Berlin
  MQTT_HOST: 192.168.1.100
  MQTT_PORT: 1883
  MQTT_USER: youruser
  MQTT_PASSWORD: yourpass
  DEVICE_ID: weather_station
  DEVICE_NAME: "Backyard Weather"
  DEVICE_MANUFACTURER: VEVOR
  DEVICE_MODEL: "7-in-1 Weather Station"
  # optional: "metric" (default) or "imperial"
  UNITS: metric
  # forward data to Weather Underground
  WU_FORWARD: "false"
  # credentials if forwarding
  WU_USERNAME: yourWUuser
  WU_PASSWORD: yourWUpass
```

### 3. Build and run

```bash
docker-compose up --build -d
```

The service now listens on port `80` for requests to `/weatherstation/updateweatherstation.php`.


---

## Station Configuration

Redirect the weather station’s upload URL (`rtupdate.wunderground.com`) to the IP of your server running this container. The simplest way is using Pi-hole or custom DNS on your router.

Example DNS override:

```
rtupdate.wunderground.com    <your-server-ip>
```
**Note:** If your router has DNS rebind protection enabled, you must allow this domain in your router settings when overriding DNS with Pi-hole.

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
2. The service converts units to metric or keeps imperial values depending on `UNITS`.
3. Each value is published to Home Assistant via MQTT, auto-discovered as a sensor, and grouped under the configured device.
4. The endpoint returns `success` to acknowledge the update.

### Home Assistant Sensor Entities

The following sensors are created or updated and will appear under the device specified by `DEVICE_NAME`:

*Units in parentheses assume `UNITS=metric`; values switch to imperial when `UNITS=imperial`.*

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

## Troubleshooting

- Ensure the container is reachable on port 80 from your network.
- Check that your DNS or Pi-hole setup correctly redirects the WU domain.
- Verify your MQTT broker settings.
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
