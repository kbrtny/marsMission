sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y feh libdbus-1-dev 
pip3 install omxplayer-wrapper

echo "@python3 /home/pi/Documents/marsMission/marsvideo.py" >> /home/pi/.config/lxsession/LXDE-pi/autostart
