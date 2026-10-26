# ftp-listener.ps1  — receive data exfiltrated over FTP
python -m pyftpdlib -p 21 -u user -w -d C:\ftproot --range 60000-60010
