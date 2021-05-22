from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
from adafruit_ntp import NTP
from digitalio import DigitalInOut
import board
import busio
import tasko
import time

# Get wifi details and more from a config.py file
try:
    from config import config
except ImportError:
    print("WiFi config is kept in config.py, please add them there!")
    raise

wifi = None
esp32_cs = DigitalInOut(board.D13)
esp32_reset = DigitalInOut(board.D12)
esp32_ready = DigitalInOut(board.D11)
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)


def init(status_light):
    global wifi

    wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(
        esp, config, status_light)
    # wifi.reset()
    wifi.connect()
    print("WiFi started and connected!")


def get_esp():
    return esp


def get_rssi():
    # wifi signal
    rssi = -120
    if (wifi.esp.is_connected):
        rssi = wifi.signal_strength()
    return rssi


def set_time():
    ntp = NTP(esp)
    while True:
        try:
            ntp.set_time()
            if not ntp.valid_time:
                time.sleep(1)
                continue
            current_time = time.time()
            print("NTP Time set! Seconds since Jan 1, 1970: {} seconds".format(
                current_time))
            return
        except (ValueError, RuntimeError) as e:
            print("Failed to fetch time, retrying: ", e)
            time.sleep(1)
            wifi.reset()
            wifi.connect()
            continue


async def async_set_time():
    retries = 0
    max_retries = 10
    ntp = NTP(esp)
    while True:
        retries = retries + 1
        if retries > max_retries:
            print("Too many NTP retries, bailing out!")
            return
        try:
            ntp.set_time()
            if not ntp.valid_time:
                await tasko.sleep(1)
                continue
            current_time = time.time()
            print("NTP Time set! Seconds since Jan 1, 1970: {} seconds".format(
                current_time))
            return
        except (ValueError, RuntimeError) as e:
            print("Failed to fetch time, retrying: ", e)
            wifi.reset()
            await tasko.sleep(5)
            wifi.connect()
            continue
