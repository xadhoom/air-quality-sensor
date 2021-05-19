import mqtt
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

    def get_humidity(self):
        # not ideal if one sensor is broken, but, oh well
        return self.last_and_average([self.bme280_hum, self.bme680_hum])

    def get_temp(self):
        # not ideal if one sensor is broken, but, oh well
        return self.last_and_average([self.bme280_temp, self.bme680_temp])

    def get_pressure(self):
        # not ideal if one sensor is broken, but, oh well
        return self.last_and_average([self.bme280_pres, self.bme680_pres])

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
        await mqtt.publish(["gas", "eco2"], self.get_eco2())
        await mqtt.publish(["gas", "tvoc"], self.get_tvoc())
        self.reset()

    def get_eco2(self):
        data = self.get_mean_value(self.sgp30_eco2)
        if not data:
            return []
        ts, avg = data
        data_points = [{
            "sensor": "sgp30",
            "eco2": avg,
            "ts": ts
        }]
        return data_points

    def get_tvoc(self):
        data = self.get_mean_value(self.sgp30_tvoc)
        if not data:
            return []
        ts, avg = data
        data_points = [{
            "sensor": "sgp30",
            "tvoc": avg,
            "ts": ts
        }]
        return data_points

    def get_mean_value(self, data_serie):
        count = len(data_serie)
        if not count:
            return ()

        value = 0
        last_ts = data_serie[-1]["ts"]
        for measure in data_serie:
            value = value + measure["value"]

        return last_ts, value/count

    def now_ts(self):
        return time.time()

    def last_and_average(self, *args):
        value = 0
        sensors = 0
        list_of_sensors = args[0]

        for sensor_data in list_of_sensors:
            if len(sensor_data):
                sensors = sensors + 1
                value = value + sensor_data[-1]["value"]

        if sensors and value:
            return (value / sensors)
        else:
            return None
