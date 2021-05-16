import board
from adafruit_pm25.i2c import PM25_I2C
from digitalio import DigitalInOut
from simpleio import map_range
import tasko
import time


pm25_sensor = None


def init(i2c):
    global pm25_sensor

    pm25_sensor = PM25_I2C(i2c, DigitalInOut(board.D6))


def calculate_aqi(pm_sensor_reading):
    """Returns a calculated air quality index (AQI)
    and category as a tuple.
    NOTE: The AQI returned by this function should ideally be measured
    using the 24-hour concentration average. Calculating a AQI without
    averaging will result in higher AQI values than expected.
    :param float pm_sensor_reading: Particulate matter sensor value.

    """
    # Check sensor reading using EPA breakpoint (Clow-Chigh)
    if 0.0 <= pm_sensor_reading <= 12.0:
        # AQI calculation using EPA breakpoints (Ilow-IHigh)
        aqi_val = map_range(int(pm_sensor_reading), 0, 12, 0, 50)
        aqi_cat = "Good"
    elif 12.1 <= pm_sensor_reading <= 35.4:
        aqi_val = map_range(int(pm_sensor_reading), 12, 35, 51, 100)
        aqi_cat = "Moderate"
    elif 35.5 <= pm_sensor_reading <= 55.4:
        aqi_val = map_range(int(pm_sensor_reading), 36, 55, 101, 150)
        aqi_cat = "Unhealthy for Sensitive Groups"
    elif 55.5 <= pm_sensor_reading <= 150.4:
        aqi_val = map_range(int(pm_sensor_reading), 56, 150, 151, 200)
        aqi_cat = "Unhealthy"
    elif 150.5 <= pm_sensor_reading <= 250.4:
        aqi_val = map_range(int(pm_sensor_reading), 151, 250, 201, 300)
        aqi_cat = "Very Unhealthy"
    elif 250.5 <= pm_sensor_reading <= 350.4:
        aqi_val = map_range(int(pm_sensor_reading), 251, 350, 301, 400)
        aqi_cat = "Hazardous"
    elif 350.5 <= pm_sensor_reading <= 500.4:
        aqi_val = map_range(int(pm_sensor_reading), 351, 500, 401, 500)
        aqi_cat = "Hazardous"
    else:
        print("Invalid PM2.5 concentration")
        aqi_val = -1
        aqi_cat = None
    return aqi_val, aqi_cat


async def sample_aq_sensor():
    """
    Samples PM2.5 sensor
    over a 2.3 second sample rate.
    """
    aq_reading = {"pm10": 0, "pm25": 0, "pm100": 0}
    aq_samples10 = []
    aq_samples25 = []
    aq_samples100 = []

    # initial timestamp
    time_start = time.monotonic()
    # when concentration is low, sensor samples every 2.3 seconds
    # so we collect some samples and do an average
    while time.monotonic() - time_start <= (2.3*3):
        try:
            aqdata = pm25_sensor.read()
            # print("%r" % aqdata)
            aq_samples10.append(aqdata["pm10 env"])
            aq_samples25.append(aqdata["pm25 env"])
            aq_samples100.append(aqdata["pm100 env"])
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            await tasko.sleep(0.5)
            continue

        # pm sensor output rate of 1s
        await tasko.sleep(1)

    # average sample reading / # samples
    aq_reading["pm10"] = sum(aq_samples10) / len(aq_samples10)
    aq_reading["pm25"] = sum(aq_samples25) / len(aq_samples25)
    aq_reading["pm100"] = sum(aq_samples100) / len(aq_samples100)

    aq_samples10.clear()
    aq_samples25.clear()
    aq_samples100.clear()

    return aq_reading
