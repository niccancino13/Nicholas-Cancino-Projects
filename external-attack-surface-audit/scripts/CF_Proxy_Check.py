import ipaddress
from concurrent.futures import ThreadPoolExecutor
import dns.resolver

# Cloudflare's published ranges: https://www.cloudflare.com/ips/
CF_RANGES = [ipaddress.ip_network(n) for n in open("cloudflare_ips_v4.txt").read().split()]

# Query PUBLIC DNS on purpose -- corporate DNS returns internal answers (split-horizon)
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ["1.1.1.1"]

def zone_on_cloudflare(hostname: str) -> bool:
    zone = ".".join(hostname.split(".")[-2:])
    try:
        return any("ns.cloudflare.com" in r.to_text() for r in resolver.resolve(zone, "NS"))
    except Exception:
        return False

def classify(hostname: str):
    try:
        ips = [ipaddress.ip_address(r.to_text()) for r in resolver.resolve(hostname, "A")]
    except Exception:
        return hostname, "Does not resolve"
    if any(ip in net for ip in ips for net in CF_RANGES):
        return hostname, "PROXIED"
    if zone_on_cloudflare(hostname):
        return hostname, "DNS-only (origin exposed)"
    return hostname, "Not on Cloudflare"

with open("public_hostnames.txt") as f:
    hosts = [h.strip() for h in f if h.strip()]

with ThreadPoolExecutor(max_workers=30) as pool:
    for host, status in pool.map(classify, hosts):
        print(f"{host},{status}")
