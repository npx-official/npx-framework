# modules/wordpress.py
import re
from core.colors import Colors
from utils.helpers import urljoin

class NPXWordpressScanner:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []

    def detect_wordpress(self, url):
        """الكشف عن وجود ووردبريس"""
        indicators = [
            '/wp-content/',
            '/wp-includes/',
            '/wp-admin/',
            '/xmlrpc.php',
            '/wp-json/'
        ]
        
        for indicator in indicators:
            test_url = urljoin(url, indicator)
            response = self.session.send_request("GET", test_url)
            if response and response.status_code == 200:
                return True
        return False

    def get_version(self, url):
        """محاولة استخراج إصدار ووردبريس"""
        # محاولة من ملفات CSS
        css_url = urljoin(url, '/wp-content/themes/twenty*/style.css')
        try:
            response = self.session.send_request("GET", css_url)
            if response:
                version = re.search(r'Version:\s*([0-9.]+)', response.text)
                if version:
                    return version.group(1)
        except:
            pass
            
        # محاولة من readme
        readme_url = urljoin(url, '/readme.html')
        try:
            response = self.session.send_request("GET", readme_url)
            if response:
                version = re.search(r'Version\s*([0-9.]+)', response.text)
                if version:
                    return version.group(1)
        except:
            pass
            
        return 'Unknown'

    def scan_plugins(self, url):
        """مسح الإضافات المثبتة"""
        common_plugins = [
            'woocommerce', 'elementor', 'yoast-seo', 'contact-form-7',
            'jetpack', 'wpforms', 'all-in-one-seo-pack', 'wordfence',
            'wp-rocket', 'updraftplus', 'duplicator', 'ele-custom-skin',
            'wp-super-cache', 'wp-mail-smtp', 'redirection', 'polylang',
            'woo-commerce', 'bbpress', 'ultimate-member', 'learndash'
        ]
        
        installed = []
        for plugin in common_plugins:
            test_url = urljoin(url, f'/wp-content/plugins/{plugin}/readme.txt')
            response = self.session.send_request("GET", test_url)
            if response and response.status_code == 200:
                installed.append(plugin)
                print(f"{Colors.WARNING}[!] Plugin found: {plugin}{Colors.ENDC}")
                
        return installed

    def scan_themes(self, url):
        """مسح القوالب المثبتة"""
        common_themes = [
            'twentynineteen', 'twentytwenty', 'twentytwentyone',
            'twentytwentytwo', 'twentytwentythree', 'hello-elementor',
            'generatepress', 'astra', 'oceanwp', 'newspaper'
        ]
        
        installed = []
        for theme in common_themes:
            test_url = urljoin(url, f'/wp-content/themes/{theme}/style.css')
            response = self.session.send_request("GET", test_url)
            if response and response.status_code == 200:
                installed.append(theme)
                print(f"{Colors.WARNING}[!] Theme found: {theme}{Colors.ENDC}")
                
        return installed

    def run(self, target_url):
        print(f"{Colors.OKCYAN}[*] Module: WordPress Scanner...{Colors.ENDC}")
        
        if not self.detect_wordpress(target_url):
            print(f"{Colors.DIM}[-] WordPress not detected.{Colors.ENDC}")
            return self.findings
            
        print(f"{Colors.OKGREEN}[+] WordPress detected!{Colors.ENDC}")
        
        # استخراج المعلومات
        version = self.get_version(target_url)
        print(f"{Colors.OKCYAN}[*] Version: {version}{Colors.ENDC}")
        
        plugins = self.scan_plugins(target_url)
        themes = self.scan_themes(target_url)
        
        self.findings = {
            'version': version,
            'plugins': plugins,
            'themes': themes
        }
        
        return self.findings
