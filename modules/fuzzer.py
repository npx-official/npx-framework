# modules/fuzzer.py
import subprocess
import os
import json
from core.colors import Colors
from utils.helpers import urljoin

class NPXFuzzerModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.found_paths = []

    def get_wordlist(self):
        """تحديد قائمة كلمات متاحة"""
        possible_paths = [
            "/usr/share/wordlists/dirb/common.txt",
            "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
            "/usr/share/wordlists/dirb/big.txt",
            "/usr/share/seclists/Discovery/Web-Content/common.txt"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        # إذا لم توجد، أنشئ قائمة صغيرة مؤقتة
        temp_list = "/tmp/npx_wordlist.txt"
        if not os.path.exists(temp_list):
            with open(temp_list, "w") as f:
                f.write("\n".join([
                    "admin", "login", "dashboard", "api", "v1", "v2", "backup", "wp-admin",
                    "administrator", "panel", "cpanel", "webmail", "mail", "test", "dev",
                    "uploads", "files", "downloads", "images", "assets", "css", "js", "img",
                    ".env", ".git/config", "config.php", "wp-config.php", ".htaccess",
                    "robots.txt", "sitemap.xml", "index.php", "index.html", "readme.md",
                    "CHANGELOG.md", "LICENSE", "composer.json", "package.json"
                ]))
        return temp_list

    def run_ffuf(self, target):
        """تشغيل FFUF لاكتشاف الدلائل والملفات"""
        # استخدم الـ target الأساسي فقط
        base = target.rstrip("/")
        print(f"{Colors.OKCYAN}[*] Running FFUF on {base}...{Colors.ENDC}")
        
        wordlist = self.get_wordlist()
        output_file = "ffuf_output.json"
        
        try:
            cmd = [
                "ffuf", "-u", f"{base}/FUZZ",
                "-w", wordlist,
                "-fc", "404,403",
                "-o", output_file,
                "-of", "json",
                "-s"
            ]
            subprocess.run(cmd, check=True, timeout=60)
            
            # تحليل النتائج
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    data = json.load(f)
                    for result in data.get("results", []):
                        status = result.get("status", 0)
                        if status in [200, 301, 302, 401, 403]:
                            path = result.get("url", "")
                            self.found_paths.append({"url": path, "status": status})
                            color = Colors.OKGREEN if status == 200 else Colors.WARNING
                            print(f"  {color}[{status}] {path}{Colors.ENDC}")
                os.remove(output_file)
            return True
            
        except FileNotFoundError:
            print(f"{Colors.WARNING}[!] FFUF not installed. Falling back to internal fuzzer.{Colors.ENDC}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}[!] FFUF error: {e}{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}[!] FFUF error: {e}{Colors.ENDC}")
            return False

    def run_internal_fuzzer(self, target_urls):
        """الطريقة الداخلية لتكسير المسارات (بدون FFUF)"""
        print(f"{Colors.DIM}[*] Using internal directory bruteforce...{Colors.ENDC}")
        # هنا نستخدم القائمة الداخلية ونرسل طلبات مباشرة
        wordlist = self.get_wordlist()
        with open(wordlist, "r") as f:
            paths = [line.strip() for line in f if line.strip()]
        for url in target_urls:
            for path in paths:
                test_url = urljoin(url, path)
                try:
                    response = self.session.send_request("GET", test_url)
                    if response and response.status_code in [200, 301, 302, 401, 403]:
                        self.found_paths.append({"url": test_url, "status": response.status_code})
                        color = Colors.OKGREEN if response.status_code == 200 else Colors.WARNING
                        print(f"  {color}[{response.status_code}] {test_url}{Colors.ENDC}")
                except:
                    pass

    def run(self, target_urls):
        """تشغيل الفازر: يستخدم FFUF على الهدف الأول، ثم يمر على الباقي داخلياً"""
        if not target_urls:
            return []
        
        # استخدم الهدف الأول كقاعدة لتشغيل FFUF
        main_target = list(target_urls)[0] if target_urls else ""
        if main_target:
            success = self.run_ffuf(main_target)
            if not success:
                self.run_internal_fuzzer([main_target])
        return self.found_paths
