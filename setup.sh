#!/usr/bin
# For felica application setup.
sudo apt-get install libusb-dev python3-usb
pip install nfcpy
pip install requests
pip install python-dotenv
sudo adduser <USERNAME> plugdev
sudo sh -c 'echo SUBSYSTEM==\"usb\", ACTION==\"add\", ATTRS{idVendor}==\"054c\", ATTRS{idProduct}==\"06c1\", GROUP=\"plugdev\" >> /etc/udev/rules.d/nfcdev.rules'
sudo udevadm control -R
