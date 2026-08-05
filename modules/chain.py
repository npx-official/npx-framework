# modules/chain.py
from core.colors import Colors

class NPXExploitChainBuilder:
    def __init__(self, framework):
        self.framework = framework
        self.session = framework.session_manager
        self.chains = []

    def build_chain(self, vulnerabilities):
        """بناء سلسلة استغلال من الثغرات الموجودة"""
        chain = []
        
        # ترتيب الاستغلال المنطقي
        if any(v.get('type') == 'LFI' for v in vulnerabilities):
            chain.append('Read sensitive files via LFI')
            
        if any(v.get('type') == 'SQLi' for v in vulnerabilities):
            chain.append('Extract database credentials via SQLi')
            
        if any(v.get('type') == 'XSS' for v in vulnerabilities):
            chain.append('Steal session cookies via XSS')
            
        if any(v.get('type') == 'SSRF' for v in vulnerabilities):
            chain.append('Access internal services via SSRF')
            
        if any(v.get('type') == 'XXE' for v in vulnerabilities):
            chain.append('Read files and perform SSRF via XXE')
        
        return chain

    def generate_recommendations(self, chain):
        """توليد توصيات بناءً على سلسلة الاستغلال"""
        recommendations = []
        
        if 'LFI' in str(chain):
            recommendations.append("• Restrict file inclusion to specific whitelisted paths")
        if 'SQLi' in str(chain):
            recommendations.append("• Use parameterized queries and input validation")
        if 'XSS' in str(chain):
            recommendations.append("• Implement proper output encoding and CSP headers")
        if 'SSRF' in str(chain):
            recommendations.append("• Block internal IP ranges and validate URL inputs")
        if 'XXE' in str(chain):
            recommendations.append("• Disable external entity processing in XML parsers")
            
        return recommendations

    def run(self, vulnerabilities):
        print(f"{Colors.OKCYAN}[*] Module: Exploit Chain Builder...{Colors.ENDC}")
        
        if not vulnerabilities:
            print(f"{Colors.DIM}[-] No vulnerabilities found to build chain.{Colors.ENDC}")
            return self.chains
            
        chain = self.build_chain(vulnerabilities)
        
        if chain:
            print(f"{Colors.OKGREEN}[+] Exploit chain built:{Colors.ENDC}")
            for i, step in enumerate(chain, 1):
                print(f"  {i}. {step}")
                
            recommendations = self.generate_recommendations(chain)
            if recommendations:
                print(f"\n{Colors.OKCYAN}[*] Recommendations:{Colors.ENDC}")
                for rec in recommendations:
                    print(f"  {rec}")
        else:
            print(f"{Colors.DIM}[-] No logical exploit chain possible.{Colors.ENDC}")
            
        self.chains.append({
            'vulnerabilities': vulnerabilities,
            'chain': chain
        })
        
        return self.chains
