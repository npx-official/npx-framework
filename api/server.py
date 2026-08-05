from core.colors import Colors

class NPXRESTAPI:
    def __init__(self, framework):
        self.framework = framework
        self.port = 8080

    def start(self):
        print(f"{Colors.WARNING}[!] REST API not fully implemented yet.{Colors.ENDC}")
