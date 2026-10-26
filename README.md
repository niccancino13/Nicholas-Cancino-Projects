# Nicholas Cancino — Projects

A collection of hands-on projects I've worked on across cybersecurity, IT, and cloud. Each project has its own folder with a README covering the goal, tools used, steps taken, problems solved, and what I learned.

> All employer names, hostnames, IP addresses, and credentials have been removed or generalized. These write-ups document methodology and lessons learned, not any live environment.

## Projects

### 🛡️ [Cybersecurity Home Lab](cybersecurity-home-lab/)
A physical home lab built on surplus enterprise hardware (Dell Precision 5820, Xeon, 112 GB ECC) running Proxmox VE. Covers GPU passthrough for a self-hosted LLM, OPNsense firewalling, and Tailscale remote access, with a planned detection stack (Security Onion, Wazuh, Splunk) and an AI purple-team loop.
**Skills:** Proxmox, OPNsense, Tailscale, GPU passthrough, Linux, networking, IaC

### 🔍 [External Attack Surface Audit](external-attack-surface-audit/)
Inventoried internet-facing F5 load balancer VIPs across two data centers, validated CrowdStrike EDR coverage on the backend servers, and checked whether each public hostname was shielded by the Cloudflare proxy.
**Skills:** Python, FalconPy, Cloudflare, DNS, F5 BIG-IP, nmap, PowerShell, Excel reporting

### 🟣 [Purple Team EDR Evaluation](purple-team-edr-evaluation/)
Ran Atomic Red Team tests mapped to MITRE ATT&CK in an isolated lab to measure whether CrowdStrike Falcon blocked, detected, or missed lateral movement and exfiltration techniques.
**Skills:** MITRE ATT&CK, Atomic Red Team, CrowdStrike Falcon, Wireshark, VirtualBox, PowerShell

## Repository Layout

```
.
├── README.md
├── cybersecurity-home-lab/
│   └── README.md
├── external-attack-surface-audit/
│   ├── README.md
│   └── scripts/
└── purple-team-edr-evaluation/
    ├── README.md
    └── scripts/
```
