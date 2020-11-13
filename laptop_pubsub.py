import paho.mqtt.client as mqtt
import PySimpleGUI as gui
import time
flag = 0

def getLayout1():
    return [[gui.Text("Welcome to Pet Observation APP! \nplease choose a following action:\n1. 'get status': to see if your pet is in the cage\n2. 'play music': to play a song to relax your pet\n3. 'visualize data': TBD\n4. 'send message': send a 32 character max message\n5. 'change zipcode': change zipcode to location of pet")],
            [gui.Text("Notifications: "), gui.Text(size=(75,1), key='-OUTPUT-')],
            [gui.Input(key='-IN-')],
            [gui.Button('Enter')]]

def getLayout2():
    return [[gui.Text("Enter message to send:")],
            [gui.Text("Notifications:"), gui.Text(size=(75,1), key='-OUTPUT-')],
            [gui.Input(key='-IN-')],
            [gui.Button('Enter')]]

def getLayout3():
    return [[gui.Text("Enter new zip code:")],
            [gui.Text("Notifications:"), gui.Text(size=(75,1), key='-OUTPUT-')],
            [gui.Input(key='-IN-')],
            [gui.Button('Enter')]]


window = gui.Window('Pet Observation App', getLayout1())

import threading
lock = threading.Lock()

# ALL subscribe callbacks here

## noise alert
def noise_alert(client, userdata, msg):
    noise = "A loud noise was detected, would you like to play music to calm the pet? Type play music"
    window['-OUTPUT-'].update(noise)
    

## location request
def print_location(client, userdata, msg):
    location = str(msg.payload, "utf-8")
    location1 = "Pet is " + location
    window['-OUTPUT-'].update(location1)
    print("Response: Pet is " + location)


## weather alert
def weather_alert(client, userdata, msg):
    notif = "A storm may be coming in your area, would you like to play calming music? Type play music"
    window['-OUTPUT-'].update(notif)


#general MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with the following result "+str(rc))
    
    #all subscriptions
    client.subscribe("petStat/sound")
    client.message_callback_add("petStat/sound", noise_alert)

    client.subscribe("petStat/location")
    client.message_callback_add("petStat/location", print_location)   

    client.subscribe("petStat/weather")
    client.message_callback_add("petStat/weather", weather_alert)
    

def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def publish_bank(key):
    #go through and execute different publishes based on the key entered

    if key == 'status':
        client.publish("petStat/request")
    elif key == 'visualize':
        client.publish("petStat/request")
    elif key == 'music':
        client.publish("petStat/play_music")

def sendMess(message):
    client.publish("petStat/message", message)
    flag = 0

def sendZip(zip):
    client.publish("petStat/zipcode",zip)
    flag = 0

if __name__ == '__main__':
    #create MQTT connection
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True: 
        event, values = window.read()
        print(values)
        if event == gui.WIN_CLOSED:
            break
        if flag == 0:
            if event == 'Enter':
                if values['-IN-'] == 'send message':
                    print("hello")
                    flag = 1
                    window.close()
                    window = gui.Window('Pet Observation App Message Screen', getLayout2())
                elif values['-IN-'] == 'get status':
                    publish_bank('status')
                elif values['-IN-'] == 'play music':
                    publish_bank('music')
                elif values['-IN-'] == 'change zipcode':
                    flag = 2
                    window.close()
                    window = gui.Window('Pet Observation App Zipcode Change', getLayout3())
        elif flag == 1:
            if event == 'Enter':
                sendMess(values['-IN-'])
                flag = 0
                window.close()
                window = gui.Window('Pet Observation App', getLayout1())
        else:
            if event == 'Enter':
                sendZip(values['-IN-'])
                flag = 0
                window.close()
                window = gui.Window('Pet Observation App', getLayout1())

    while True: time.sleep(1)
