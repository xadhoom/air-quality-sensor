import mqtt
import time


class Measurements:
    def __init__(self):
        self.reset()

    def put_cpu_temp(self, value):
        meas = {"value": value, "ts": self.now_ts()}
        self.cpu_temp.append(meas)

    def put_rssi(self, value):
        meas = {"value": value, "ts": self.now_ts()}
        self.wfi_rssi.append(meas)

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
        self.cpu_temp = []
        self.wfi_rssi = []

    async def publish(self):
        print("Publishing data")
        await mqtt.publish(["gas", "eco2"], self.prepare_eco2_data())
        await mqtt.publish(["gas", "tvoc"], self.prepare_tvoc_data())
        await mqtt.publish(["gas", "ohm"], self.prepare_bme680gas_ohm_data())
        await mqtt.publish(["gas", "aqi"], self.prepare_bme680gas_aqi_data())
        await mqtt.publish(["humidity"], self.prepare_hum_data())
        await mqtt.publish(["temperature"], self.prepare_temp_data())
        await mqtt.publish(["pressure"], self.prepare_pressure_data())
        await mqtt.publish(["pm"], self.prepare_pm_data())
        await mqtt.publish(["system", "battery"], self.prepare_battery_data())
        await mqtt.publish(["system", "cpu_temp"], self.prepare_cpu_temp_data())
        await mqtt.publish(["system", "wifi"], self.prepare_rssi_data())
        self.reset()

    def prepare_cpu_temp_data(self):
        data_points = []

        for data in self.wfi_rssi:
            data_points.append({
                "sensor": "cpu",
                "temperature": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_rssi_data(self):
        data_points = []

        for data in self.wfi_rssi:
            data_points.append({
                "sensor": "wifi",
                "rssi": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_battery_data(self):
        data_points = []

        for data in self.battery_voltage:
            data_points.append({
                "sensor": "system",
                "voltage": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_pm_data(self):
        # value is {'pm100': 0.9, 'pm10': 0.3, 'pm25': 0.9}
        data_points = []

        for data in self.pm_data:
            data_points.append({
                "sensor": "pmsa003i",
                "ts": data["ts"],
                "pm10.0": data["value"]["pm100"],
                "pm2.5": data["value"]["pm25"],
                "pm1.0": data["value"]["pm10"],
            })

        return data_points

    def prepare_bme680gas_ohm_data(self):
        data_points = []

        for data in self.bme680_gas:
            data_points.append({
                "sensor": "bme680",
                "ohm": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_bme680gas_aqi_data(self):
        data_points = []

        for data in self.bme680_gas_aqi:
            data_points.append({
                "sensor": "bme680",
                "aqi": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_pressure_data(self):
        data_points = []

        for data in self.bme280_pres:
            data_points.append({
                "sensor": "bme280",
                "pressure": data["value"],
                "ts": data["ts"]
            })

        for data in self.bme680_pres:
            data_points.append({
                "sensor": "bme680",
                "pressure": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_temp_data(self):
        data_points = []

        for data in self.bme280_temp:
            data_points.append({
                "sensor": "bme280",
                "temperature": data["value"],
                "ts": data["ts"]
            })

        for data in self.bme680_temp:
            data_points.append({
                "sensor": "bme680",
                "temperature": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_hum_data(self):
        data_points = []

        for data in self.bme280_hum:
            data_points.append({
                "sensor": "bme280",
                "humidity": data["value"],
                "ts": data["ts"]
            })

        for data in self.bme680_hum:
            data_points.append({
                "sensor": "bme680",
                "humidity": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_eco2_data(self):
        data_points = []

        for data in self.sgp30_eco2:
            data_points.append({
                "sensor": "sgp30",
                "eco2": data["value"],
                "ts": data["ts"]
            })

        return data_points

    def prepare_tvoc_data(self):
        data_points = []

        for data in self.sgp30_tvoc:
            data_points.append({
                "sensor": "sgp30",
                "tvoc": data["value"],
                "ts": data["ts"]
            })

        return data_points

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
