<p align="center">
  <img src="https://npx-official.github.io/assets/logo.png" alt="NPX Framework" width="200"/>
</p>

<h1 align="center">🛡️ NPX Framework</h1>
<p align="center">
  <strong>Ultimate All-in-One Web Security Scanner</strong><br>
  <em>Penetration Testing • Security Research • Future Ready</em>
</p>

<p align="center">
  <a href="https://npx-official.github.io">
    <img src="https://img.shields.io/badge/Website-NIGHT%20PULSE%20X-0a0a0a?style=for-the-badge&logo=github&logoColor=white&color=0a0a0a" alt="Website"/>
  </a>
  <a href="https://github.com/npx-official/npx-framework">
    <img src="https://img.shields.io/github/stars/npx-official/npx-framework?style=for-the-badge&logo=github&color=0a0a0a" alt="GitHub stars"/>
  </a>
  <a href="https://github.com/npx-official/npx-framework/issues">
    <img src="https://img.shields.io/github/issues/npx-official/npx-framework?style=for-the-badge&logo=github&color=0a0a0a" alt="GitHub issues"/>
  </a>
  <a href="https://github.com/npx-official/npx-framework/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/npx-official/npx-framework?style=for-the-badge&logo=github&color=0a0a0a" alt="License"/>
  </a>
</p>

<p align="center">
  <b>Version:</b> v1.0 Ultimate &nbsp;|&nbsp; <b>Author:</b> NPX &nbsp;|&nbsp; <b>Website:</b> <a href="https://npx-official.github.io">NIGHT PULSE X</a>
</p>

---



## ⚠️ **Disclaimer**

> **🚨 This tool is intended for educational purposes, authorized security assessments, and penetration testing only.**
>
> The authors (NPX) and the community are **not responsible** for any illegal use, damage, or unauthorized access caused by this software. Always ensure you have explicit written permission from the target system owner before scanning.
>
> **⚠️ The tools are not complete yet, do not try them on real sites without proper authorization.**

---

## ✨ **Key Features**

NPX Framework combines the power of multiple well-known open-source techniques into one tool, featuring:

### 🔍 Reconnaissance Engine
- Extracts internal/external links, subdomains, JavaScript files
- Identifies backend technologies and server information
- Intelligent crawling with sitemap detection

### ⚡ Directory & File Bruteforce
- High-speed fuzzing with FFUF integration
- Discover hidden admin panels, backup files
- Configuration leaks (`.env`, `.git`, `.htaccess`)

### 💉 Injection Scanners
- **SQLi Engine:** Time-based & Error-based detection
- **XSS Detector:** Reflected XSS payload injection
- **LFI / RFI Scanner:** Local and Remote file inclusion with path traversal

### 🎯 Advanced Modules
- **WAF Bypass Engine:** Detects WAFs (Cloudflare, ModSecurity, etc.) and generates bypass payloads
- **SSRF Scanner:** Detects Server-Side Request Forgery (AWS Metadata, Internal services)
- **XXE Engine:** Detects XML External Entity injection vulnerabilities
- **Modern Web Scanning:** GraphQL introspection and WebSocket evaluation

### 🤖 Automated Exploitation
- **Post-Exploit Module:** Automatically dumps database tables via SQLi
- **Exploit Chain Builder:** Links multiple vulnerabilities (e.g., LFI → Log Poisoning → RCE)

### 🔑 Credential Harvesting & Hashcat
- Scrapes pages for API keys, JWTs, and passwords using regex patterns
- Integrates with `hashcat` to automatically crack discovered hashes

### ⚙️ Infrastructure & Automation
- **REST API:** Exposes an API endpoint (`/api/v1/scan`) to run scans remotely
- **Scheduler Engine:** Schedule automated scans via the CLI (`schedule add`)
- **SQLite Storage:** Saves all scan history locally in a database

---

## 📋 **Requirements**

### Python
- **Python:** 3.7 or higher
- **pip:** Python package manager

### Required Python Libraries
```bash
pip install requests beautifulsoup4 lxml dnspython pyjwt graphql-core
```

### External System Tools (Optional but recommended)
| Tool | Purpose | Installation |
|------|---------|--------------|
| **FFUF** | Directory bruteforce | `apt install ffuf` |
| **Nuclei** | CVE scanning | `apt install nuclei` |
| **Hashcat** | Password cracking | `apt install hashcat` |
| **Amass** | Subdomain enumeration | `apt install amass` |

---

## 🚀 **Installation & Usage**

### 1. Clone the repository
```bash
git clone https://github.com/npx-official/npx-framework.git
cd npx-framework
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Framework
```bash
python3 npx_framework.py
```
*(To set a target directly upon launch: `python3 npx_framework.py https://target.com`)*

---

## 🎮 **CLI Commands Overview**

Once launched, you will be greeted with the interactive NPX CLI. Type `help` to see all commands.

| Command | Description |
| :--- | :--- |
| `scan <url>` | **Crucial:** Starts a full reconnaissance and vulnerability scan |
| `scan <url> --fast` | Fast scan (fuzzer, SQLi, XSS, LFI only) |
| `modules` | Lists all available attack modules |
| `report` | Generates an HTML report from the last scan |
| `nuclei <url>` | Runs an external CVE scan using Nuclei |
| `bypass` | Runs the WAF bypass engine |
| `chain` | Builds exploit chains from discovered vulnerabilities |
| `ssrf` | Executes the SSRF scanner |
| `xxe` | Executes the XXE scanner |
| `lfi` | Executes the LFI scanner |
| `postexploit` | Runs the post-exploitation module |
| `api` | Starts a Flask-based REST API server on port `8080` |
| `cloud <domain>` | Scans cloud resources (AWS S3, Azure, GCP) |
| `dns <domain>` | DNS reconnaissance (zone transfer, subdomains) |
| `graphql <url>` | GraphQL introspection |
| `jwt <token>` | JWT decoder and analyzer |
| `schedule add <url> <seconds>` | Schedules an automated scan |
| `schedule list` | Displays all scheduled jobs |
| `history` | Displays scan history from SQLite database |
| `info` | Displays current configuration |
| `clear` | Clears the terminal screen |
| `exit` | Exits the NPX Framework |

---

## 🎯 **How to Test a Specific Vulnerability (Single Point Test)**

While the NPX Framework is built for **broad automated scans**, you can easily use it to test a specific vulnerability on a single endpoint.

### Option 1: Using the NPX Framework for a Targeted URL
```bash
npx> scan http://example.com/page.php?id=1
```
The framework will:
1. Extract only that endpoint
2. Fuzz for directories/backups relative to that URL
3. Test the `id` parameter specifically against **SQLi, XSS, and LFI** payloads

### Option 2: Manual `curl` Check (The Quickest Way)
**Test for Local File Inclusion (LFI):**
```bash
curl "http://example.com/page.php?id=../../../../etc/passwd"
```
*(If you see `root:x:0:0:`, the LFI exists).*

**Test for Reflected XSS:**
```bash
curl "http://example.com/page.php?id=<script>alert('NPX')</script>"
```
*(If the output contains the full script tag, it's reflecting).*

**Test for Open Redirect:**
```bash
curl -I "http://example.com/redirect.php?url=https://evil.com"
```
*(Check the `Location:` header for `evil.com`).*

---

## 📊 **Generating a Report**

After running a scan (`scan http://target.com`), simply run the `report` command:

```bash
npx> report
```

The framework will save files in `scan_results/reports/`:
- **HTML Report:** Professional dark-themed security assessment
- **JSON Report:** Raw data for further analysis

---

## 🏆 **Featured Writeups & Projects**

### 🔥 From NIGHT PULSE X

| Project | Description |
| :--- | :--- |
| **Mythical** | 🏆 HTB ProLabs |
| **Puppet** | 🏆 HTB ProLabs |
| **DarkZero Returns** | HTB Windows Hard |
| **Fries** | HTB Windows Hard |
| **Garfield** | HTB Windows Hard |
| **Ghostlink** | HTB Windows Hard |
| **H1 2022 CTF** | 🛡️ Hacker101 CTF |
| **Nimbus** | 🐧 HTB Linux Hard |
| **Odyssey** | 💀 HTB Windows Insane |

### 📂 Featured Projects
- **Linux Machines:** 18+ Writeups
- **Windows Machines:** 2 Writeups
- **ProLabs:** 1 Writeup

---

## 🗂️ **Project Structure**

```
npx-framework/
├── npx_framework.py          # Main entry point
├── cli.py                    # CLI interface
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
│
├── core/                     # Core components
│   ├── colors.py            # Terminal colors
│   ├── config.py            # Configuration
│   ├── session.py           # Session management
│   ├── recon.py             # Reconnaissance engine
│   └── scheduler.py         # Task scheduler
│
├── modules/                  # Attack modules
│   ├── chain.py             # Exploit chain builder
│   ├── cloud_enum.py        # Cloud enumeration
│   ├── credential.py        # Credential harvesting
│   ├── dns_recon.py         # DNS reconnaissance
│   ├── exploit.py           # Auto exploitation
│   ├── fuzzer.py            # Directory bruteforce
│   ├── graphql_enum.py      # GraphQL enumeration
│   ├── hashcat.py           # Hashcat integration
│   ├── jwt_tools.py         # JWT tools
│   ├── lfi.py               # LFI scanner
│   ├── modern.py            # Modern web scanning
│   ├── nuclei.py            # Nuclei integration
│   ├── postexploit.py       # Post-exploitation
│   ├── sqli.py              # SQL injection
│   ├── ssrf.py              # SSRF scanner
│   ├── subdomain.py         # Subdomain takeover
│   ├── waf_bypass.py        # WAF bypass
│   ├── wordpress.py         # WordPress scanner
│   ├── xss.py               # XSS detector
│   ├── xss_exploit.py       # XSS exploitation
│   └── xxe.py               # XXE engine
│
├── utils/                    # Utilities
│   ├── helpers.py           # Helper functions
│   ├── storage.py           # Database storage
│   ├── report.py            # Report generation
│   ├── smart_helper.py      # Smart suggestions
│   └── updater.py           # Auto updater
│
├── api/                      # REST API
│   └── server.py            # Flask server
│
└── scan_results/             # Scan results (auto-generated)
    ├── reports/             # HTML/JSON reports
    ├── scans/               # Scan JSON files
    ├── logs/                # Log files
    ├── nuclei/              # Nuclei results
    ├── ffuf/                # FFUF results
    └── temp/                # Temporary files
```

---

## 🤝 **Contributing**

We welcome contributions! If you'd like to contribute to NPX Framework:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write clear commit messages
- Update documentation as needed
- Add tests for new features

---

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Credits**

Built with ❤️ by **NPX**

### Special Thanks
- All contributors and testers
- Open-source community for amazing tools and libraries
- HTB for providing realistic training environments

### Connect with Us
- **Website:** [NIGHT PULSE X](https://npx-official.github.io)
- **GitHub:** [npx-official](https://github.com/npx-official)
- **Writeups:** Featured writeups available on our website

---

<p align="center">
  <strong>NPX Framework</strong> — <em>Penetration Testing • Security Research • Future Ready</em>
</p>

<p align="center">
  <a href="https://npx-official.github.io">
    <img src="https://img.shields.io/badge/🌐%20NIGHT%20PULSE%20X-Visit%20Our%20Website-0a0a0a?style=for-the-badge&logo=github&logoColor=white&color=0a0a0a" alt="Website"/>
  </a>
</p>
```

