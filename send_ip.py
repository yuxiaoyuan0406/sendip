#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import os
from time import sleep
import json
import sys

def _format_addr(s: str):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def _ping(addr: str):
    return os.system('ping {} -c 3 >> /dev/null'.format(addr))

if __name__ == "__main__":
    # sleep(20)

    assert len(sys.argv) >= 2, '[ERROR]: No config file. '
    config_file = sys.argv[1]

    with open(config_file) as f:
        config = json.load(f)
        # print(config)
    from_addr = config['from']
    password = config['password']
    to_addr = config['to']
    smtp_server = config['server']
    ip_file = '/etc/sendip/.hostname'

    assert _ping(smtp_server) is 0, 'Network connection failed. '

    os.system("hostname -I > "+ip_file)
    os.system("echo \"diff /etc/sendip/.hostname <(hostname -I)\" | bash")
    ip_file = open(ip_file)

    # '''
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)

    msg = MIMEText(ip_file.readline().replace(' ', '\n'), 'plain', 'utf-8')
    msg['From'] = _format_addr(from_addr)
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header('rpi system ip', 'utf-8').encode()
    server.sendmail(from_addr, [to_addr], msg.as_string())

    server.quit()
    # '''
    # print(ip_file.readline().replace(' ', '\n'))
    ip_file.close()
