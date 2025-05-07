from DIPPID import SensorUDP
import time

PORT = 5700
sensor = SensorUDP(PORT)

def handle_button_press(data):
    if int(data) == 0:
        print('button released')
    else:
        print('button pressed')

def handle_acc(data):
    print(data)

sensor.register_callback('button_1', handle_button_press)
sensor.register_callback('accelerometer', handle_acc)

while True:
    time.sleep(60)