import adafruit_bme280
#import adafruit_bme680_clear as adafruit_bme680
import adafruit_bme680
import math


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

    print("BME280  T: %0.1fC, H: %0.1f%%, P: %0.1f hPa" % (temp, hum, press))

    return temp, hum, press


def read_bme680():
    hum = bme680_sensor.humidity
    temp = bme680_sensor.temperature
    press = bme680_sensor.pressure
    gas = bme680_sensor.gas
    # altitude = bme680_sensor.altitude
    aqi_gas = math.log(gas) + 0.04 * hum

    print("BME680  T: %0.1fC, H: %0.1f%%, P: %0.1f hPa, R: %d ohm, %0.1f AQI" % (
        temp, hum, press, gas, aqi_gas))

    return temp, hum, press, gas, aqi_gas
