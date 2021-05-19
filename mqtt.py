from config import config
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import json
import tasko

mqtt_client = None


def init(esp):
    global mqtt_client

    MQTT.set_socket(socket, esp)
    mqtt_client = MQTT.MQTT(
        broker=config["mqtt_host"],
        username=config["mqtt_user"],
        password=config["mqtt_pass"],
        is_ssl=True
    )

    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_publish = on_publish


def on_connect(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")


def on_disconnect(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from MQTT Broker!")


def on_publish(client, userdata, topic, rc):
    print("A message has been published!")


def connect():
    print("Connecting to MQTT Broker...")
    mqtt_client.connect()


async def publish(topic_segments, payload):
    retries = 0
    max_retries = 5
    root = config["mqtt_root_topic"]
    topic = "/".join([root] + topic_segments)
    payload = json.dumps(payload)

    while True:
        retries = retries + 1
        if retries > max_retries:
            print("MQTT giving up publishing....")
            return False
        try:
            mqtt_client.publish(topic, payload)
            print("Published on mqtt topic %r, %r" % (topic, payload))
            return True
        except (RuntimeError, MQTT.MMQTTException) as e:
            print("MQTT publish error (%d): %r" % (retries, e))
            await tasko.sleep(5)
            try:
                mqtt_client.connect()
            except Exception as e_recon:
                print("Whoa, MQTT reconnect error...: %r" % e_recon)