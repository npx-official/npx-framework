# modules/subdomain.py
import subprocess
import json
import re
import socket
from core.colors import Colors

class NPXSubdomainTakeover:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.subdomains = set()

    def run_dig(self, target):
        """محاولة استخراج النطاقات الفرعية عبر DIG"""
        try:
            result = subprocess.run(["dig", target, "ANY"], capture_output=True, text=True, timeout=10)
            if result.stdout:
                ips = re.findall(r'[\d.]+', result.stdout)
                for ip in ips:
                    if ip.count('.') == 3 and ip != '127.0.0.1':
                        try:
                            name = socket.gethostbyaddr(ip)[0]
                            if target in name:
                                self.subdomains.add(name.split('.')[0] + '.' + target)
                        except:
                            pass
        except:
            pass

    def run_amass(self, target):
        """تشغيل Amass لاكتشاف النطاقات الفرعية"""
        print(f"{Colors.OKCYAN}[*] Running Amass on {target}...{Colors.ENDC}")
        try:
            cmd = ["amass", "enum", "-passive", "-d", target, "-json", "amass_output.json"]
            subprocess.run(cmd, check=True, timeout=120)
            with open("amass_output.json", "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "name" in data:
                            self.subdomains.add(data["name"])
                    except:
                        pass
            print(f"{Colors.OKGREEN}[+] Amass found {len(self.subdomains)} subdomains.{Colors.ENDC}")
            return self.subdomains
        except FileNotFoundError:
            print(f"{Colors.WARNING}[!] Amass not installed. Falling back to internal scanner.{Colors.ENDC}")
            return set()
        except Exception as e:
            print(f"{Colors.FAIL}[!] Amass error: {e}{Colors.ENDC}")
            return set()

    def run(self, target_domain):
        if not target_domain:
            print(f"{Colors.FAIL}[!] No domain provided for subdomain scan.{Colors.ENDC}")
            return []
        subdomains = self.run_amass(target_domain)
        if not subdomains:
            self.run_dig(target_domain)
        return list(self.subdomains)
