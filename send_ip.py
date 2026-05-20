#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import os
from time import sleep
import json
import sys
import subprocess


def _format_addr(s: str):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def _ping(host: str, count: int = 3):
    """
    ping a host for limited times
    """
    return os.system('ping {} -c {} >> /dev/null'.format(host, count))


def get_ipv4_addr(interface: str):
    """
    Get IPv4 addresses of a specified network interface using system command `ip`.

    Example command:
        ip -4 addr show dev eth0
    """
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show", "dev", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
    except FileNotFoundError:
        raise RuntimeError("Command `ip` not found. Please install iproute2.")

    if result.returncode != 0:
        return []

    ipv4_addrs = []

    for line in result.stdout.splitlines():
        line = line.strip()

        if line.startswith("inet "):
            # Example:
            # inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0
            addr_with_prefix = line.split()[1]
            addr = addr_with_prefix.split("/")[0]
            ipv4_addrs.append(addr)

    return ipv4_addrs


def write_selected_ipv4_addrs(ip_file: str, interfaces: list):
    """
    Write selected interfaces' IPv4 addresses to file.
    """
    with open(ip_file, "w", encoding="utf-8") as f:
        for interface in interfaces:
            ipv4_addrs = get_ipv4_addr(interface)

            for addr in ipv4_addrs:
                f.write(f"{interface}: {addr}\n")


if __name__ == "__main__":
    assert len(sys.argv) >= 2, '[ERROR]: No config file. '
    config_file = sys.argv[1]

    with open(config_file) as f:
        config: dict = json.load(f)

    from_addr = config.get('from', '')
    password = config.get('password', '')
    to_addr = config.get('to', '')
    smtp_server = config.get('server', '')

    ip_file = '/etc/sendip/.hostname'

    # 在这里指定需要导出的网卡名称
    # 可以根据实际情况修改，例如 ["eth0", "wlan0", "eno1"]
    interface_list = [
        "eth0",
        "wlan0",
        "oray_vnc",
    ]

    assert _ping(smtp_server) == 0, 'Network connection failed. '

    # 获取指定网卡的 IPv4 地址并写入文件
    write_selected_ipv4_addrs(ip_file, interface_list)

    # 显示当前文件内容和实时查询结果的差异，可选
    # 如果不需要，可以删除这一行
    os.system("cat " + ip_file)

    with open(ip_file, "r", encoding="utf-8") as f:
        ip_content = f.read()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)

    msg = MIMEText(ip_content, 'plain', 'utf-8')
    msg['From'] = _format_addr(from_addr)
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header('rpi system ip', 'utf-8').encode()
    server.sendmail(from_addr, [to_addr], msg.as_string())

    server.quit()