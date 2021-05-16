import time


class Measurements:
    def __init__(self):
        self.reset()

    def put_eco2(self, value):
        meas = {"value": value, "ts": self.now_ts()}
        self.sgp30_eco2.append(meas)

    def put_tvoc(self, value):
        meas = {"value": value, "ts": self.now_ts()}
        self.sgp30_tvoc.append(meas)

    def put_pressure(self, sensor, value):
        meas = {"value": value, "ts": self.now_ts()}
        if sensor == "bme280":
            self.bme280_pres.append(meas)
        elif sensor == "bme680":
            self.bme680_pres.append(meas)

    def put_temperature(self, sensor, value):
        meas = {"value": value, "ts": self.now_ts()}
        if sensor == "bme280":
            self.bme280_temp.append(meas)
        elif sensor == "bme680":
            self.bme680_temp.append(meas)

    def put_humidity(self, sensor, value):
        meas = {"value": value, "ts": self.now_ts()}
        if sensor == "bme280":
            self.bme280_hum.append(meas)
        elif sensor == "bme680":
            self.bme680_hum.append(meas)

    def put_gas(self, gas_ohm, gas_aqi):
        gas_ohm = {"value": gas_ohm, "ts": self.now_ts()}
        gas_aqi = {"value": gas_aqi, "ts": self.now_ts()}
        self.bme680_gas.append(gas_ohm)
        self.bme680_gas_aqi.append(gas_aqi)

    def put_battery(self, value):
        meas = {"value": value, "ts": self.now_ts()}
        self.battery_voltage.append(meas)

    def put_pm_data(self, value):
        meas = {"value": value, "ts": self.now_ts()}
        self.pm_data.append(meas)

    def reset(self):
        print("Resetting all measurements")
        self.bme280_temp = []
        self.bme280_hum = []
        self.bme280_pres = []

        self.bme680_temp = []
        self.bme680_hum = []
        self.bme680_pres = []
        self.bme680_gas = []
        self.bme680_gas_aqi = []

        self.sgp30_eco2 = []
        self.sgp30_tvoc = []

        self.pm_data = []

        self.battery_voltage = []

    async def publish(self):
        print("Publishing data")
        self.reset()

    def now_ts(self):
        return time.time()
