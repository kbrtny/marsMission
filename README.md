# marsMission
simple video playback and game controller for the Mission to Mars game at San Diego Maker Faire 2018.

All you should need to do is clone this on a fresh Rasbian image (to a mars folder)
Then run raspi-config and enable i2c
Then run: chmod +x install.sh
and: chmod +x marsvideo.py
Finally: sudo ./install.sh

This will install all prerequisites, then add the python file to the rc.local which ensures that this loads at startup.
You will also need videos to use and a back-ground image.  One of the buttons is used as a quite by holding it down for 4 seconds.
