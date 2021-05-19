# this dict is formatted according to ESP32 needs, for wifi data al least

config = {
    'ssid': 'YOUR_WIFI',
    'password': 'somepassword',
    'timezone': "Europe/Rome",
    'mqtt_host': 'some.mqtt.broker',
    'mqtt_user': 'mqtt_username',
    'mqtt_pass': 'a_super_secret_mqtt_pass',
    'mqtt_root_topic': 'root_topic',
    'latitude': '90.000000',  # https://www.latlong.net/
    'longitude': '135.000000',
    'elevation': 42,  # used to correct pressure readings to sea level
}
