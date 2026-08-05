from core.colors import Colors
from utils.helpers import urljoin

class NPXWordpressScanner:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []

    def run(self, target_url):
        print(f"{Colors.OKCYAN}[*] Module: WordPress Scanner...{Colors.ENDC}")
        return self.findings
