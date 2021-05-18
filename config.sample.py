# this dict is formatted according to ESP32 needs, for wifi data al least

config = {
    'ssid': 'YOUR_WIFI',
    'password': 'somepassword',
    'timezone': "Europe/Rome",
    'latitude': '90.000000',  # https://www.latlong.net/
    'longitude': '135.000000',
    'elevation': 42,  # used to correct pressure readings to sea level
}
