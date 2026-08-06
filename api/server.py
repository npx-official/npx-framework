# api/server.py
from flask import Flask, request, jsonify
import threading
import json
from core.colors import Colors

class NPXRESTAPI:
    def __init__(self, framework):
        self.framework = framework
        self.port = 8080
        self.app = Flask(__name__)
        self.scan_results = {}
        
        # تعريف نقاط النهاية
        @self.app.route('/api/v1/scan', methods=['POST'])
        def scan_endpoint():
            data = request.get_json()
            if not data or 'target' not in data:
                return jsonify({'error': 'Missing target URL'}), 400
                
            target = data['target']
            scan_id = threading.get_ident()
            
            # تشغيل الفحص في خيط منفصل
            thread = threading.Thread(target=self._run_scan, args=(target, scan_id))
            thread.start()
            
            return jsonify({
                'status': 'accepted',
                'scan_id': scan_id,
                'target': target,
                'message': 'Scan started. Check status at /api/v1/scan/status/<scan_id>'
            }), 202
            
        @self.app.route('/api/v1/scan/status/<int:scan_id>', methods=['GET'])
        def status_endpoint(scan_id):
            if scan_id not in self.scan_results:
                return jsonify({'error': 'Scan ID not found'}), 404
                
            result = self.scan_results[scan_id]
            return jsonify(result), 200

    def _run_scan(self, target, scan_id):
        """تشغيل الفحص في الخلفية"""
        print(f"{Colors.OKCYAN}[*] API: Starting scan on {target}{Colors.ENDC}")
        
        try:
            # تحديث الهدف
            self.framework.config.target_url = target
            self.framework.recon.crawl_sitemap()
            
            internal_urls = self.framework.recon.discovered_urls['internal']
            if not internal_urls:
                internal_urls.add(target)
                
            # تشغيل الوحدات الأساسية
            from modules.fuzzer import NPXFuzzerModule
            from modules.sqli import NPXSQLiModule
            from modules.xss import NPXXSSModule
            from modules.lfi import NPXLFIModule
            
            fuzzer = NPXFuzzerModule(self.framework)
            fuzzer.run(internal_urls)
            
            sqli = NPXSQLiModule(self.framework)
            sqli.run(internal_urls)
            
            xss = NPXXSSModule(self.framework)
            xss.run(internal_urls)
            
            lfi = NPXLFIModule(self.framework)
            lfi.run(internal_urls)
            
            vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
            
            self.scan_results[scan_id] = {
                'status': 'completed',
                'target': target,
                'vulnerabilities_found': len(vulnerabilities),
                'vulnerabilities': vulnerabilities
            }
            
            print(f"{Colors.OKGREEN}[+] API: Scan completed. Found {len(vulnerabilities)} vulnerabilities.{Colors.ENDC}")
            
        except Exception as e:
            self.scan_results[scan_id] = {
                'status': 'failed',
                'error': str(e)
            }
            print(f"{Colors.FAIL}[!] API: Scan failed: {e}{Colors.ENDC}")

    def start(self):
        try:
            print(f"{Colors.OKCYAN}[*] Starting REST API on port {self.port}...{Colors.ENDC}")
            print(f"{Colors.OKGREEN}[+] API endpoint: http://localhost:{self.port}/api/v1/scan{Colors.ENDC}")
            self.app.run(host='0.0.0.0', port=self.port, threaded=True)
        except Exception as e:
            print(f"{Colors.FAIL}[!] Failed to start API: {e}{Colors.ENDC}")
