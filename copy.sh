#!/bin/sh
sudo cp send_ip.py /usr/local/bin/
sudo cp sendip.service /usr/lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart sendip.service
systemctl status sendip.service
