# modules/nuclei.py
import subprocess
import json
from core.colors import Colors

class NPXNucleiIntegration:
    def __init__(self, framework):
        self.framework = framework

    def run(self, target_url):
        print(f"{Colors.OKCYAN}[*] Running Nuclei on {target_url}...{Colors.ENDC}")
        try:
            cmd = [
                "nuclei", "-u", target_url,
                "-severity", "critical,high,medium",
                "-silent",
                "-json", "-o", "nuclei_results.json"
            ]
            subprocess.run(cmd, check=True, timeout=300)
            
            findings = []
            with open("nuclei_results.json", "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        name = data.get("info", {}).get("name", "Unknown")
                        severity = data.get("info", {}).get("severity", "N/A")
                        print(f"{Colors.FAIL}[!] {name} (Severity: {severity}){Colors.ENDC}")
                        findings.append(data)
                    except:
                        pass
            return findings
        except FileNotFoundError:
            print(f"{Colors.WARNING}[!] Nuclei not installed. Skipping.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Nuclei error: {e}{Colors.ENDC}")
        return []
