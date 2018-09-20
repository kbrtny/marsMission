import sys
import os
from subprocess import Popen
import I2C_LCD_driver
import RPi.GPIO as GPIO
import time
from omxplayer.player import OMXPlayer
from pathlib import Path


game_start = 17
boost_active = 27
button_1 = 5
button_2 = 6
button_3 = 13
button_4 = 19
logic_state = 0

background = ("/home/pi/Documents/mars/MtM-transparent-white.png")
countdown = ("/home/pi/Documents/mars/countdown.mp4")
introboost = ("/home/pi/Documents/mars/Intro_video_boost.mp4")
intro = ("/home/pi/Documents/mars/Intro_video_no_boost.mp4")
after = ("/home/pi/Documents/mars/aftershow.mp4")

backgroundload = ["feh",
                  "--hide-pointer",
                  "-x",
                  "-q",
                  "-B", "black",
                  "-F", background]

menus = ["Start Game",
         "Start Boost Game",
         "Start Inf Game",
         "Start Inf Boost Game",
         "Stop Game"]

# Initialize GPIOs on RPi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(game_start, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(boost_active, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(button_1, GPIO.IN)
GPIO.setup(button_2, GPIO.IN)
GPIO.setup(button_3, GPIO.IN)
GPIO.setup(button_4, GPIO.IN)

# Create video player instance
player = OMXPlayer(after, 
        dbus_name='org.mpris.MediaPlayer2.omxplayer1')
player.stop()

# Initialize LCD display
mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_clear()

# Load the background image
image = Popen(backgroundload)

def am_i_playing():
    try:
        if player.is_playing():
            return 1
        else:
            return 0
    except:
        return 0

def wait_for_video():
    time.sleep(1)
    play_state = am_i_playing()
    while play_state:
        play_state = am_i_playing()

def main_menu():
    #print("Main Menu")
    logic_state = 0
    mylcd.lcd_clear()
    time.sleep(.1)
    for i in range(1, 5):
        update_display(i-1, i, 0)
        time.sleep(.1)
    GPIO.output(game_start, 0)
    GPIO.output(boost_active, 0)

def start_game(boost,infinite):
    if infinite:
        # print("Infinite")
        GPIO.output(game_start, 1)
    else:
        # print("Single")
        if(boost):
            # print("Boost")
            player.load(introboost)
        else:
            # print("Normal")
            player.load(intro)
        wait_for_video()
        
        GPIO.output(game_start, 1)
        if(boost):
            GPIO.output(boost_active, 1)
        player.load(countdown)
        wait_for_video()

        GPIO.output(game_start, 0)
        GPIO.output(boost_active, 0)
        player.load(after)
        wait_for_video()

        main_menu()

def update_display(entry, line, clear):
    if clear:
        mylcd.lcd_clear()
    mylcd.lcd_display_string(menus[entry], line, 0)

def button_1_callback(channel):
    global logic_state
    if logic_state:
        main_menu()
    else:
        update_display(4, 1, 1)
        logic_state=1
        start_game(0,0)

def button_2_callback(channel):
    global logic_state
    if logic_state:
        main_menu()
    else:
        update_display(4, 1, 1)
        logic_state=1
        start_game(1,0)

def button_3_callback(channel):
    global logic_state
    if logic_state:
        main_menu()
    else:
        update_display(4, 1, 1)
        logic_state=1
        start_game(0,1)

def button_4_callback(channel):
    global logic_state
    if logic_state:
        main_menu()
    else:
        update_display(4, 1, 1)
        logic_state=1
        start_game(1,1)

GPIO.add_event_detect(button_1, GPIO.FALLING, callback=button_1_callback)
GPIO.add_event_detect(button_2, GPIO.FALLING, callback=button_2_callback)
GPIO.add_event_detect(button_3, GPIO.FALLING, callback=button_3_callback)
GPIO.add_event_detect(button_4, GPIO.FALLING, callback=button_4_callback)

def main():
    buttons=0
    main_menu()
    while buttons!=8:
        time.sleep(1)
        if GPIO.input(button_4):
            buttons=0
        else:
            buttons+=1
    GPIO.cleanup()
    image.kill()
        

if __name__ == "__main__":
    main()
    

