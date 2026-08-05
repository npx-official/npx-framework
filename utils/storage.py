import sqlite3
import json
import datetime
from core.colors import Colors

class NPXStorage:
    def __init__(self, db_path="npx_scan_history.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                scan_date TEXT NOT NULL,
                modules TEXT,
                vulns INTEGER,
                results TEXT
            )
        ''')
        self.conn.commit()

    def save_scan(self, target, modules, vulns_count, results):
        scan_date = datetime.datetime.now().isoformat()
        self.cursor.execute('''
            INSERT INTO scans (target, scan_date, modules, vulns, results)
            VALUES (?, ?, ?, ?, ?)
        ''', (target, scan_date, ','.join(modules), vulns_count, json.dumps(results, default=str)))
        self.conn.commit()
        print(f"{Colors.OKGREEN}[+] Scan saved to database.{Colors.ENDC}")

    def get_history(self):
        self.cursor.execute('SELECT id, target, scan_date, vulns FROM scans ORDER BY scan_date DESC')
        rows = self.cursor.fetchall()
        if not rows:
            print(f"{Colors.DIM}[-] No history found.{Colors.ENDC}")
        for row in rows:
            print(f"  [{row[0]}] {row[1]} | {row[2]} | Vulns: {row[3]}")
