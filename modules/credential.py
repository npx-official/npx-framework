# modules/credential.py
import re
from core.colors import Colors

class NPXCredentialHarvester:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.credentials = []

    def extract_emails(self, content):
        """استخراج الإيميلات"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(pattern, content)

    def extract_passwords(self, content):
        """استخراج كلمات مرور محتملة"""
        patterns = [
            r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'pass["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'pwd["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'api_key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ]
        found = []
        for pattern in patterns:
            found.extend(re.findall(pattern, content, re.IGNORECASE))
        return found

    def extract_usernames(self, content):
        """استخراج أسماء مستخدمين محتملة"""
        pattern = r'user(name)?["\']?\s*[:=]\s*["\']([^"\']+)["\']'
        return re.findall(pattern, content, re.IGNORECASE)

    def run(self, urls):
        print(f"{Colors.OKCYAN}[*] Module: Credential Harvester...{Colors.ENDC}")
        
        for url in urls:
            try:
                response = self.session.send_request("GET", url)
                if not response:
                    continue
                    
                content = response.text
                
                # استخراج البيانات
                emails = self.extract_emails(content)
                passwords = self.extract_passwords(content)
                usernames = self.extract_usernames(content)
                
                if emails or passwords or usernames:
                    self.credentials.append({
                        'url': url,
                        'emails': emails,
                        'passwords': passwords,
                        'usernames': usernames
                    })
                    
                    if emails:
                        print(f"{Colors.WARNING}[!] Found {len(emails)} emails at {url}{Colors.ENDC}")
                    if passwords:
                        print(f"{Colors.FAIL}[!] Found {len(passwords)} potential passwords at {url}{Colors.ENDC}")
                        
            except Exception as e:
                pass
                
        return self.credentials
