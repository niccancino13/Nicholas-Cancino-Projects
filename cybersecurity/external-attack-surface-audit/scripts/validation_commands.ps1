# De-duplicate a host list before feeding it to scripts
Get-Content hosts.txt | Sort-Object -Unique | Set-Content hosts_unique.txt

# Compare public vs. internal DNS answers for a host (split-horizon check)
nslookup <hostname> 1.1.1.1
nslookup <hostname>

# Check what a "dead" host actually returns
curl.exe -s -o NUL -w "%{http_code}" https://<hostname>

# Fast top-100 port scan on VIPs that resolve but showed no web ports
nmap -Pn -F -iL resolves_no_web.txt -oA nmap_validation
