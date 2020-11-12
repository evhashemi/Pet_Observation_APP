import paho.mqtt.client as mqtt
import time

import threading
lock = threading.Lock()

valid_commands = ['get_status', 'play_music', 'visualize_data', 'send_message', 'change_zipcode']
print("Choose from following commands and hit enter: {}".format(valid_commands))
command = ''

def command_is_valid(inp):
    if inp in valid_commands:
        return True
    elif inp == "":
       x = 1    
    else:
        print('Valid commands are {}'.format(valid_commands))
        return False

# ALL subscribe callbacks here

## noise alert
def noise_alert(client, userdata, msg):
    noise = str(msg.payload, "utf-8")

    print("A noise of " + noise + " dB was detected, would you like to play calming music?  play_music ")

## location request
def print_location(client, userdata, msg):
    location = str(msg.payload, "utf-8")
    print("Response: Pet is " + location)


## weather alert
def weather_alert(client, userdata, msg):
    print("A storm may be coming in your area, would you like to play calming music?  Type play_music ")


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
    elif key == 'message':
        inp = input("Enter your message here: ")
        client.publish("petStat/message", inp)
    elif key == 'zip':
        inp = input("Enter your zipcode: ")
        client.publish("petStat/zipcode", inp)
    command = ''


if __name__ == '__main__':
    with lock:
    #create MQTT connection
        client = mqtt.Client()
        client.on_message = on_message
        client.on_connect = on_connect
        client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
        client.loop_start()

    #keyboard listener
    
    command = ""
    user_input = ""

    #print('Command: ')
    while command != 'quit' and command != 'q':
        while not command_is_valid(user_input):

            user_input = input()
            command = user_input
        if command == 'get_status':
            try:
                publish_bank("status")
                user_input = ""
            except Exception as e:
                print(e)
        elif command == "play_music":
            try:
                publish_bank("music")
                user_input = ""
            except Exception as e:
                print(e)
        elif command == "visualize_data":
            try:
                publish_bank("visualize")
                user_input = ""
            except Exception as e:
                print(e)
        elif command == "send_message":
            try:
                publish_bank("message")
                user_input = ""
            except Exception as e:
                print(e)
        elif command == "change_zipcode":
            try:
                publish_bank("zip")
                user_input = ""
            except Exception as e:
                print(e)
    #intro message
    #print statement with intro to the program and list of possible commands
    
    while True:
        time.sleep(1)