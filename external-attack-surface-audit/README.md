# External Attack Surface Audit — F5 VIPs, EDR Coverage & Cloudflare Proxy Gaps

> Security Operations internship project in an enterprise environment.
> All hostnames, IP addresses, credentials, internal identifiers, and environment-specific findings have been removed or generalized. Problems below are described as methodology lessons, not as the state of any specific network.

## Overview

The goal was to answer three questions about everything the organization exposes to the internet across two data centers:

1. **What's actually external?** Inventory every internet-facing F5 load balancer virtual server (VIP) and the backend servers behind it.
2. **Are those servers protected?** Validate that each backend server has a CrowdStrike Falcon sensor installed.
3. **Is the front door shielded?** Check whether each public hostname is proxied through Cloudflare (orange cloud) or exposing the origin directly (grey cloud / not on Cloudflare).

Success meant traceable, evidence-backed deliverables — Excel workbooks and a presentation — that reflected real infrastructure state, not estimates.

**Scope:** external-facing VIPs only. Internal infrastructure was out of scope unless it surfaced as a finding.

## Tools & Environment

| Category | Tools |
|---|---|
| Workstation | Windows, PowerShell, Python (installed via `winget`) |
| Data sources | F5 BIG-IP virtual server reports (Excel exports, one per data center) |
| EDR | CrowdStrike Falcon API via [FalconPy](https://github.com/CrowdStrike/falconpy) (Hosts service, FQL filters; Discover/Assets as fallback) |
| CDN / WAF | Cloudflare — public DNS resolution against Cloudflare's published IP ranges, NS record checks, dashboard review |
| Python libraries | `falconpy`, `pandas`, `openpyxl`, `ipaddress`, `re`, `dnspython`, `concurrent.futures` / threading |
| Validation | `nslookup`, `curl`, `nmap` |
| Reporting | Excel (openpyxl-generated workbooks), PowerPoint (generated with `pptxgenjs`) |

## What I Did

### 1. Filtered F5 reports down to external-facing VIPs
- Parsed both data centers' F5 virtual server exports (VIP address column + pool member column).
- Used Python's `ipaddress` module to keep only publicly routable VIPs and drop RFC 1918 / loopback / reserved ranges.
- Extracted backend pool members (`name(ip)` format) with a regex so each VIP mapped to the actual servers behind it.

### 2. Checked CrowdStrike sensor coverage
- Built a FalconPy script that takes a list of hostnames/IPs, auto-detects whether each entry is a hostname, private IP, or public IP, and runs the matching FQL query (`hostname:`, `local_ip:`, or `external_ip:`).
- Pulled device details (OS, last seen, OU, site, containment status) into a CSV for every match, and flagged entries with no sensor as **Not in CrowdStrike**.
- Iterated to a v2 that does dual-field IP lookups (local + external) and adds a Discover/Assets API fallback with a **Match Method** column showing how each host was matched.

### 3. Assessed Cloudflare proxy protection
- Resolved every public hostname against **public DNS (1.1.1.1)** — not corporate DNS — and classified each one:
  - **PROXIED** — resolves to Cloudflare IP ranges (origin hidden)
  - **DNS-only** — zone is on Cloudflare but the record isn't proxied (origin IP exposed)
  - **Not on Cloudflare** — no Cloudflare involvement
  - **Does not resolve**
- Ran checks across 30 threads to get through dozens of domains quickly.

### 4. Validated "dead" infrastructure
- Probed hosts from **inside** the network to see whether entries that looked dead externally were actually alive.
- Ran `nmap` against VIPs that resolved publicly but showed no TCP 80/443, to confirm whether F5's DOWN status was accurate.
- Spot-checked script output by hand with `nslookup`, `curl`, and `nmap` before trusting any result.

### 5. Built the deliverables
- **Combined audit workbook** (8 sheets) covering both data centers, CrowdStrike coverage, and Cloudflare status.
- **Cloudflare results workbook** (13 sheets) with per-HTTP-status-code breakdowns.
- Every sheet follows the same standard: a yellow description bar in row 1, headers in row 2, frozen panes, autofilter, color-coded status cells, a legend for any coded values, and a plain-English **"What This Means"** column.
- **Presentation** for a non-technical business audience, framing results around cost and risk rather than technical detail.

## Code & Configs

All scripts live in [`scripts/`](scripts/):

| File | What it does |
|---|---|
| [`CScode.py`](scripts/CScode.py) | CrowdStrike sensor status checker (v1). Takes a file of hostnames/IPs (one per line), sends each to the right FQL lookup (`hostname:`, `local_ip:`, or `external_ip:`), and writes a timestamped CSV. |
| [`f5_external_filter.py`](scripts/f5_external_filter.py) | Core logic for filtering F5 exports down to publicly routable VIPs and extracting the backend pool members behind each one. |
| [`CF_Proxy_Check.py`](scripts/CF_Proxy_Check.py) | Core logic for classifying public hostnames as Proxied / DNS-only / Not on Cloudflare / Does not resolve, using public DNS across 30 threads. |
| [`validation_commands.ps1`](scripts/validation_commands.ps1) | Manual validation and cleanup commands (`nslookup`, `curl`, `nmap`) used to spot-check script output. |

Example usage of the CrowdStrike checker (credentials come from your Falcon API client and are never committed):

```powershell
python CScode.py -i <CLIENT_ID> -s <CLIENT_SECRET> -f hosts.txt -o .\output
```


## Problems I Solved

| Problem | What was happening | Fix |
|---|---|---|
| **Split-horizon DNS** | Corporate DNS returned internal VIPs, making hosts look reachable (or unreachable) in ways that didn't match the internet's view. | All public-exposure checks query a public resolver (1.1.1.1) explicitly. |
| **Checking the wrong layer** | Early runs searched CrowdStrike for F5 VIP addresses — but sensors live on backend servers, not the load balancer. | Parsed pool members out of the F5 reports and checked those servers instead. |
| **Stale IP matches** | The Falcon `external_ip:` filter only matches a host's *current* external IP, so lookups missed hosts whose IP had changed. | Prioritized hostname-based lookups; added dual local/external IP lookups and a Discover/Assets fallback with a "Match Method" column for transparency. |
| **F5 "DOWN" ≠ offline** | Load balancer health monitors only test one narrow thing, so a DOWN status can't be taken as proof a host is offline. | Validated status directly with `nmap` and `curl` instead of trusting the monitor. |
| **"Dead" can mean "only dead externally"** | A host that doesn't resolve publicly may still have internal DNS and be serving traffic. | Added an internal reachability check so "doesn't resolve" gets investigated instead of auto-ignored. |
| **Silent scope exclusions** | Marking servers "unsupported" for EDR without evidence can hide real coverage gaps. | Required a documented rationale for any incompatibility exception, separating genuinely unsupported platforms from sensors that just weren't deployed. |
| **Region mismatch** | API calls fail or return nothing if the client isn't pointed at the tenant's Falcon cloud region. | Set `base_url` explicitly on every FalconPy client (v1 only did this in the hostname path — fixed in v2). |
| **Unreadable reports** | Raw output was too technical for decision-makers. | Standardized workbook layout with plain-English explanation columns, legends, and summary tables; dropped chart-heavy sheets that added noise. |

## What I Learned

- **Trust, but verify the tool.** Every automated result got spot-checked by hand, because "obvious" conclusions (host is dead, server is protected) can be wrong until tested directly.
- **Know which layer you're auditing.** A load balancer, the servers behind it, and the DNS name in front of it are three different things with three different owners and risks.
- **DNS perspective matters.** What you see from inside the network isn't what an attacker sees. Always test from the attacker's vantage point.
- **Grey-cloud records are real exposure.** A DNS-only Cloudflare record leaks the origin IP, letting attackers bypass the WAF entirely.
- **Decommissioning is a security control.** Forgotten infrastructure that's still running is unmonitored attack surface — and wasted spend, which is often the angle that gets leadership's attention.
- **Write for the audience.** The same data needed two forms: detailed, traceable workbooks for engineers and a cost-and-risk story for business stakeholders.

## What I'd Improve Next

- Refactor the CrowdStrike script: the three lookup functions are ~95% identical and should collapse into one function that takes the FQL field as a parameter.
- Load API credentials from environment variables or a secrets vault instead of command-line arguments (which end up in shell history).
- Replace the hand-written private-IP regex with `ipaddress.ip_address(x).is_private` / `.is_global`.
- Use the Cloudflare API (where access allows) to pull proxy status directly instead of inferring it from DNS.
- Schedule the checks to run continuously so new exposure is caught as it appears, not once per audit.
