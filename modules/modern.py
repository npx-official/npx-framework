# modules/modern.py
from core.colors import Colors
from utils.helpers import urljoin

class NPXModernScanner:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.findings = []

    def scan_graphql(self, url):
        """فحص GraphQL Introspection"""
        test_url = urljoin(url, '/graphql')
        introspection_query = '{"query":"{__schema{types{name}}}"}'
        try:
            headers = {'Content-Type': 'application/json'}
            response = self.session.send_request("POST", test_url, data=introspection_query, headers=headers)
            if response and "__schema" in response.text:
                self.findings.append({
                    'type': 'GraphQL',
                    'url': test_url,
                    'details': 'GraphQL Introspection Enabled'
                })
                print(f"{Colors.WARNING}[!] GraphQL Introspection Enabled at {test_url}{Colors.ENDC}")
        except Exception as e:
            pass

    def scan_websocket(self, url):
        """فحص WebSocket الأساسي"""
        ws_urls = [
            urljoin(url, '/ws'),
            urljoin(url, '/socket.io'),
            urljoin(url, '/websocket')
        ]
        for ws_url in ws_urls:
            try:
                # محاولة اتصال بسيطة عبر HTTP Upgrade
                headers = {
                    'Upgrade': 'websocket',
                    'Connection': 'Upgrade',
                    'Sec-WebSocket-Key': 'x3JJHMbDL1EzLkh9GBhXDw==',
                    'Sec-WebSocket-Version': '13'
                }
                response = self.session.send_request("GET", ws_url, headers=headers)
                if response and response.status_code in [101, 200]:
                    self.findings.append({
                        'type': 'WebSocket',
                        'url': ws_url,
                        'details': f'WebSocket endpoint found (Status: {response.status_code})'
                    })
                    print(f"{Colors.WARNING}[!] WebSocket Found: {ws_url} (Status: {response.status_code}){Colors.ENDC}")
            except:
                pass

    def run(self, target_urls):
        print(f"{Colors.OKCYAN}[*] Module: Modern Web Scanner (GraphQL/WebSocket)...{Colors.ENDC}")
        for url in target_urls:
            if any(x in url for x in ['graphql', 'api', 'ws']):
                self.scan_graphql(url)
                self.scan_websocket(url)
        return self.findings
