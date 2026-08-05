from core.colors import Colors
from utils.helpers import quote
import urllib.parse

class NPXLFIModule:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.vulnerabilities = []

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: LFI Scanner...{Colors.ENDC}")
        return self.vulnerabilities
