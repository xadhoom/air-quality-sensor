import adafruit_sgp30


sgp30_sensor = None


def init(i2c):
    global sgp30_sensor

    sgp30_sensor = adafruit_sgp30.Adafruit_SGP30(i2c)


def read_sgp(abs_hum=None):
    if abs_hum:
        print("Correcting gas reading with abs hum of %0.3f" % abs_hum)
        sgp30_sensor.set_iaq_humidity(abs_hum)

    eco2, tvoc = sgp30_sensor.iaq_measure()

    print("eCO2 = %d ppm \t TVOC = %d ppb" % (eco2, tvoc))

    return eco2, tvoc
