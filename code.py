from analogio import AnalogIn
from measurements import Measurements
import bme
import board
import busio
import led
import microcontroller
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


async def read_sgp():
    abs_hum = bme.get_humidity_to_gm3()
    eco2, tvoc = sgp30.read_sgp(abs_hum)
    measurements.put_eco2(eco2)
    measurements.put_tvoc(tvoc)

    print("eCO2 = %d ppm \t TVOC = %d ppb (Hum correction: %0.3f g/m3)" %
          (eco2, tvoc, abs_hum or 0))


async def poll_sgp():
    # according to datasheet, this sensor must be read
    # every second to ensure proper operation of the dynamic baseline
    # compensation algorithm
    abs_hum = bme.get_humidity_to_gm3()
    sgp30.read_sgp(abs_hum)


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


async def get_rssi():
    rssi = wifi.get_rssi()
    measurements.put_rssi(rssi)
    print("RSSI: %0.1f dBm" % rssi)


async def get_cpu_temp():
    t = microcontroller.cpu.temperature
    measurements.put_cpu_temp(t)
    print("CPU Temp: %0.1fC" % t)


# init functions
bme.init(i2c)
sgp30.init(i2c)
pm25.init(i2c)
wifi.init(status_light)
wifi.set_time()
mqtt.init(wifi.get_esp())
mqtt.connect()

tasko.schedule(hz=1, coroutine_function=poll_sgp)
tasko.schedule(hz=1/2, coroutine_function=led.blink,
               led=status_light, interval=0.1, times=2)
tasko.schedule(hz=1/60, coroutine_function=read_sgp)
tasko.schedule(hz=1/60, coroutine_function=read_bmes)
tasko.schedule(hz=1/60, coroutine_function=get_voltage)
tasko.schedule(hz=1/60, coroutine_function=get_rssi)
tasko.schedule(hz=1/60, coroutine_function=get_cpu_temp)
tasko.schedule(hz=1/120, coroutine_function=read_pm25)
tasko.schedule_later(hz=1/300, coroutine_function=measurements.publish)
tasko.schedule_later(hz=1/1800, coroutine_function=wifi.async_set_time)
tasko.run()
