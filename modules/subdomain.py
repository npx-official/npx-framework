# modules/subdomain.py
import subprocess
import json
import re
from core.colors import Colors

class NPXSubdomainTakeover:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager

    def run_amass(self, target):
        """تشغيل Amass لاكتشاف النطاقات الفرعية"""
        print(f"{Colors.OKCYAN}[*] Running Amass on {target}...{Colors.ENDC}")
        try:
            # تشغيل Amass في الوضع السلبي (سريع)
            cmd = ["amass", "enum", "-passive", "-d", target, "-json", "amass_output.json"]
            subprocess.run(cmd, check=True, timeout=120)
            
            # قراءة النتائج
            subdomains = set()
            with open("amass_output.json", "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "name" in data:
                            subdomains.add(data["name"])
                    except:
                        pass
            print(f"{Colors.OKGREEN}[+] Amass found {len(subdomains)} subdomains.{Colors.ENDC}")
            return subdomains
        except FileNotFoundError:
            print(f"{Colors.WARNING}[!] Amass not installed. Falling back to internal scanner.{Colors.ENDC}")
            return set()
        except Exception as e:
            print(f"{Colors.FAIL}[!] Amass error: {e}{Colors.ENDC}")
            return set()

    def run(self, target_domain):
        """تشغيل ماسح النطاقات الفرعية"""
        if not target_domain:
            print(f"{Colors.FAIL}[!] No domain provided for subdomain scan.{Colors.ENDC}")
            return []
        
        # محاولة استخدام Amass أولاً
        subdomains = self.run_amass(target_domain)
        
        # إذا لم يعمل Amass، استخدم الطريقة الداخلية (من Recon)
        if not subdomains:
            print(f"{Colors.DIM}[*] Using internal subdomain discovery...{Colors.ENDC}")
            # هنا يمكنك استدعاء الدوال الداخلية من Recon
            # مثلاً: self.framework.recon.discover_subdomains(...)
            # لكننا سنتركها فارغة حالياً.
        
        return list(subdomains)
