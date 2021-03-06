import adafruit_sgp30


sgp30_sensor = None


def init(i2c):
    global sgp30_sensor

    sgp30_sensor = adafruit_sgp30.Adafruit_SGP30(i2c)
    print("SGP30 sensor started!")


def read_sgp(abs_hum=None):
    if abs_hum:
        sgp30_sensor.set_iaq_humidity(abs_hum)

    eco2, tvoc = sgp30_sensor.iaq_measure()

    return eco2, tvoc
