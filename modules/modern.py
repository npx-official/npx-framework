from core.colors import Colors

class NPXModernScanner:
    def __init__(self, framework):
        self.framework = framework
        self.findings = []

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: Modern Web Scanner...{Colors.ENDC}")
        return self.findings
