#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import os
import json
import sys
import subprocess


def _format_addr(s: str):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def _ping(host: str, count: int = 3):
    """
    Ping a host for limited times.
    """
    return os.system('ping {} -c {} >> /dev/null'.format(host, count))


def get_ipv4_addr(interface: str):
    """
    Get IPv4 addresses of a specified network interface using system command `ip`.

    Example:
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


def get_selected_ipv4_content(interfaces: list):
    """
    Generate the current IPv4 address content for selected interfaces.

    Output example:
        eth0: 192.168.1.101
        wlan0: 192.168.1.102
    """
    lines = []

    for interface in interfaces:
        ipv4_addrs = get_ipv4_addr(interface)

        for addr in ipv4_addrs:
            lines.append(f"{interface}: {addr}")

    return "\n".join(lines) + "\n"


def read_file_content(path: str):
    """
    Read file content. Return empty string if file does not exist.
    """
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file_content(path: str, content: str):
    """
    Write content to file.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def send_email(
    smtp_server: str,
    from_addr: str,
    password: str,
    to_addr: str,
    subject: str,
    content: str
):
    """
    Send email.
    """
    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)

    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(from_addr)
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


if __name__ == "__main__":
    assert len(sys.argv) >= 2, '[ERROR]: No config file.'

    config_file = sys.argv[1]

    with open(config_file, "r", encoding="utf-8") as f:
        config: dict = json.load(f)

    from_addr = config.get('from', '')
    password = config.get('password', '')
    to_addr = config.get('to', '')
    smtp_server = config.get('server', '')

    ip_file = '/etc/sendip/.hostname'
    pid_file = '/etc/sendip/sendip.pid'

    # 保存当前 Python 脚本进程 PID，等价于原 Bash 中的：
    # echo $$ > /etc/sendip/sendip.pid
    write_file_content(pid_file, str(os.getpid()) + "\n")

    # 在这里指定需要检查和导出的网卡
    # interface_list = [
    #     "eth0",
    #     "wlan0",
    # ]
    interface_list = config.get('interfaces', ["eth0", "wlan0"])

    assert _ping(smtp_server) == 0, 'Network connection failed.'

    old_ip_content = read_file_content(ip_file)
    new_ip_content = get_selected_ipv4_content(interface_list)

    if old_ip_content == new_ip_content:
        print("no need to update hostname")
        sys.exit(0)

    print("updating hostname")

    # 更新 /etc/sendip/.hostname
    write_file_content(ip_file, new_ip_content)

    # 发送邮件
    send_email(
        smtp_server=smtp_server,
        from_addr=from_addr,
        password=password,
        to_addr=to_addr,
        subject='rpi system ip',
        content=new_ip_content
    )