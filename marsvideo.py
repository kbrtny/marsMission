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

background = ("/home/pi/Documents/mars/MtM-transparent-white.png")
countdown = ("/home/pi/Documents/mars/countdown.mp4")
introboost = ("/home/pi/Documents/mars/Intro_video_boost.mp4")
intro = ("/home/pi/Documents/mars/Intro_video_no_boost.mp4")
after = ("/home/pi/Documents/mars/aftershow.mp4")

backgroundload = ["feh",
                  "-Y",
                  "-x",
                  "-q",
                  "-B", "black",
                  "-F", background]

menus = ["Start Game",
         "Start Boost Game",
         "Start Inf Game",
         "Start Inf Boost Game",
         "Stop Game"]

class Videoplayer:
    def __init__(self):
        self.logic_state = 0
        self.boost = 0
        self.infinite = 0
        self.game_state = 99
        self.is_menu = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(game_start, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(boost_active, GPIO.OUT, initial=GPIO.LOW)

        GPIO.setup(button_1, GPIO.IN)
        GPIO.setup(button_2, GPIO.IN)
        GPIO.setup(button_3, GPIO.IN)
        GPIO.setup(button_4, GPIO.IN)
        
        GPIO.add_event_detect(button_1, GPIO.FALLING, callback=self.button_callback)
        GPIO.add_event_detect(button_2, GPIO.FALLING, callback=self.button_callback)
        GPIO.add_event_detect(button_3, GPIO.FALLING, callback=self.button_callback)
        GPIO.add_event_detect(button_4, GPIO.FALLING, callback=self.button_callback)
        
        self.player = OMXPlayer(after, 
            dbus_name='org.mpris.MediaPlayer2.omxplayer1')
        self.player.stop()
        
        self.mylcd = I2C_LCD_driver.lcd()
        self.mylcd.lcd_clear()

        self.image = Popen(backgroundload)

    def am_i_playing(self):
        try:
            if self.player.is_playing():
                return 1
            else:
                return 0
        except:
            return 0

    def wait_for_video(self):
        time.sleep(1)
        play_state = self.am_i_playing()
        while play_state:
            play_state = self.am_i_playing()

    def main_menu(self):
        # print("Main Menu")
        self.mylcd.lcd_clear()
        time.sleep(.1)
        for i in range(1, 5):
            self.update_display(i-1, i, 0)
            time.sleep(.1)
        GPIO.output(game_start, 0)
        GPIO.output(boost_active, 0)
        self.is_menu = 1

    def start_game(self, channel):
        # print(str(channel))
        self.update_display(4, 1, 1)
        self.logic_state=1
        if channel == button_1:
            self.boost = 0
            self.infinite = 0
        elif channel == button_2:
            self.boost = 1
            self.infinite = 0
        elif channel == button_3:
            self.boost = 0
            self.infinite = 1
        elif channel == button_4:
            self.boost = 1
            self.infinite = 1
        self.game_state = 0
        self.is_menu = 0

    def stop_game(self):
        self.logic_state = 0
        self.game_state = -1
        if self.infinite == 0:
            self.player.stop()
        self.main_menu()
        

    def get_logic_state(self):
        return self.logic_state

    def update_display(self,entry, line, clear):
        if clear:
            self.mylcd.lcd_clear()
        self.mylcd.lcd_display_string(menus[entry], line, 0)

    def button_callback(self, channel):
        if self.get_logic_state():
            self.stop_game()
        else:
            self.start_game(channel)

    def state_machine(self):
        # print(videoplayer.game_state)
        if self.game_state == 0:
            if self.infinite:
                # print("Infinite")
                GPIO.output(game_start, 1)
                if self.boost:
                    GPIO.output(boost_active, 1)
                self.game_state = -1
            else:
                self.game_state = 1
                # print("Single")
                if self.boost:
                    # print("Boost")
                    self.player.load(introboost)
                else:
                    # print("Normal")
                    self.player.load(intro)
                time.sleep(1)
                
        elif self.game_state == 1:
            if self.am_i_playing() == 0:
                self.game_state = 2
                GPIO.output(game_start, 1)
                if self.boost:
                    GPIO.output(boost_active, 1)
                self.player.load(countdown)
                time.sleep(1)
                
        elif self.game_state == 2:
            if self.am_i_playing() == 0:
                self.game_state = 3
                GPIO.output(game_start, 0)
                GPIO.output(boost_active, 0)
                self.player.load(after)
                time.sleep(1)
                
        elif self.game_state == 3:
            if self.is_menu == 0:
                self.main_menu()
                self.game_state = -1

def main():
    videoplayer = Videoplayer()
    buttons = 0
    videoplayer.main_menu()
    while buttons != 20:
        time.sleep(.2)
        if GPIO.input(button_4):
            buttons = 0
        else:
            buttons += 1
        videoplayer.state_machine()    
    GPIO.cleanup()
    videoplayer.mylcd.lcd_clear()
    videoplayer.image.kill()
    if videoplayer.am_i_playing():
        videoplayer.player.stop()


if __name__ == "__main__":
    main()


