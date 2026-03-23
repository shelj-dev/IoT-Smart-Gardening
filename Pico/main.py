import network
import time
import urequests
from machine import ADC, Pin


WIFI_SSID = "iot kids"
WIFI_PASSWORD = "bright kidoos" 

SERVER_IP_URL = "http://10.163.201.158:8000/" 

wifi_status = False

soil_sensor = ADC(28)

pump = Pin(15, Pin.OUT)

THRES  = 30000


def connect_wifi():
    global wifi_status

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        wifi_status = True
        print("WiFi connected:", wlan.ifconfig()[0])
        return

    print("Connecting to WiFi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    timeout = 5
    while timeout > 0 and not wlan.isconnected():
        print("Waiting for connection...")
        time.sleep(1)
        timeout -= 1

    wifi_status = wlan.isconnected()

    if wifi_status:
        print("WiFi connected:", wlan.ifconfig()[0])
    else:
        print("WiFi failed")


def soil_data():
    value = soil_sensor.read_u16()
    voltage = value * 3.3 / 65535
    print("Soil Moisture Raw:", value, "Voltage:", round(voltage, 2))
    return value

def motor_on(delay):
    pump.value(1)
    time.sleep(delay)
    pump.value(0)


def control_pump(value, threshold):
    if value > threshold:
        print("Soil is dry - Pump ON")
        motor_on()
    else:
        print("Soil is wet - Pump OFF")
        pump.value(0)


def send_data(data):

    payload = {
        "moisture": data
    }

    url = SERVER_IP_URL + "api/gardensensor/"
    
    print(url)

    r = None

    try:
        print(payload)
        r = urequests.post(url, json=payload)
        print("Server response:", r.text)

    except Exception as e:
        print("Send error:", e)

    finally:
        if r is not None:
            r.close()



def get_data():

    url = SERVER_IP_URL + "api/pump/"
    
    try:
        r = urequests.get(url)
        data = r.json()
        r.close()
        
        print(data)
        return data

    except Exception as e:
        print("Get error:", e)



def main():

    while True:
        connect_wifi()

        soil = soil_data()

        if wifi_status:
            send_data(soil)
            data = get_data()

            status = data.get("status")
            delay_hour = data.get("delay_hour")
            pump_on = data.get("pump_on")
            off_delay = data.get("off_delay")
            threshold = data.get("threshold")

            THRES = threshold

            if status:
                if delay_hour:
                    motor_on(off_delay)

            if pump_on:
                motor_on(off_delay)

        control_pump(soil, THRES)

        time.sleep(2)


main()

