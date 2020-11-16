## MQTT Import
import paho.mqtt.client as mqtt

## Grovepi Imports

import grovepi as gp
from grove_rgb_lcd import *
import threading
lock = threading.Lock()

## Import used for playing music from mp3 file included in repository

import pygame

## General Imports

import time
import sys

## Our Weather App, using data from WeatheStack

import weather_api

sys.path.append('/home/pi/Dexter/GrovePi/Software/Python')

## Clear lcd screen

setText_norefresh(" ")


## If you have a half working LCD like me you can set this to 8, otherwise 16
LCD_LINE_LEN = 16

## Initialize variables/sensors

sound_sensor = 0
gp.pinMode(sound_sensor,"INPUT")

ranger = 3
temp = {}

dist=0

## ALL subscribe callbacks here

## Location request callback - used when user just wants to obtain simple, instantaneous state of pet

def location_request(client, userdata, msg):
    print("request received")
    with lock:
        dist = gp.ultrasonicRead(ranger)
    print(dist)
    if dist < 30:
        locate = "in bed"
    else:
        locate = "not in bed"
    client.publish("petStat/location", locate)

## Music callback - used when user wants to play song to calm pet

def music_play(client, userdata, msg):
    pygame.mixer.init()
    pygame.mixer.music.load('part1.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        try:
            continue
        except KeyboardInterrupt:
            break

## LCD callback - prints message to RPI node when user wants to notify pet caretaker

def print_message(client, userdata, msg):
    string = str(msg.payload, "utf-8")
    lcd_input = "  " + string
    #print(lcd_input)
    length = len(lcd_input)
    with lock:
        setRGB(200,0,0)
        setText_norefresh("NEW MESSAGE")
        for j in range (0,1): # scrolls message
            for i in range (0, length+1):
                setText_norefresh("\n" + lcd_input[i:i+LCD_LINE_LEN])
                time.sleep(0.5)
            dist = gp.ultrasonicRead(ranger)
        setRGB(0,255,0)
        setText_norefresh(string) # display full message 

## General MQTT functions

def on_connect(client, userdata, flags, rc):
    print("Connected to broker with the following result "+str(rc))
    
    #all subscriptions
    client.subscribe("petStat/request")
    client.message_callback_add("petStat/request", location_request)

    client.subscribe("petStat/play_music")
    client.message_callback_add("petStat/play_music", music_play)

    client.subscribe("petStat/message")
    client.message_callback_add("petStat/message", print_message)

def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    ## Create MQTT connection
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()


    count = 0
    active = 0

    while True:
        '''
        Check a weather API either for thunderstorms or barometric pressure, then publish an update
        We don't want to constantly send API requests since it has a limit for the free trial
        For however often you want to call the API and check the whether, modify the if statement below
        By dividing the period you want (in seconds) by 0.1  For example, if you want to check the weather
        reading every thirty seconds, modify the if statement to check for 30/0.1 = 300
        '''
        
        if count == 30:
            #count = 0         # Reset the counter variable
            val = [weather_api.API]           # Retrieve the output from the AIP
            pressure = val[0]['pressure']()        # Parse the pressure output from the API, in millibars
            if pressure < 2000:                  # Only notify user if pressure is below a threshold that indicates a storm is coming
                client.publish('petStat/weather')
        
        ## Consistently publish pet's state real time. unlike the previous function, this is called every 30*0.1 = 3 seconds
        if( count % 30) == 0:
            with lock:
                distance = gp.ultrasonicRead(ranger)
            if distance < 25:
                active = 0
            else:
                active = 1
            client.publish("petStat/real_time", active)
        
        ## Check if sounds levels are high enough to indicate pet is in distress
        with lock:
            sensor_value = gp.analogRead(sound_sensor)
        if sensor_value > 400:
            client.publish("petStat/sound",sensor_value)
        
        ''' 
        The 2 lines below are important because they determine how often the above publish statements are called.
        time.sleep(0.1) is very close to the increment of time the while loops takes each time, so you can use
        this, along with the value of count, to determine how often you want to publish the pet's state or call
        the weather API
        '''
        
        time.sleep(.1)
        count += 1
    
    print("Closing Pet Observer App")        
