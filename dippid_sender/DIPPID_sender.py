import socket
import time
import random
import math
import random
import json

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#cooldown for sending button_01 data
cooldown_button_1 = 3
#state of button_01, either 0 or 1
button_1 = 0

#Values for the accelerometer
acc_axis_x = 0
acc_axis_y = 0
acc_axis_z = 0

while True:
    #logic for button_01
    if cooldown_button_1 == 0:
        if button_1 == 0:
            message = '{"button_1" : ' + str(0) + '}'
            sock.sendto(message.encode(), (IP, PORT))
            button_1 = 1
        else:
            message = '{"button_1" : ' + str(1) + '}'
            sock.sendto(message.encode(), (IP, PORT))
            button_1 = 0
        cooldown_button_1 = random.randrange(100,1000)
    else:
        cooldown_button_1 -= 1
    
    #logic for accelerometer
    #Create diverse sine waves, scale them up by three to make them look better on a visualizer
    acc_axis_x = round(math.sin(2*math.pi*time.time()), 10)*3
    acc_axis_y = round(math.sin(2*math.pi*time.time()*2), 10)*3
    acc_axis_z = round(math.sin(2*math.pi*time.time()*3), 10)*3
    #Put the axis data into a dict
    acc_data = {
        'x': acc_axis_x,
        'y': acc_axis_y,
        'z': acc_axis_z
    }
    #Properly setup the data into a message with json
    acc_message = '{"accelerometer" : ' + str(json.dumps(acc_data)) + '}'
    sock.sendto(acc_message.encode(), (IP, PORT))

    time.sleep(0.01)
