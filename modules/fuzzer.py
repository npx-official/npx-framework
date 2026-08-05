import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.colors import Colors
from utils.helpers import quote, urljoin

class NPXFuzzerModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.found_paths = []

    def get_wordlist(self, target_type="directory"):
        if target_type == "directory":
            return ["admin", "login", "dashboard", "api", "v1", "v2", "backup", "wp-admin",
                    "administrator", "panel", "cpanel", "webmail", "mail", "test", "dev",
                    "uploads", "files", "downloads", "images", "assets", "css", "js", "img"]
        elif target_type == "file":
            return [".env", ".git/config", "config.php", "wp-config.php", ".htaccess",
                    "robots.txt", "sitemap.xml", "index.php", "index.html", "readme.md",
                    "CHANGELOG.md", "LICENSE", "composer.json", "package.json"]
        return []

    def check_path(self, base_url, path):
        target = urljoin(base_url, path)
        try:
            response = self.session.send_request("GET", target)
            if response and response.status_code in [200, 301, 302, 403, 401]:
                return target, response.status_code
        except:
            pass
        return None

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: Directory & File Bruteforce...{Colors.ENDC}")
        dir_wordlist = self.get_wordlist("directory")
        print(f"{Colors.DIM}[*] Checking {len(dir_wordlist)} directories...{Colors.ENDC}")
        tasks = []
        for url in target_urls:
            for path in dir_wordlist:
                tasks.append((url, path))
        with ThreadPoolExecutor(max_workers=self.framework.config.threads) as executor:
            future_to_task = {executor.submit(self.check_path, url, path): (url, path) for url, path in tasks}
            for future in as_completed(future_to_task):
                result = future.result()
                if result:
                    target, status = result
                    color = Colors.OKGREEN if status == 200 else Colors.WARNING
                    print(f"  {color}[{status}] {target}{Colors.ENDC}")
                    self.found_paths.append({'url': target, 'status': status})
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
