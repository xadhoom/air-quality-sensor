from adafruit_pm25.i2c import PM25_I2C
from simpleio import map_range
import board
import digitalio
import tasko
import time


pm25_sensor = None


class PM25(PM25_I2C):
    def __init__(self, i2c_bus, set_pin=None, reset_pin=None):
        self._reset_pin = reset_pin
        self._i2c_bus = i2c_bus
        self._set_pin = set_pin
        self._set_pin.direction = digitalio.Direction.OUTPUT
        self._set_pin.value = True

        super().__init__(i2c_bus, reset_pin)

    def resume(self):
        self._set_pin.value = True

    def shutdown(self):
        self._set_pin.value = False


def init(i2c):
    global pm25_sensor

    rst = digitalio.DigitalInOut(board.D6)
    set = digitalio.DigitalInOut(board.D5)

    pm25_sensor = PM25(i2c, rst, set)
    pm25_sensor.shutdown()
    print("PMSA003I sensor started (idle)!")


async def sample_aq_sensor():
    """
    Samples PM2.5 sensor
    over a 2.3 second sample rate.
    """
    global pm25_sensor

    aq_reading = {"pm10": 0, "pm25": 0, "pm100": 0}
    aq_samples10 = []
    aq_samples25 = []
    aq_samples100 = []

    # activate sensor
    pm25_sensor.resume()
    pm25_sensor = PM25(pm25_sensor._i2c_bus,
                       pm25_sensor._reset_pin, pm25_sensor._set_pin)
    # according to datasheet, after powering on the sensor we should
    # wait at least 30 seconds because of fan
    await tasko.sleep(30)

    # initial timestamp
    time_start = time.monotonic()
    # gather some samples for 10 seconds and average them
    while time.monotonic() - time_start <= 10:
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

    # Shutdown sensor
    pm25_sensor.shutdown()

    return aq_reading
