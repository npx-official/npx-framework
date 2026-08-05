from core.colors import Colors

class NPXXMLEngine:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: XXE Scanner...{Colors.ENDC}")
        return self.findings
