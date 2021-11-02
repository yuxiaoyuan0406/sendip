#!/bin/sh
sudo cp send_ip.py /usr/local/bin/
sudo cp sendip.service /etc/systemd/system/
sudo mkdir /etc/sendip -p
chmod a+x sendip_st*
sudo cp sendip_st* /etc/sendip/
sudo cp email.json /etc/sendip/
sudo systemctl daemon-reload
sudo systemctl restart sendip.service
systemctl status sendip.service
