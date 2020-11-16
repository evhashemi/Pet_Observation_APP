# Pet_Observation_APP
Team Members: Baran Cinbis, Evan Hashemi
Video Link:
External Libraries and how to install:
  pygame - used to play music, already preloaded in RPI >>> python3 -m pip install -U pygame --user
  PySimpleGUi - used to creat GUI >>> pip install PySimpleGUI
  matplotlib - used to plot pet activity over time >>> pip3 install matplotlib
  paho mqtt - mqtt connection >>> pip install paho-mqtt
  grovepi/lcd - access and control grovepi

Executing Instructions
1. Plug RPI into a display with speaker by means of HDMI connection, an amplifier through the audio port should also suffice but we could not test it due  to lack of access.
2. Plug the GrovePI sound sensor into port A0, the ultrasonic ranger into port D3, and the lcd into any of the i2C ports
3. Download and Run rpi_pet_pubsub.py on your RPI board
4. Download and Run laptop_pubsub.py on any computer
5. Begin interacting with program

Disclaimer: the weather API only goes off once for each run because it is a limited time API, if it is used too many times, the free trial will run out and the program will stop working. IF this happens, go into rpi_pet_pubsub.py and comment out lines 127-132 (the if statement that deals with the weather API)
