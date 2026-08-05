import time
import threading
from core.colors import Colors

class NPXScheduler:
    def __init__(self, framework):
        self.framework = framework
        self.jobs = []

    def add_job(self, target, interval):
        self.jobs.append({'target': target, 'interval': interval, 'active': True})
        print(f"{Colors.OKGREEN}[+] Scheduled scan added: {target} every {interval} seconds.{Colors.ENDC}")
        def run_scan():
            while True:
                time.sleep(interval)
                if not self.jobs[-1]['active']:
                    break
                print(f"{Colors.WARNING}[*] Running auto-scan on {target}...{Colors.ENDC}")
                self.framework.config.target_url = target
                # يمكن استدعاء فحص كامل هنا
        threading.Thread(target=run_scan, daemon=True).start()

    def list_jobs(self):
        if not self.jobs:
            print(f"{Colors.DIM}[-] No scheduled jobs.{Colors.ENDC}")
        for i, job in enumerate(self.jobs):
            print(f"  {i+1}. Target: {job['target']} | Interval: {job['interval']}s | Active: {job['active']}")

    def stop_job(self, index):
        if 0 <= index < len(self.jobs):
            self.jobs[index]['active'] = False
            print(f"{Colors.WARNING}[!] Stopped job #{index+1}{Colors.ENDC}")
