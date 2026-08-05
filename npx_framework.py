#!/usr/bin/env python3
import sys
from core.config import NPXConfig
from core.session import NPXSessionManager
from core.recon import NPXReconEngine
from core.scheduler import NPXScheduler
from utils.storage import NPXStorage
from cli import NPXCLIUltimate
from core.colors import Colors

class NPXFrameworkUltimate:
    def __init__(self):
        self.config = NPXConfig()
        self.session_manager = NPXSessionManager(self.config)
        self.recon = NPXReconEngine(self.session_manager)
        self.scheduler = NPXScheduler(self)
        self.storage = NPXStorage()
        self.cli = NPXCLIUltimate(self)
        self.is_running = False
        self.vulnerabilities = []
        self.exploits = []

    def run_cli(self):
        self.is_running = True
        self.cli.run()

def main():
    print(f"{Colors.DIM}[*] Initializing NPX Framework...{Colors.ENDC}")
    framework = NPXFrameworkUltimate()
    if len(sys.argv) > 1:
        framework.config.target_url = sys.argv[1]
        print(f"{Colors.OKGREEN}[+] Target set to: {framework.config.target_url}{Colors.ENDC}")
    framework.run_cli()

if __name__ == "__main__":
    main()
