# modules/nuclei.py
import subprocess
import json
import os
from datetime import datetime
from core.colors import Colors

class NPXNucleiIntegration:
    def __init__(self, framework):
        self.framework = framework

    def run(self, target_url):
        print(f"{Colors.OKCYAN}[*] Running Nuclei on {target_url}...{Colors.ENDC}")
        
        output_dir = "scan_results/nuclei"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"nuclei_{target_url.replace('/', '_')}_{timestamp}.json")
        
        try:
            cmd = [
                "nuclei", "-u", target_url,
                "-severity", "critical,high,medium",
                "-silent",
                "-json", "-o", output_file
            ]
            subprocess.run(cmd, check=True, timeout=300)
            
            findings = []
            with open(output_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        name = data.get("info", {}).get("name", "Unknown")
                        severity = data.get("info", {}).get("severity", "N/A")
                        print(f"{Colors.FAIL}[!] {name} (Severity: {severity}){Colors.ENDC}")
                        findings.append(data)
                    except:
                        pass
            
            print(f"{Colors.DIM}[+] Nuclei results saved to: {output_file}{Colors.ENDC}")
            return findings
        except FileNotFoundError:
            print(f"{Colors.WARNING}[!] Nuclei not installed. Skipping.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Nuclei error: {e}{Colors.ENDC}")
        return []
