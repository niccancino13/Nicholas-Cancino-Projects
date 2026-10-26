# Purple Team Evaluation of Endpoint Detection & Response (EDR)

A hands-on purple team project assessing **CrowdStrike Falcon**'s ability to **detect** and **block** adversary techniques, using the [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) framework mapped to the [MITRE ATT&CK](https://attack.mitre.org/) matrix. Conducted during a SOC internship at a healthcare organization.

> **Note on scope:** Employer and individual names have been generalized, and all credentials, internal IP addresses, and hostnames removed. This repo documents methodology and lessons learned, not any live environment.

---

## Goal

Measure how well the EDR catches and stops real attacker behavior across two technique categories — **lateral movement** and **data exfiltration** — then translate the results into findings for both a technical audience (SOC/vendor) and a business audience (leadership).

Every technique test was scored into one of three buckets:

| Result | Meaning |
|--------|---------|
| **Block** | Falcon actively stopped the technique from executing |
| **Detect** | Falcon generated an alert but did not stop it |
| **No Detect** | Technique ran with no alert — a visibility gap |

---

## What is Purple Teaming?

- **Red team** = offense (simulate attacks). **Blue team** = defense (detect and respond).
- **Purple team** = both working together: you *run* a known attack and immediately *check* whether the defense tooling saw it. It's a controlled, repeatable way to validate that your detections actually fire, instead of hoping they would.

**Atomic Red Team** provides small, single-technique "atomic" test scripts, each tied to a MITRE ATT&CK technique ID (e.g. `T1021.002`). You run the atomic, watch what the EDR does, and record the result.

---

## Lab Environment

Fully isolated lab so that live attack traffic never touched a production network.

| Component | Role |
|-----------|------|
| VirtualBox host-only network | Isolated segment connecting the VMs |
| Windows VM — "Attacker" | Launches the Atomic Red Team tests |
| Windows VM — "Target" | Victim host; runs the Falcon sensor |
| Cloud Linux droplet | External receiver, used to test exfiltration past a corporate proxy |

### Software & Tooling

- **Frameworks:** Atomic Red Team (ART), MITRE ATT&CK
- **EDR under test:** CrowdStrike Falcon
- **Packet capture:** Wireshark, `tshark`
- **Exfil listeners:** `ncat` (HTTP), `aiosmtpd` (SMTP), `pyftpdlib` (FTP)
- **Reporting:** `pdftoppm`, `pdftotext`, ReportLab, PIL (`ImageChops.difference` for auto-cropping screenshots)

Install Wireshark via winget:

```powershell
# install-wireshark.ps1
winget install --id WiresharkFoundation.Wireshark
```

---

## Techniques Tested

Grouped by ATT&CK tactic. Each links to the public ART documentation.

### Lateral Movement

| Technique | Name | Notable result |
|-----------|------|----------------|
| [T1021.002](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1021.002/T1021.002.md) | SMB / Windows Admin Shares | **Double-alert** — one alert named the atomic test, a second flagged the underlying command |
| [T1021.006](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1021.006/T1021.006.md) | Windows Remote Management (WinRM) | Detected |
| [T1021.003](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1021.003/T1021.003.md) | Distributed Component Object Model (DCOM) | **Blocked outright** by Falcon |
| [T1021.001](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1021.001/T1021.001.md) | Remote Desktop Protocol (RDP) | Detected (had been mislabeled as SSH in an earlier tracking sheet) |
| [T1047](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1047/T1047.md) | Windows Management Instrumentation (WMI) | Mixed — encoded-command variant flagged High |

### Exfiltration

| Technique | Name | Notable result |
|-----------|------|----------------|
| [T1048.003](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1048.003/T1048.003.md) | Exfiltration Over Unencrypted Non-C2 Protocol (ICMP, HTTP, SMTP, FTP) | Mix of detect/block; external tests used the cloud droplet |
| [T1048.002](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1048.002/T1048.002.md) | Exfiltration Over Asymmetric Encrypted Protocol | Blocked by corporate proxy; flagged for off-network retest |
| [T1567.002](https://github.com/redcanaryco/atomic-red-team/blob/master/atomics/T1567.002/T1567.002.md) | Exfiltration to Cloud Storage | Blocked by proxy; flagged for retest |

---

## Methodology / Steps Taken

1. **Build the lab** — stand up isolated Windows VMs on a VirtualBox host-only network plus a cloud receiver for external-destination tests.
2. **Select techniques** — pick ATT&CK techniques relevant to the environment (lateral movement + exfil), look them up in the ART index.
3. **Run the atomic** — execute each `Invoke-AtomicTest` on the attacker VM.
4. **Capture evidence** — record network traffic (Wireshark / listeners) and screenshot the Falcon console.
5. **Cross-reference** — match each run against Falcon's detections and record Block / Detect / No Detect.
6. **Document** — group screenshots by technique, tie each back to its ART reference, and write up findings.

ART index reference:
```
https://raw.githubusercontent.com/redcanaryco/atomic-red-team/master/atomics/Indexes/Indexes-Markdown/windows-index.md
```

---

## Code & Configs Written

All scripts below are also saved as separate files in [`scripts/`](scripts/).

### Exfiltration listeners

```powershell
# http-listener.ps1  — receive data exfiltrated over HTTP
ncat -lvp 80 > received_http.dat
# verify what landed:
Get-Item received_http.dat | Select-Object Name, Length
```

```powershell
# smtp-listener.ps1  — receive data exfiltrated over SMTP (prints messages to console)
python -m aiosmtpd -n -l 0.0.0.0:25
```

```powershell
# ftp-listener.ps1  — receive data exfiltrated over FTP
python -m pyftpdlib -p 21 -u user -w -d C:\ftproot --range 60000-60010
```

> **Gotcha:** `pyftpdlib` takes the password with `-P` (capital). Using `-p pass` is read as the *port* argument and fails with `invalid int value: 'pass'`.

### Generating a compressible test payload

A requirement was a **large** source file that zips down **small** (to demonstrate exfil of bulk data). Random bytes don't compress — repeating text does:

```powershell
# make-exfil-payload.ps1
"This is a fake file to test the exfil command for FTP" | Out-File C:\temp\exfil_test.7z
```

### Manual technique variant (WMI remote process creation)

Run when the packaged atomic couldn't complete due to lab resource limits:

```powershell
# wmi-remote-exec.ps1
Invoke-CimMethod -ClassName Win32_Process -MethodName Create `
  -Arguments @{ CommandLine = 'rundll32.exe shell32.dll,Control_RunDLL desk.cpl' }
```

---

## Problems Solved

- **"Allowed" ≠ "delivered."** Egress logs showed `action=allow`, but the sessions ended with `reason=incomplete` and `tcp-rst-from-server` — the TCP handshake never finished. The firewall permitted the *attempt* but the server reset the connection, so no data actually left. Learned to read the session-end reason, not just the allow/deny verdict.
- **PowerShell `&&` breaks in filter strings.** Replaced with `and`.
- **Corrupted output encoding.** PowerShell's `>` redirect writes UTF-16, which mangled captured payloads. Switched to `Out-File -Encoding ascii`.
- **Per-test argument names.** Each T1048.003 sub-test expects a *different* `-InputArgs` key (`ip_address`, `smtp_server`, `ftp_server`) — mixing them up silently fails the run.
- **FTP listener failures** traced to a folder-name typo (`ftprrot` vs `ftproot`) and a swapped password flag.
- **Choosing the right event identifier for vendor follow-up.** The Falcon **Detection ID** is the correct reference to hand CrowdStrike — a file hash (SHA256) identifies a *binary* not an *event*, PIDs get recycled, and MITRE IDs are behavioral *categories*, not specific detections.

---

## What I Learned

- **Blocked at egress is a real finding, not a test failure.** If the perimeter stops an exfil attempt, that's a win to document — not something to "work around."
- **Connectionless vs connection-based capture.** ICMP exfil can be seen with Wireshark alone; TCP-based protocols (HTTP/SMTP/FTP) need an active listener on the receiving end or the connection never completes.
- **Compression behavior is data-dependent** — repeating content shrinks dramatically, random content doesn't. Matters when demonstrating realistic data theft.
- **Detection tuning reveals itself in alert chains.** Some techniques fired *two* alerts at different severities (one on the atomic test name, one on the underlying command) — useful signal about how layered the detection logic is.
- **Translating for the audience matters.** The same results became a technical write-up for the SOC/vendor *and* a leadership deck framed around cost savings, security ROI, and layered defense.
- **Treat any credential shared in plaintext as compromised** and rotate it.

---

## Deliverables Produced

- Technical slide deck covering the purple team testing and an external asset audit, with a Blocked / Detected / Missed scorecard.
- Business-audience deck framing findings around security ROI and layered defense.
- Consolidated PDF report with screenshots grouped by technique, each linked to its ART reference.

---

## Skills Demonstrated

`MITRE ATT&CK` · `Atomic Red Team` · `CrowdStrike Falcon` · `EDR evaluation` · `PowerShell` · `Wireshark / tshark` · `Network exfiltration analysis` · `VirtualBox lab building` · `Firewall log analysis` · `Technical + executive reporting`
