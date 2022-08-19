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
    "to": "example@hotmail.com"
}
```
