from core.colors import Colors

class NPXSmartHelper:
    def __init__(self, framework):
        self.framework = framework

    def run(self, vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Smart Helper Suggestions:{Colors.ENDC}")
        if not vulnerabilities:
            print("  - No critical findings. Consider running 'nuclei' for CVE scanning.")
        else:
            print("  - Run 'postexploit' to extract data.")
