# smtp-listener.ps1  — receive data exfiltrated over SMTP (prints messages to console)
python -m aiosmtpd -n -l 0.0.0.0:25
