# Nicholas Cancino — Projects

A collection of hands-on projects I've worked on across cybersecurity, IT, and cloud. Each project folder has its own README covering the goal, tools used, steps taken, problems solved, and what I learned.

> All employer names, hostnames, IP addresses, and credentials have been removed or generalized. These write-ups document methodology and lessons learned, not any live environment.

## Cybersecurity

| Project | Summary | Skills |
|---|---|---|
| [External Attack Surface Audit](cybersecurity/external-attack-surface-audit/) | Inventoried internet-facing F5 load balancer VIPs across two data centers, validated CrowdStrike EDR coverage on the servers behind them, and checked whether each public hostname was shielded by the Cloudflare proxy. | Python, FalconPy, Cloudflare, DNS, F5 BIG-IP, nmap, PowerShell, Excel reporting |
| [Purple Team EDR Evaluation](cybersecurity/purple-team-edr-evaluation/) | Ran Atomic Red Team tests mapped to MITRE ATT&CK in an isolated lab to measure whether CrowdStrike Falcon blocked, detected, or missed lateral movement and exfiltration techniques. | MITRE ATT&CK, Atomic Red Team, CrowdStrike Falcon, Wireshark, VirtualBox, PowerShell |

## Repository Layout

```
.
├── README.md
└── cybersecurity/
    ├── external-attack-surface-audit/
    │   ├── README.md
    │   └── scripts/
    └── purple-team-edr-evaluation/
        ├── README.md
        └── scripts/
```
