from core.colors import Colors

class NPXAutoUpdater:
    def __init__(self, framework):
        self.framework = framework

    def run(self):
        print(f"{Colors.OKCYAN}[*] Checking for updates...{Colors.ENDC}")
