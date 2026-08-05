from core.colors import Colors

class NPXHashcatIntegration:
    def __init__(self, framework):
        self.framework = framework

    def run(self, credentials):
        print(f"{Colors.OKCYAN}[*] Module: Hashcat Integration...{Colors.ENDC}")
        return credentials
