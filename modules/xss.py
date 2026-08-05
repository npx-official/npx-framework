import urllib.parse
from core.colors import Colors
from utils.helpers import quote

class NPXXSSModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []

    def test_reflected_xss(self, url, param, value):
        payloads = ["<script>alert('NPX')</script>", "<img src=x onerror=alert(1)>",
                    "\"><script>alert(1)</script>", "';alert(1)//", "<svg onload=alert(1)>"]
        for payload in payloads:
            injected = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            resp = self.session.send_request("GET", injected)
            if resp and payload in resp.text:
                return injected, f"Reflected XSS: '{payload[:30]}...'"
        return None, None

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: XSS Detector...{Colors.ENDC}")
        testable = [u for u in target_urls if '?' in u and '=' in u]
        for url in testable:
            parsed = urllib.parse.urlparse(url)
            for part in parsed.query.split('&'):
                if '=' in part:
                    param, value = part.split('=', 1)
                    if not value:
                        continue
                    result = self.test_reflected_xss(url, param, value)
                    if result:
                        vuln_url, details = result
                        self.vulnerabilities.append({'type': 'XSS', 'url': vuln_url, 'details': details, 'param': param})
                        print(f"  {Colors.FAIL}[!] {details} at {vuln_url}{Colors.ENDC}")
        return self.vulnerabilities
