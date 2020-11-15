# Members: Baran Cinbis and Evan Hashemi
# Github Repo: https://github.com/evhashemi/Pet_Observation_APP

import paho.mqtt.client as mqtt
import PySimpleGUI as gui
import matplotlib.pyplot as plt
import time
import sys

## Flag for changing GUI when sending message
flag = 0

## Variables/arrays for storing pet activity data
global index
index = 0
activity = []
activity_times = []


## Layouts for GUI design
# General layout with all commands and notification display
def getLayout1():
    return [[gui.Text("Welcome to Pet Observation APP! \nPlease choose a following action:\n1. 'get status': See if your pet is in its bed\n2. 'play music': Play a song to relax your pet\n3. 'visualize data': See how active your pet has been over time\n4. 'send message': Send a 32 character max message")], # Where the actions are displayed
            [gui.Text("Notifications: "), gui.Text(size=(75,1), key='-OUTPUT-')], # where notifications are displayed (from MQTT updates)
            [gui.Input(key='-IN-')], # Where input is accepted
            [gui.Button('Enter')]] # Enter Button

# Specific layout for sending a message, still has space for notfications
def getLayout2():
    return [[gui.Text("Enter message to send:")], # Instruction
            [gui.Text("Notifications:"), gui.Text(size=(75,1), key='-OUTPUT-')], # Notification
            [gui.Input(key='-IN-')], # Input
            [gui.Button('Enter')]] # Enter

# Display window
window = gui.Window('Pet Observation App', getLayout1())


## Method specifically for storing activity levels
def store_data(inp):
    global index
    activity.append(int(inp)) # Add activity level to array
    t = time.localtime() # Grab Local Time
    current_t = time.strftime("%H:%M:%S", t) # Format Local TIme
    activity_times.append(current_t) # Track Time
    
    index += 1
    if index == 20: # ensures that the lists do not get too full or unmanageable
        index -= 1
        del activity[0]
        del activity_times[0]


## ALL subscribe callbacks here
# noise alert: Tells user that a noise (that breaks the threshold to be considered a bark) was detected
def noise_alert(client, userdata, msg):
    noise = "A loud noise was detected, would you like to play music to calm the pet? Type play music"
    window['-OUTPUT-'].update(noise)
    
# location request: Tells user if pet is in bed or not in bed
def print_location(client, userdata, msg):
    location = str(msg.payload, "utf-8")
    location1 = "Pet is " + location
    window['-OUTPUT-'].update(location1)
    print("Response: Pet is " + location)

# weather alert: Warns user of incoming storms that may affect pet
def weather_alert(client, userdata, msg):
    notif = "A storm may be coming in your area, would you like to play calming music? Type play music"
    window['-OUTPUT-'].update(notif)    

# Activity data: Continuously recieves activity levels (active or not) of pet
def real_time_data(client, userdata, msg):
    active = str(msg.payload, "utf-8")
    #print(active)
    store_data(active)
    


#general MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected to broker with the following result "+str(rc))
    
    #all subscriptions seen above
    client.subscribe("petStat/sound")
    client.message_callback_add("petStat/sound", noise_alert)

    client.subscribe("petStat/location")
    client.message_callback_add("petStat/location", print_location)   

    client.subscribe("petStat/weather")
    client.message_callback_add("petStat/weather", weather_alert)

    client.subscribe("petStat/real_time")
    client.message_callback_add("petStat/real_time", real_time_data)
    

def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))


## All MQTT publishes
# publish requests, and publish to play music
def publish_bank(key):
    # go through and execute different publishes based on the key entered

    if key == 'status': # Request to check if pet is active or not
        client.publish("petStat/request")
    elif key == 'music': # Publish info that user wants to play calming music to soothe dog
        client.publish("petStat/play_music")

# Publish method to send instructions or a not to the lcd of the RPI
def send_mess(message):
    client.publish("petStat/message", message)
    flag = 0


## Main function
if __name__ == '__main__':
    #create MQTT connection
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    ## Main loop
    while True:
        event, values = window.read() # Read values from the GUI input bar
        if event == gui.WIN_CLOSED: # Close GUI if x is pressed
            break
        ## This if statement differentiates between the two possible GUI windows
        if flag == 0: # We are in first GUI layout with all possible commands
            
            if event == 'Enter': # check for execution, then see what command was
                if values['-IN-'] == 'send message':
                    flag = 1
                    window.close() # Switch to window that specifically asks for message to be sent
                    window = gui.Window('Pet Observation App Message Screen', getLayout2())
                    
                elif values['-IN-'] == 'get status': # Check if pet is in bed or not
                    publish_bank('status')
                    
                elif values['-IN-'] == 'play music': # Play music to soothe pet
                    publish_bank('music')
                    
                elif values['-IN-'] == 'visualize data': # See pet activity levels over time
                    plt.plot(activity_times, activity)
                    plt.title('Pet Activity')
                    plt.xlabel('Time')
                    plt.ylabel('Activity Level')
                    plt.show()
                else:
                    window['-OUTPUT-'].update("please make sure to type one of the above commands")
                    
        elif flag == 1: # We are in second window to send message 
            if event == 'Enter':
                send_mess(values['-IN-']) # send message
                flag = 0
                window.close()
                window = gui.Window('Pet Observation App', getLayout1()) # After message sent, return to main GUI layout

    sys.exit(0) # if x is pressed on GUI, close entire program
