import time
from time import mktime
import board
import busio
import math
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
from adafruit_io.adafruit_io import IO_HTTP
from simpleio import map_range
# from adafruit_pm25.uart import PM25_UART
# Uncomment below for PMSA003I Air Quality Breakout
from adafruit_pm25.i2c import PM25_I2C
import adafruit_bme280
import adafruit_bme680
import adafruit_sgp30

# for battery readings
from analogio import AnalogIn
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)

### Configure Sensor ###
# Return environmental sensor readings in degrees Celsius
USE_CELSIUS = True
# Interval the sensor publishes to Adafruit IO, in minutes
PUBLISH_INTERVAL = 1

### WiFi ###

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# AirLift FeatherWing
esp32_cs = DigitalInOut(board.D13)
esp32_reset = DigitalInOut(board.D12)
esp32_ready = DigitalInOut(board.D11)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(
    esp, secrets, status_light)

# Connect to a PM2.5 sensor over UART
reset_pin = DigitalInOut(board.D6)
#uart = busio.UART(board.TX, board.RX, baudrate=9600)
#pm25 = PM25_UART(uart, reset_pin)

# Create i2c object
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Connect to a BME280 over I2C
bme280_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# Uncomment below for PMSA003I Air Quality Breakout
pm25 = PM25_I2C(i2c, reset_pin)

# Uncomment below for BME680
# import adafruit_bme680
bme680_sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

sgp30_sensor = adafruit_sgp30.Adafruit_SGP30(i2c)


### Sensor Functions ###


def get_voltage(pin):
    return (pin.value * 3.3) / 65536 * 2


def read_sgp(abs_hum=None):
    if abs_hum:
        print("Correcting gas reading with abs hum of %0.3f" % abs_hum)
        sgp30_sensor.set_iaq_humidity(abs_hum)

    eCO2, TVOC = sgp30_sensor.iaq_measure()
    print("eCO2 = %d ppm \t TVOC = %d ppb" % (eCO2, TVOC))


def blink(led, interval=0.5, times=3, color=(0, 255, 0)):
    for i in range(1, times):
        led.fill(color)
        time.sleep(interval)
        led.fill(0)
        time.sleep(interval)


# Create an instance of the Adafruit IO HTTP client
io = IO_HTTP(secrets["aio_user"], secrets["aio_key"], wifi)

# Describes feeds used to hold Adafruit IO data
feed_aqi = io.get_feed("air-quality-sensor.aqi")
feed_aqi_category = io.get_feed("air-quality-sensor.category")
feed_pm10 = io.get_feed("air-quality-sensor.pm10")
feed_pm25 = io.get_feed("air-quality-sensor.pm25")
feed_pm100 = io.get_feed("air-quality-sensor.pm100")
feed_humidity = io.get_feed("air-quality-sensor.humidity")
feed_temperature = io.get_feed("air-quality-sensor.temperature")
feed_pressure = io.get_feed("air-quality-sensor.pressure")
feed_rssi = io.get_feed("air-quality-sensor.rssi")

elapsed_minutes = 0
current_timestamp = 0
previous_timestamp = 0

# Main Loop
while True:
    try:
        print("Fetching time...")
        cur_time = io.receive_time()
        current_timestamp = mktime(cur_time)
        print("Time fetched OK! Current ts: %d" % current_timestamp)
        elapsed_minutes = (current_timestamp - previous_timestamp) / 60
    except (ValueError, RuntimeError) as e:
        print("Failed to fetch time, retrying\n", e)
        wifi.reset()
        wifi.connect()
        continue

    if elapsed_minutes >= PUBLISH_INTERVAL:
        previous_timestamp = current_timestamp
        print("Sampling AQI...")
        aqi_reading = sample_aq_sensor()
        aqi, aqi_category = calculate_aqi(aqi_reading["pm25"])
        print("AQI: %d" % aqi)
        print("Category: %s" % aqi_category)

        print("pm1.0: %0.2f" % aqi_reading["pm10"])
        print("pm2.5: %0.2f" % aqi_reading["pm25"])
        print("pm10: %0.2f" % aqi_reading["pm100"])

        # temp and humidity (280)
        print("Sampling environmental sensor bme280...")
        temperature, humidity, pressure = read_bme280(USE_CELSIUS)
        print("Temperature: %0.1f C" % temperature)
        print("Humidity: %0.1f %%" % humidity)
        print("Pressure: %0.1f hPa" % pressure)

        # temp and humidity (680)
        print("Sampling environmental sensor bme680...")
        temperature, humidity, pressure, gas = read_bme680(USE_CELSIUS)
        print("Temperature: %0.1f C" % temperature)
        print("Humidity: %0.1f %%" % humidity)
        print("Pressure: %0.1f hPa" % pressure)
        print("Gas: %d ohm" % gas)

        # gas sensor
        abs_hum = humidity_to_gm3(temperature, pressure, humidity)
        print("ABS Hum: %0.3f g/m3" % abs_hum)
        read_sgp(abs_hum)

        # battery
        battery_voltage = get_voltage(vbat_voltage)
        print("VBat voltage: {:.2f}".format(battery_voltage))

        # wifi signal
        rssi = -120
        if (wifi.esp.is_connected):
            rssi = wifi.signal_strength()
        print("RSSI: %0.1f dBm" % rssi)

        metadata = {
            "lat": secrets["latitude"],
            "lon": secrets["longitude"],
            "ele": secrets["elevation"],
            "created_at": None
        }

        # Publish all values to Adafruit IO
        print("Publishing to Adafruit IO")
        try:
            io.send_data(feed_aqi["key"], aqi, metadata)
            io.send_data(feed_aqi_category["key"], aqi_category, metadata)
            io.send_data(feed_pm10["key"], aqi_reading["pm10"], metadata)
            io.send_data(feed_pm25["key"], aqi_reading["pm25"], metadata)
            io.send_data(feed_pm100["key"], aqi_reading["pm100"], metadata)
            io.send_data(feed_temperature["key"], temperature, metadata)
            io.send_data(feed_humidity["key"], humidity, metadata)
            io.send_data(feed_pressure["key"], pressure, metadata)
            io.send_data(feed_rssi["key"], rssi, metadata)
            print("Published!")
            # Visually notify a successful publish
            blink(status_light, times=5, color=(148, 3, 252))
        except (ValueError, RuntimeError) as e:
            print("Failed to send data to IO, retrying\n", e)
            wifi.reset()
            wifi.connect()
            continue
    else:
        print("Skipping reading/publish cycle, interval not elapsed yet")

    # blink for some seconds to indicate idle
    for i in range(1, 10):
        wifi.pixel_status((0, 245, 245))
        time.sleep(1)
        wifi.pixel_status(0)
        time.sleep(1)
