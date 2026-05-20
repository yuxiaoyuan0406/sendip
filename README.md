# send ip service

usage:

```bash
chmod a+x copy.sh
sudo copy.sh
```

edit file `/etc/sendip/email.json`  
for example

```json
{
    "from": "example@example.com",
    "password": "password",
    "server": "smtp.example.com", 
    "to": "example@hotmail.com",
    "interfaces": ["eth0", "wlan0"]
}
```
 
`interfaces` is used to specify which network interfaces shold be cheched.

For example, use `["eth0"]` for wired network only, or use `["wlan0"]` for wireless network only.

The program will only send IPv4 addressed of the interfaces listed in `interfaces`.
