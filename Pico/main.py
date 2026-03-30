import network
import time
import urequests
from machine import ADC, Pin


WIFI_SSID = "Redmi Note 12"
WIFI_PASSWORD = "jijijiji" 

SERVER_IP_URL = "http://172.19.108.236:8000/" 

wifi_status = False

soil_sensor = ADC(28)

pump1 = Pin(16, Pin.OUT)
pump2 = Pin(20, Pin.OUT)

pump1.value(1)
pump2.value(1)

off_delay = 10

THRES  = 40000


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
    pump1.value(0)
    pump2.value(0)
    time.sleep(delay)
    pump1.value(1)
    pump2.value(1)


def control_pump(value, threshold, off_delay):
    if value > threshold:
        print("Soil is dry - Pump ON")
        motor_on(off_delay)
    else:
        print("Soil is wet - Pump OFF")
        pump1.value(1)
        pump2.value(1)


def send_data(data):

    payload = {
        "moisture": data
    }

    url = SERVER_IP_URL + "api/gardensensor/"
    
    print(url)

    r = None

    try:
        print(payload)
        r = urequests.post(url, json=payload , headers={"Content-Type": "application/json"})
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
    global THRES, off_delay
    
    while True:
        connect_wifi()

        soil = soil_data()
        
        pump_on = False

        if wifi_status:
            send_data(soil)
            data = get_data()
            
            if data:
                status = data.get("status")
                delay_hour = data.get("is_delay_hour")
                pump_on = data.get("pump_on")
                off_delay = data.get("off_delay" ,off_delay)
                threshold = data.get("threshold",THRES)

                THRES = threshold

                if status:
                    if delay_hour:
                        motor_on(off_delay)

        if pump_on:
            motor_on(off_delay)
        else:
            control_pump(soil, THRES, off_delay)

        time.sleep(0.5)


main()


