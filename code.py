from analogio import AnalogIn
from measurements import Measurements
import bme
import board
import busio
import led
import mqtt
import neopixel
import pm25
import sgp30
import supervisor
import tasko
import wifi

# Disable auto reload on USB activity
supervisor.disable_autoreload()

# Devices setup
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Battery
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)

# Global vars
measurements = Measurements()


async def blink_led():
    await led.blink(status_light)


async def read_sgp():
    # according to datasheet, this sensor must be read
    # every second to ensure proper operation of the dynamic baseline
    # compensation algorithm
    abs_hum = bme.get_humidity_to_gm3()
    eco2, tvoc = sgp30.read_sgp(abs_hum)
    measurements.put_eco2(eco2)
    measurements.put_tvoc(tvoc)


async def read_bmes():
    temp, hum, press = bme.read_bme280()
    measurements.put_temperature("bme280", temp)
    measurements.put_humidity("bme280", hum)
    measurements.put_pressure("bme280", press)

    temp, hum, press, gas, aqi_gas = bme.read_bme680()
    measurements.put_temperature("bme680", temp)
    measurements.put_humidity("bme680", hum)
    measurements.put_pressure("bme680", press)
    measurements.put_gas(gas, aqi_gas)


async def read_pm25():
    aq_reading = await pm25.sample_aq_sensor()
    aqi, aqi_category = pm25.calculate_aqi(aq_reading["pm25"])
    measurements.put_pm_data(aq_reading)
    print("%r" % aq_reading)
    print("%r %r" % (aqi, aqi_category))


async def get_voltage():
    vbat = (vbat_voltage.value * 3.3) / 65536 * 2
    print("Battery voltage: %0.2fV" % vbat)
    measurements.put_battery(vbat)


# init functions
bme.init(i2c)
sgp30.init(i2c)
pm25.init(i2c)
wifi.init(status_light)
wifi.set_time()
mqtt.init(wifi.get_esp())
mqtt.connect()

# tasko.schedule(hz=5, coroutine_function=blink_led)
tasko.schedule(hz=1, coroutine_function=read_sgp)
tasko.schedule(hz=1/30, coroutine_function=read_bmes)
tasko.schedule(hz=1/30, coroutine_function=read_pm25)
tasko.schedule(hz=1/60, coroutine_function=get_voltage)
tasko.schedule_later(hz=1/60, coroutine_function=measurements.publish)
tasko.schedule_later(hz=1/1800, coroutine_function=wifi.async_set_time)
tasko.run()
