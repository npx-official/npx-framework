# utils/storage.py
import os
import json
import sqlite3
from datetime import datetime
from core.colors import Colors

class NPXStorage:
    def __init__(self):
        self.base_dir = "scan_results"
        self.scans_dir = os.path.join(self.base_dir, "scans")
        self.reports_dir = os.path.join(self.base_dir, "reports")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.nuclei_dir = os.path.join(self.base_dir, "nuclei")
        self.ffuf_dir = os.path.join(self.base_dir, "ffuf")
        self.temp_dir = os.path.join(self.base_dir, "temp")
        
        for dir_path in [self.scans_dir, self.reports_dir, self.logs_dir, 
                        self.nuclei_dir, self.ffuf_dir, self.temp_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        self.db_path = os.path.join(self.base_dir, "npx_scan_history.db")
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                modules TEXT,
                vulnerabilities INTEGER,
                timestamp TEXT,
                details TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_scan(self, target, modules, vuln_count, vulnerabilities):
        timestamp = datetime.now().isoformat()
        details = json.dumps(vulnerabilities)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scans (target, modules, vulnerabilities, timestamp, details) VALUES (?, ?, ?, ?, ?)",
            (target, str(modules), vuln_count, timestamp, details)
        )
        conn.commit()
        scan_id = cursor.lastrowid
        conn.close()
        
        json_path = os.path.join(self.scans_dir, f"scan_{scan_id}_{target.replace('/', '_')}.json")
        with open(json_path, 'w') as f:
            json.dump({
                'id': scan_id,
                'target': target,
                'modules': modules,
                'vulnerabilities': vulnerabilities,
                'timestamp': timestamp
            }, f, indent=2)
        
        print(f"{Colors.DIM}[+] Scan saved to: {json_path}{Colors.ENDC}")
        return scan_id

    def get_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, target, modules, vulnerabilities, timestamp FROM scans ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print(f"{Colors.DIM}[-] No scan history found.{Colors.ENDC}")
            return
        
        print(f"{Colors.OKCYAN}Scan History:{Colors.ENDC}")
        for row in rows:
            id, target, modules, vuln_count, timestamp = row
            print(f"  [{id}] {target} - {vuln_count} vulns - {timestamp[:19]}")

    def save_nuclei_results(self, target, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nuclei_{target.replace('/', '_')}_{timestamp}.json"
        filepath = os.path.join(self.nuclei_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        return filepath

    def save_ffuf_results(self, target, results):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ffuf_{target.replace('/', '_')}_{timestamp}.json"
        filepath = os.path.join(self.ffuf_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        return filepath
