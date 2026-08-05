# modules/waf_bypass.py
import urllib.parse
from core.colors import Colors

class NPXWAFBypassEngine:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.bypasses = []

    def generate_payloads(self, original_payload):
        """توليد أشكال مختلفة من البايلود لتجاوز WAF"""
        bypasses = [
            original_payload,
            original_payload.replace(' ', '+'),
            original_payload.replace(' ', '/**/'),
            original_payload.replace(' ', '%20'),
            original_payload.replace('=', ' LIKE '),
            original_payload.replace("'", "`"),
            original_payload.replace("'", "%27"),
            original_payload.replace('<', '%3C'),
            original_payload.replace('>', '%3E'),
            original_payload.upper(),
            original_payload.lower(),
            original_payload.capitalize(),
            urllib.parse.quote(original_payload),
            urllib.parse.quote_plus(original_payload),
            f"/*!{original_payload}*/",
            f"{original_payload}--",
            f"{original_payload}#",
            f"{original_payload}/*",
        ]
        return list(set(bypasses))

    def detect_waf(self, url):
        """محاولة اكتشاف نوع WAF"""
        waf_signatures = {
            'Cloudflare': ['cf-ray', 'cloudflare', '__cfuid'],
            'ModSecurity': ['modsecurity', 'mod_security', 'X-Mod-Security'],
            'Sucuri': ['sucuri', 'sucuri-id'],
            'Akamai': ['akamai', 'x-akamai'],
            'AWS WAF': ['aws-waf', 'x-amz', 'awsalb'],
            'Fortinet': ['fortigate', 'fortiweb'],
            'Imperva': ['imperva', 'incapsula'],
            'F5 BIG-IP': ['f5-bigip', 'bigip'],
            'WordFence': ['wordfence', 'wf_'],
            'Barracuda': ['barracuda', 'barra'],
            'WebKnight': ['webknight'],
            'Nginx': ['nginx', 'nginx-waf'],
        }
        
        detected = []
        try:
            response = self.session.send_request("GET", url)
            if response:
                headers = str(response.headers).lower()
                content = response.text.lower()
                
                for waf_name, signatures in waf_signatures.items():
                    for sig in signatures:
                        if sig.lower() in headers or sig.lower() in content:
                            detected.append(waf_name)
                            break
        except Exception as e:
            pass
            
        return list(set(detected))

    def run(self, target_urls, vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Module: WAF Bypass Engine...{Colors.ENDC}")
        
        if not target_urls:
            print(f"{Colors.DIM}[-] No URLs provided for WAF detection.{Colors.ENDC}")
            return self.bypasses
            
        for url in list(target_urls)[:3]:  # اختبر أول 3 روابط
            waf = self.detect_waf(url)
            if waf:
                print(f"{Colors.WARNING}[!] WAF detected at {url}: {', '.join(waf)}{Colors.ENDC}")
                self.bypasses.append({
                    'url': url,
                    'waf': waf,
                    'status': 'WAF Detected'
                })
            else:
                print(f"{Colors.OKGREEN}[+] No WAF detected at {url}{Colors.ENDC}")
                self.bypasses.append({
                    'url': url,
                    'waf': [],
                    'status': 'No WAF'
                })
                
        return self.bypasses
