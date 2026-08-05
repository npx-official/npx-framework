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

    def get_wordlist(self, wordlist_type="common"):
        """
        إرجاع مسار قائمة كلمات حسب النوع من المجلد المركزي
        الأنواع: common, directories, passwords, fuzzing
        """
        central_dir = "/usr/share/wordlists/central"
        
        # تعريف القوائم حسب النوع
        wordlists_map = {
            "common": [
                f"{central_dir}/common.txt",
                f"{central_dir}/Discovery/Web-Content/common.txt",
                "/usr/share/dirb/wordlists/common.txt"
            ],
            "directories": [
                f"{central_dir}/Discovery/Web-Content/directory-list-2.3-medium.txt",
                f"{central_dir}/Discovery/Web-Content/directory-list-lowercase-2.3-medium.txt",
                f"{central_dir}/common.txt",
                "/usr/share/dirb/wordlists/common.txt"
            ],
            "passwords": [
                f"{central_dir}/rockyou.txt",
                f"{central_dir}/Passwords/Common-Credentials/10k-most-common.txt",
                f"{central_dir}/Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt",
                "/usr/share/wordlists/rockyou.txt"
            ],
            "fuzzing": [
                f"{central_dir}/Fuzzing/fuzz.txt",
                f"{central_dir}/Miscellaneous/fuzz.txt",
                "/usr/share/wfuzz/wordlist/fuzz.txt"
            ],
            "all": [
                f"{central_dir}/common.txt",
                f"{central_dir}/Discovery/Web-Content/common.txt",
                f"{central_dir}/Fuzzing/fuzz.txt",
                f"{central_dir}/rockyou.txt"
            ]
        }
        
        # الحصول على قائمة المسارات المطلوبة
        paths = wordlists_map.get(wordlist_type, wordlists_map["common"])
        
        # البحث عن أول مسار موجود
        for path in paths:
            if os.path.exists(path):
                return path
        
        # إذا لم يتم العثور على أي قائمة، إنشاء قائمة مؤقتة
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

    def run_ffuf(self, target, wordlist_type="common"):
        """تشغيل FFUF لاكتشاف الدلائل والملفات"""
        base = target.rstrip("/")
        print(f"{Colors.OKCYAN}[*] Running FFUF on {base}...{Colors.ENDC}")
        
        wordlist = self.get_wordlist(wordlist_type)
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

    def run_internal_fuzzer(self, target_urls, wordlist_type="common"):
        """الطريقة الداخلية لتكسير المسارات (بدون FFUF)"""
        print(f"{Colors.DIM}[*] Using internal directory bruteforce...{Colors.ENDC}")
        wordlist = self.get_wordlist(wordlist_type)
        
        # قراءة القائمة
        try:
            with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
                paths = [line.strip() for line in f if line.strip()]
        except:
            paths = [
                "admin", "login", "dashboard", "api", "v1", "v2", "backup", "wp-admin",
                "administrator", "panel", "cpanel", "webmail", "mail", "test", "dev",
                "uploads", "files", "downloads", "images", "assets", "css", "js", "img",
                ".env", ".git/config", "config.php", "wp-config.php", ".htaccess",
                "robots.txt", "sitemap.xml", "index.php", "index.html", "readme.md"
            ]
        
        for url in target_urls:
            for path in paths:
                if not path:
                    continue
                test_url = urljoin(url, path)
                try:
                    response = self.session.send_request("GET", test_url)
                    if response and response.status_code in [200, 301, 302, 401, 403]:
                        self.found_paths.append({"url": test_url, "status": response.status_code})
                        color = Colors.OKGREEN if response.status_code == 200 else Colors.WARNING
                        print(f"  {color}[{response.status_code}] {test_url}{Colors.ENDC}")
                except:
                    pass

    def run(self, target_urls, wordlist_type="common"):
        """تشغيل الفازر: يستخدم FFUF على الهدف الأول، ثم يمر على الباقي داخلياً"""
        if not target_urls:
            return []
        
        # استخدم الهدف الأول كقاعدة لتشغيل FFUF
        main_target = list(target_urls)[0] if target_urls else ""
        if main_target:
            success = self.run_ffuf(main_target, wordlist_type)
            if not success:
                self.run_internal_fuzzer([main_target], wordlist_type)
        return self.found_paths
