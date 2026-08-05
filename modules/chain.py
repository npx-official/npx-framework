from core.colors import Colors
from utils.helpers import quote

class NPXExploitChainBuilder:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.chains = []

    def run(self, vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Module: Exploit Chain Builder...{Colors.ENDC}")
        return self.chains
