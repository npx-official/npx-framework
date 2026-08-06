# modules/hashcat.py
import subprocess
import os
import json
from core.colors import Colors

class NPXHashcatIntegration:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager

    def run(self, credentials):
        print(f"{Colors.OKCYAN}[*] Module: Hashcat Integration...{Colors.ENDC}")
        
        if not credentials:
            print(f"{Colors.DIM}[-] No credentials provided to hashcat.{Colors.ENDC}")
            return []
            
        results = []
        hash_file = "/tmp/npx_hashes.txt"
        
        try:
            # استخراج أي قيم تبدو كـ hashes من الاعتمادات
            hashes = []
            for cred in credentials:
                if isinstance(cred, dict):
                    for key, value in cred.items():
                        if isinstance(value, str) and len(value) > 10:
                            # محاولة التعرف على تنسيقات الهاش الشائعة
                            if value.startswith("$2y$") or value.startswith("$2a$"):
                                hashes.append(f"bcrypt:{value}")
                            elif value.startswith("$1$"):
                                hashes.append(f"md5crypt:{value}")
                            elif len(value) == 32 and all(c in '0123456789abcdef' for c in value):
                                hashes.append(f"md5:{value}")
                            elif len(value) == 40 and all(c in '0123456789abcdef' for c in value):
                                hashes.append(f"sha1:{value}")
                            elif len(value) == 64 and all(c in '0123456789abcdef' for c in value):
                                hashes.append(f"sha256:{value}")
                            elif "password" in key.lower() and "hash" in key.lower():
                                hashes.append(f"unknown:{value}")
            
            if not hashes:
                print(f"{Colors.DIM}[-] No recognizable hashes found in credentials.{Colors.ENDC}")
                return credentials
                
            print(f"{Colors.OKGREEN}[+] Found {len(hashes)} potential hashes.{Colors.ENDC}")
            
            # حفظ الهاشات في ملف
            with open(hash_file, "w") as f:
                for h in hashes:
                    f.write(h + "\n")
            
            # محاولة استخدام hashcat
            try:
                # استخدام wordlist صغير للاختبار
                wordlist = "/usr/share/wordlists/rockyou.txt"
                if os.path.exists(wordlist):
                    print(f"{Colors.OKCYAN}[*] Running hashcat with {wordlist}...{Colors.ENDC}")
                    cmd = ["hashcat", "-m", "0", hash_file, wordlist, "--force", "--quiet"]
                    subprocess.run(cmd, check=True, timeout=60)
                    
                    # عرض النتائج
                    result_cmd = ["hashcat", "--show", hash_file]
                    result = subprocess.run(result_cmd, capture_output=True, text=True, timeout=10)
                    if result.stdout:
                        print(f"{Colors.OKGREEN}[+] Hashcat cracked: {result.stdout.strip()}{Colors.ENDC}")
                        results.append({"hashcat": "success", "results": result.stdout.strip()})
                    else:
                        print(f"{Colors.DIM}[-] No hashes cracked.{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}[!] Wordlist not found at {wordlist}. Skipping hashcat.{Colors.ENDC}")
            except FileNotFoundError:
                print(f"{Colors.WARNING}[!] Hashcat not installed. Skipping.{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}[!] Hashcat error: {e}{Colors.ENDC}")
                
            # تنظيف
            if os.path.exists(hash_file):
                os.remove(hash_file)
                
        except Exception as e:
            print(f"{Colors.FAIL}[!] Hashcat integration error: {e}{Colors.ENDC}")
            
        return credentials
