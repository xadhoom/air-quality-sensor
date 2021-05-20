import adafruit_bme280
import adafruit_bme680
import hum_utils
import math

try:
    from config import config
    elevation = int(config["elevation"])
except ImportError:
    print("Could not import config or elevation not found, setting elevation to 0.")
    elevation = 0


humidity_gm3 = None
bme280_sensor = None
bme680_sensor = None


def init(i2c):
    global bme280_sensor, bme680_sensor

    bme280_sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    bme680_sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)


def read_bme280():
    hum = bme280_sensor.humidity
    temp = bme280_sensor.temperature
    press = bme280_sensor.pressure
    sea_press = sea_level_pressure(press, temp)

    print("BME280  T: %0.1fC, H: %0.1f%%, P: %0.1f hPa" %
          (temp, hum, sea_press))

    return temp, hum, sea_press


def read_bme680():
    global humidity_gm3

    hum = bme680_sensor.humidity
    temp = bme680_sensor.temperature
    press = bme680_sensor.pressure
    sea_press = sea_level_pressure(press, temp)
    gas = bme680_sensor.gas
    # altitude = bme680_sensor.altitude
    aqi_gas = math.log(gas) + 0.04 * hum

    humidity_gm3 = hum_utils.humidity_to_gm3(temp, press, hum)
    print("BME680  T: %0.1fC, H: %0.1f%% (%0.2f g/m3), P: %0.1f hPa, R: %d ohm, %0.1f AQI" % (
        temp, hum, humidity_gm3, sea_press, gas, aqi_gas))

    return temp, hum, sea_press, gas, aqi_gas


def sea_level_pressure(p, t):
    var1 = 1 - ((0.0065 * elevation) / (t + (0.0065 * elevation) + 273.15))
    var1 = pow(var1, -5.257)
    return p * var1


def get_humidity_to_gm3():
    return humidity_gm3
