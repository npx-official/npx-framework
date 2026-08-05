from core.colors import Colors

class NPXCredentialHarvester:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager

    def run(self, urls):
        print(f"{Colors.OKCYAN}[*] Module: Credential Harvester...{Colors.ENDC}")
        return []
