
import paho.mqtt.client as mqtt

import grovepi as gp
from grove_rgb_lcd import *
import threading #we might use this, might not
lock = threading.Lock()
import pickle
import pygame
import time
import sys
import weather_api

sys.path.append('/home/pi/Dexter/GrovePi/Software/Python')
setText_norefresh(" ")
LCD_LINE_LEN = 16
lcd_input = ""
global lcd_flag
lcd_flag = 0
length = 0


#activity_file = 'active.pickle'

sound_sensor = 0
gp.pinMode(sound_sensor,"INPUT")

ranger = 3
temp = {}

dist=0
#setRGB(250,0,0)

#ALL subscribe callbacks here
##lcd message
##song playing
### subscribes that send to publishes

#pet location

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

def music_play(client, userdata, msg):
    pygame.mixer.init()
    pygame.mixer.music.load('part1.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        try:
            continue
        except KeyboardInterrupt:
            break

def print_message(client, userdata, msg):
    string = str(msg.payload, "utf-8")
    lcd_input = "  " + string
    print(lcd_input)
    length = len(lcd_input)
    with lock:
        setRGB(200,0,0)
        setText_norefresh("NEW MESSAGE")
        for j in range (0,1):
            for i in range (0, length+1):
                setText_norefresh("\n" + lcd_input[i:i+LCD_LINE_LEN])
                time.sleep(0.5)
            dist = gp.ultrasonicRead(ranger)
        setRGB(0,255,0)
        setText_norefresh(string)
#general MQTT setup
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
    #creat MQTT connection
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    count = 0
    active = 0
    #temp = {}
    #pickle_init()
    
    while True:
        #check a weather API either for thunderstorms or barometric pressure
        #publish weather update
        if count == 20:
            count = 0
            val = [weather_api.API]
            cache = val[0]['pressure']()
            if cache < 1000:
                client.publish('petStat/weather')
        
        #print(lcd_flag)
        if lcd_flag == 1:
            print("dick")
            lcd_flag = 0
            setRGB(200,0,255)
            #setText_norefresh("dickkkkkkkkkkkkk")
            with lock:
                setText_norefresh("NEW MESSAGE")
                for i in range (length):
                    setText_norefresh("\n" + lcd_input[i:i+LCD_LINE_LEN])
                    time.sleep(0.1)
                #setText_norefresh("pipi")
                #print(lcd_input)
                setRGB(0,0,0)



        
        #possibly check to say if dog is in bed
        #publish notification
        #distance = gp.ultrasonicRead(ranger)
        #print(distance)
        #if distance < 25:
            #active = 0
        #else:
            #active = 1
        
        #check sound levels
        with lock:
            sensor_value = gp.analogRead(sound_sensor)
        if sensor_value > 400:
            client.publish("petStat/sound",sensor_value)
        
        #print(temp)
        if (count % 10)==0:            #how to get actual time
            t = time.localtime()
            current_t = time.strftime("%H:%M:%S", t)
            # current_t would be something like 08:45:23
            temp[current_t] = str(active)
            
        time.sleep(.1)
        count = count + 1
        
