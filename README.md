```markdown
# 🛡️ NPX Framework - Ultimate All-in-One Web Security Scanner

> **Version:** v1.0 Ultimate | **Author:** NPX | **Website:** [https://npx-official.github.io/](https://npx-official.github.io/)

NPX Framework is an advanced, modular, and extensible Python-based penetration testing framework built specifically for web application security assessments. Designed to simulate a real attacker, it integrates intelligence gathering, vulnerability scanning, exploitation, WAF bypass, and post-exploitation into a single cohesive CLI environment.

---

## ✨ Key Features

NPX Framework combines the power of multiple well-known open-source techniques into one tool, featuring:

*   **🕵️ Reconnaissance Engine:** Extracts internal/external links, subdomains, JavaScript files, and identifies backend technologies.
*   **⚡ Directory & File Bruteforce:** High-speed fuzzing to discover hidden admin panels, backup files, and configuration leaks (`.env`, `.git`).
*   **💉 Injection Scanners:**
    *   **SQLi Engine:** Time-based & Error-based detection.
    *   **XSS Detector:** Reflected XSS payload injection.
    *   **LFI / RFI Scanner:** Local and Remote file inclusion with path traversal.
*   **🎯 Advanced Modules:**
    *   **WAF Bypass Engine:** Detects WAFs (Cloudflare, ModSecurity, etc.) and generates bypass payloads (Double encoding, Comment injection).
    *   **SSRF Scanner:** Detects Server-Side Request Forgery (AWS Metadata, Internal services).
    *   **XXE Engine:** Detects XML External Entity injection vulnerabilities.
    *   **Modern Web Scanning:** GraphQL introspection and WebSocket evaluation.
*   **🤖 Automated Exploitation:**
    *   **Post-Exploit Module:** Automatically dumps database tables via SQLi and uploads web shells via LFI (Log Poisoning).
    *   **Exploit Chain Builder:** Links multiple vulnerabilities (e.g., LFI → Log Poisoning → RCE).
*   **🔑 Credential Harvesting & Hashcat:**
    *   Scrapes pages for API keys, JWTs, and passwords using regex patterns.
    *   Integrates with `hashcat` to automatically crack discovered hashes using `rockyou.txt`.
*   **⚙️ Infrastructure & Automation:**
    *   **REST API:** Exposes an API endpoint (`/api/v1/scan`) to run scans remotely.
    *   **Scheduler Engine:** Schedule automated scans via the CLI (`schedule add`).
    *   **SQLite Storage:** Saves all scan history locally in a database (`npx_scan_history.db`) for later review.

---

## 📋 Requirements

*   **Python:** 3.7 or higher.
*   **pip:** Python package manager.

### Required Python Libraries:
```bash
pip install requests beautifulsoup4
```
*(Optional for advanced features: `flask` for REST API).*

### External System Tools (Optional but recommended):
*   **Hashcat:** For automated password cracking (`apt install hashcat`).
*   **Nuclei:** For advanced CVE scanning (`apt install nuclei`).

---

## 🚀 Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/npx-framework.git
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

## 🎮 CLI Commands Overview

Once launched, you will be greeted with the interactive NPX CLI. Type `help` to see all commands.

| Command | Description |
| :--- | :--- |
| `scan <url>` | **Crucial:** Starts a full reconnaissance and vulnerability scan against the target. |
| `modules` | Lists all available attack modules integrated into the framework. |
| `report` | Generates an HTML report (`npx_scan_report.html`) based on the last scan. |
| `nuclei <url>` | Runs an external CVE scan using the Nuclei engine (if installed). |
| `bypass` | Runs the WAF bypass engine against vulnerabilities found in the last scan. |
| `chain` | Attempts to build complex exploit chains based on discovered vulnerabilities (e.g., LFI to RCE). |
| `ssrf` | Executes the SSRF (Server-Side Request Forgery) scanner. |
| `xxe` | Executes the XXE (XML External Entity) scanner. |
| `postexploit` | Runs the post-exploitation module (Database dump, Shell upload). |
| `api` | Starts a Flask-based REST API server on port `8080`. |
| `schedule add <url> <seconds>` | Schedules an automated scan every X seconds. |
| `schedule list` | Displays all currently scheduled jobs. |
| `history` | Displays the scan history stored in the local SQLite database. |
| `info` | Displays the current configuration (target, threads, etc.). |
| `clear` | Clears the terminal screen. |
| `exit` | Exits the NPX Framework. |

---

## 🎯 How to Test a Specific Vulnerability (Single Point Test)

While the NPX Framework is built for **broad automated scans**, you can easily use it, or combine it with manual checks, to test a specific vulnerability on a single endpoint.

### Option 1: Using the NPX Framework for a Targeted URL
If you want to scan just a specific page with a parameter (e.g., `http://example.com/page.php?id=1`), simply run the `scan` command on that exact URL:

```bash
npx> scan http://example.com/page.php?id=1
```
The framework will:
1. Extract only that endpoint.
2. Fuzz for directories/backups relative to that URL.
3. Test the `id` parameter specifically against **SQLi, XSS, and LFI** payloads.

### Option 2: Manual `curl` Check (The Quickest Way)
For a "Single Vulnerability" check (like testing for an LFI or XSS), the fastest method is manual `curl`. Inside your terminal (or another tab), run these commands:

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

### Option 3: Fuzzing Specific Parameters
If you want to use NPX Framework's **Directory Bruteforce Module** only for a specific file, you can modify the internal wordlist. 
Inside the code, look for the `NPXFuzzerModule` class and its `get_wordlist` method. You can comment out the default lists and just return a custom list of one file:

```python
def get_wordlist(self, target_type="directory"):
    # Return ONLY the file you want to test
    return [".env"]
```
Save the file and run `scan http://example.com`. It will only fuzz for `.env`.

---

## 📊 Generating a Report

After running a scan (`scan http://target.com`), simply run the `report` command:

```bash
npx> report
```
The framework will save a file named `npx_scan_report.html` in your current directory. Open it in any web browser to view a professional, dark-themed security assessment report generated by NPX.

---

## ⚠️ Disclaimer

**This tool is intended for educational purposes, authorized security assessments, and penetration testing only.** 
The authors (NPX) and the community are **not responsible** for any illegal use, damage, or unauthorized access caused by this software. Always ensure you have explicit written permission from the target system owner before scanning.

---

## 🏆 Credits & Contributions

Built with ❤️ by **NPX**. 
For feedback, contributions, or bug reports, please open an issue on the GitHub repository or reach out via our official website: [https://npx-official.github.io/](https://npx-official.github.io/)
```


