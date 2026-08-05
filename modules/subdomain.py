from core.colors import Colors

class NPXSubdomainTakeover:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager

    def run(self, subdomains):
        print(f"{Colors.OKCYAN}[*] Module: Subdomain Takeover...{Colors.ENDC}")
        return []
