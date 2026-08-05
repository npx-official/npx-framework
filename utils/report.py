# utils/report.py
import os
import json
from datetime import datetime
from core.colors import Colors

class NPXAdvancedReport:
    def __init__(self, framework):
        self.framework = framework
        self.reports_dir = "scan_results/reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def run(self, vulnerabilities, exploits):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.framework.config.target_url or "unknown"
        filename = f"report_{target.replace('/', '_')}_{timestamp}"
        
        html_path = os.path.join(self.reports_dir, f"{filename}.html")
        json_path = os.path.join(self.reports_dir, f"{filename}.json")
        
        report_data = {
            'target': target,
            'timestamp': timestamp,
            'vulnerabilities': vulnerabilities,
            'exploits': exploits
        }
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        html_content = f"""
        <html>
        <head>
            <title>NPX Scan Report - {target}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                h1 {{ color: #333; }}
                .vuln {{ background: #ffebee; padding: 10px; margin: 5px 0; border-left: 4px solid #f44336; }}
                .info {{ background: #e3f2fd; padding: 10px; margin: 5px 0; border-left: 4px solid #2196f3; }}
                .exploit {{ background: #fff3e0; padding: 10px; margin: 5px 0; border-left: 4px solid #ff9800; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>NPX Framework Scan Report</h1>
                <div class="info"><strong>Target:</strong> {target}</div>
                <div class="info"><strong>Timestamp:</strong> {timestamp}</div>
                <h2>Vulnerabilities Found: {len(vulnerabilities)}</h2>
        """
        for v in vulnerabilities:
            html_content += f'<div class="vuln"><strong>{v.get("type", "Unknown")}</strong> - {v.get("details", "")}</div>'
        
        if exploits:
            html_content += '<h2>Exploits Performed:</h2>'
            for e in exploits:
                html_content += f'<div class="exploit"><strong>{e.get("type", "Unknown")}</strong> - {e.get("details", "")}</div>'
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        print(f"{Colors.OKGREEN}[+] Report generated:{Colors.ENDC}")
        print(f"  HTML: {html_path}")
        print(f"  JSON: {json_path}")
