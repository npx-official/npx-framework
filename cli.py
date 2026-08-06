#!/usr/bin/env python3
# cli.py - NPX Framework Command Line Interface
# Version: 1.0 Ultimate (Fully Corrected)

import os
import sys
import urllib.parse
import json
import time

# إخفاء تحذيرات SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import warnings
warnings.filterwarnings('ignore')

# محاولة استيراد readline لدعم التنقل بالأسهم وتحرير النص
try:
    import readline
    readline.set_history_length(1000)
except ImportError:
    pass

from core.colors import Colors
from core.config import NPXConfig
from core.session import NPXSessionManager
from core.recon import NPXReconEngine
from core.scheduler import NPXScheduler
from utils.storage import NPXStorage
from modules.fuzzer import NPXFuzzerModule
from modules.sqli import NPXSQLiModule
from modules.xss import NPXXSSModule
from modules.lfi import NPXLFIModule
from modules.exploit import NPXExploitEngine
from modules.wordpress import NPXWordpressScanner
from modules.subdomain import NPXSubdomainTakeover
from modules.credential import NPXCredentialHarvester
from modules.hashcat import NPXHashcatIntegration
from modules.ssrf import NPXSSRFScanner
from modules.xxe import NPXXMLEngine
from modules.modern import NPXModernScanner
from modules.waf_bypass import NPXWAFBypassEngine
from modules.chain import NPXExploitChainBuilder
from modules.postexploit import NPXPostExploit
from modules.xss_exploit import NPXXSSExploit
from utils.report import NPXAdvancedReport
from utils.updater import NPXAutoUpdater
from utils.smart_helper import NPXSmartHelper
from api.server import NPXRESTAPI

class NPXCLIUltimate:
    def __init__(self, framework):
        self.framework = framework
        self.commands = {
            'scan': self.cmd_scan,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'clear': self.cmd_clear,
            'info': self.cmd_info,
            'modules': self.cmd_modules,
            'report': self.cmd_report,
            'nuclei': self.cmd_nuclei,
            'bypass': self.cmd_bypass,
            'api': self.cmd_api,
            'chain': self.cmd_chain,
            'postexploit': self.cmd_postexploit,
            'ssrf': self.cmd_ssrf,
            'xxe': self.cmd_xxe,
            'lfi': self.cmd_lfi,
            'schedule': self.cmd_schedule,
            'history': self.cmd_history,
            'xss_exploit': self.cmd_xss_exploit,
            'update': self.cmd_update,
            'suggest': self.cmd_suggest,
            'cloud': self.cmd_cloud,
            'graphql': self.cmd_graphql,
            'dns': self.cmd_dns,
            'jwt': self.cmd_jwt,
            'hashcat': self.cmd_hashcat,  # تمت إضافته
        }
        
        self.history_file = os.path.expanduser("~/.npx_history")
        try:
            readline.read_history_file(self.history_file)
        except (FileNotFoundError, AttributeError):
            pass
            
        self.banner()

    def banner(self):
        banner = f"""
{Colors.HEADER}
  ███╗   ██╗██████╗ ██╗  ██╗    ███████╗██████╗  █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
  ████╗  ██║██╔══██╗╚██╗██╔╝    ██╔════╝██╔══██╗██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
  ██╔██╗ ██║██████╔╝ ╚███╔╝     █████╗  ██████╔╝███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
  ██║╚██╗██║██╔═══╝  ██╔██╗     ██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
  ██║ ╚████║██║     ██╔╝ ██╗    ██║     ██║  ██║██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
  ╚═╝  ╚═══╝╚═╝     ╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
{Colors.ENDC}
{Colors.OKCYAN}  🔗 https://npx-official.github.io/         {Colors.WARNING}🛡️  NPX Framework v1.0 - Ultimate Edition{Colors.ENDC}
{Colors.DIM}  Type 'help' for available commands. (Use arrow keys to navigate history){Colors.ENDC}
"""
        print(banner)

    def run(self):
        while True:
            try:
                cmd = input(f"{Colors.OKGREEN}npx> {Colors.ENDC}").strip()
                
                if not cmd:
                    continue
                
                try:
                    readline.write_history_file(self.history_file)
                except (AttributeError, TypeError):
                    pass
                    
                parts = cmd.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"{Colors.FAIL}[!] Unknown command: {command}{Colors.ENDC}")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}[!] Interrupted. Exiting...{Colors.ENDC}")
                break
            except EOFError:
                print(f"\n{Colors.DIM}Goodbye!{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_scan(self, args):
        """تنفيذ فحص كامل للهدف"""
        if not args:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url> [--fast]{Colors.ENDC}")
            return
        
        fast_mode = '--fast' in args
        if fast_mode:
            args.remove('--fast')
        
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")
        
        if fast_mode:
            print(f"{Colors.WARNING}[!] Fast mode enabled (scanning only high-priority modules){Colors.ENDC}")
        
        print(f"{Colors.OKCYAN}[*] Crawling: {target}{Colors.ENDC}")
        self.framework.recon.crawl_sitemap()
        internal_urls = self.framework.recon.discovered_urls['internal']
        if not internal_urls:
            internal_urls.add(target)
        
        if fast_mode:
            # وضع سريع: فقط الوحدات الأساسية
            fuzzer = NPXFuzzerModule(self.framework)
            fuzzer.run(internal_urls, wordlist_type="common")
            
            sqli = NPXSQLiModule(self.framework)
            sqli.run(internal_urls)
            
            xss = NPXXSSModule(self.framework)
            xss.run(internal_urls)
            
            lfi = NPXLFIModule(self.framework)
            lfi.run(internal_urls)
            
            self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
            self.framework.exploits = []
            
            modules_used = ['Fuzzer', 'SQLi', 'XSS', 'LFI']
            
        else:
            # وضع كامل: تشغيل جميع الوحدات
            fuzzer = NPXFuzzerModule(self.framework)
            fuzzer.run(internal_urls)
            
            sqli = NPXSQLiModule(self.framework)
            sqli.run(internal_urls)
            
            xss = NPXXSSModule(self.framework)
            xss.run(internal_urls)
            
            lfi = NPXLFIModule(self.framework)
            lfi.run(internal_urls)
            
            exploit = NPXExploitEngine(self.framework)
            exploit.run(sqli.vulnerabilities + lfi.vulnerabilities)
            
            wp = NPXWordpressScanner(self.framework)
            wp.run(target)
            
            sub = NPXSubdomainTakeover(self.framework)
            domain = urllib.parse.urlparse(target).netloc
            sub.run(domain)
            
            cred = NPXCredentialHarvester(self.framework)
            cred.run(internal_urls)
            
            self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
            self.framework.exploits = exploit.exploited
            
            modules_used = ['Fuzzer', 'SQLi', 'XSS', 'LFI', 'Exploit', 'Wordpress', 'Subdomain', 'Credentials']
        
        self.framework.storage.save_scan(
            target, 
            modules_used, 
            len(self.framework.vulnerabilities), 
            self.framework.vulnerabilities
        )
        
        helper = NPXSmartHelper(self.framework)
        helper.run(self.framework.vulnerabilities)
        
        print(f"{Colors.OKGREEN}[+] Scan completed! Found {len(self.framework.vulnerabilities)} vulnerabilities.{Colors.ENDC}")
        if fast_mode:
            print(f"{Colors.WARNING}[!] Fast mode: Some modules were skipped. Use 'scan <url>' for full scan.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}[+] Use 'report' to generate HTML/PDF report.{Colors.ENDC}")

    def cmd_lfi(self, args):
        """تشغيل فحص LFI"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        lfi = NPXLFIModule(self.framework)
        lfi.run(self.framework.recon.discovered_urls['internal'])

    def cmd_help(self, args):
        """عرض المساعدة"""
        help_text = f"""
{Colors.OKCYAN}Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help
  {Colors.WARNING}scan <url>{Colors.ENDC}    Full scan
  {Colors.WARNING}scan <url> --fast{Colors.ENDC} Fast scan (fuzzer, SQLi, XSS, LFI only)
  {Colors.WARNING}modules{Colors.ENDC}       List modules
  {Colors.WARNING}report{Colors.ENDC}        Generate report (HTML+JSON)
  {Colors.WARNING}nuclei <url>{Colors.ENDC}  Run Nuclei
  {Colors.WARNING}bypass{Colors.ENDC}        WAF bypass
  {Colors.WARNING}chain{Colors.ENDC}         Build exploit chain
  {Colors.WARNING}api{Colors.ENDC}           Start REST API
  {Colors.WARNING}postexploit{Colors.ENDC}   Post-exploit (extract data)
  {Colors.WARNING}ssrf{Colors.ENDC}          SSRF scan
  {Colors.WARNING}xxe{Colors.ENDC}           XXE scan
  {Colors.WARNING}lfi{Colors.ENDC}           LFI scan
  {Colors.WARNING}schedule{Colors.ENDC}      Manage scheduled scans
  {Colors.WARNING}history{Colors.ENDC}       View scan history
  {Colors.WARNING}xss_exploit{Colors.ENDC}   Inject XSS payloads
  {Colors.WARNING}update{Colors.ENDC}        Check updates
  {Colors.WARNING}suggest{Colors.ENDC}       Smart suggestions
  {Colors.WARNING}info{Colors.ENDC}          Show config
  {Colors.WARNING}clear{Colors.ENDC}         Clear screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit
  {Colors.OKGREEN}NEW:{Colors.ENDC}
  {Colors.WARNING}cloud <domain>{Colors.ENDC}    Scan cloud resources (AWS S3, Azure)
  {Colors.WARNING}graphql <url>{Colors.ENDC}     GraphQL introspection
  {Colors.WARNING}dns <domain>{Colors.ENDC}      DNS reconnaissance (zone transfer, subdomains)
  {Colors.WARNING}jwt <token>{Colors.ENDC}       JWT decoder and analyzer
  {Colors.WARNING}hashcat{Colors.ENDC}           Crack found hashes with hashcat
"""
        print(help_text)

    def cmd_modules(self, args):
        """عرض جميع الوحدات المتاحة"""
        print(f"{Colors.OKCYAN}Available Modules:{Colors.ENDC}")
        print("  - Fuzzer, SQLi, XSS, LFI, Exploit, WAF Bypass, Credentials, Hashcat")
        print("  - Chain, Nuclei, API, Post-Exploit, SSRF, XXE, Modern (GraphQL)")
        print("  - Scheduler, Storage, XSS Exploit, Auto-Updater, Smart Helper, Advanced Report")
        print(f"{Colors.OKGREEN}  - NEW: Cloud Enumeration, DNS Recon, JWT Tools, GraphQL Enum{Colors.ENDC}")
        print(f"\n{Colors.DIM}Use 'help' for command details.{Colors.ENDC}")

    def cmd_report(self, args):
        """توليد تقرير HTML و JSON"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] No scan results. Run 'scan' first.{Colors.ENDC}")
            return
        adv = NPXAdvancedReport(self.framework)
        adv.run(self.framework.vulnerabilities, self.framework.exploits)

    def cmd_nuclei(self, args):
        """تشغيل Nuclei للكشف عن CVEs"""
        if not args:
            print(f"{Colors.FAIL}[!] Usage: nuclei <url>{Colors.ENDC}")
            return
        from modules.nuclei import NPXNucleiIntegration
        nuclei = NPXNucleiIntegration(self.framework)
        nuclei.run(args[0])

    def cmd_bypass(self, args):
        """تشغيل محرك تجاوز WAF"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        waf = NPXWAFBypassEngine(self.framework)
        waf.run(self.framework.recon.discovered_urls['internal'], self.framework.vulnerabilities)

    def cmd_api(self, args):
        """تشغيل خادم REST API"""
        api = NPXRESTAPI(self.framework)
        api.start()

    def cmd_chain(self, args):
        """بناء سلسلة استغلال"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        chain = NPXExploitChainBuilder(self.framework)
        chain.run(self.framework.vulnerabilities)

    def cmd_postexploit(self, args):
        """تشغيل وحدة ما بعد الاستغلال"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        pe = NPXPostExploit(self.framework)
        pe.run(self.framework.vulnerabilities)

    def cmd_ssrf(self, args):
        """تشغيل فحص SSRF"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        ssrf = NPXSSRFScanner(self.framework)
        ssrf.run(self.framework.recon.discovered_urls['internal'])

    def cmd_xxe(self, args):
        """تشغيل فحص XXE"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        xxe = NPXXMLEngine(self.framework)
        xxe.run(self.framework.recon.discovered_urls['internal'])

    def cmd_schedule(self, args):
        """إدارة الجدولة التلقائية"""
        if len(args) < 2:
            print(f"{Colors.FAIL}[!] Usage: schedule add <target> <seconds>{Colors.ENDC}")
            print(f"{Colors.DIM}       schedule list{Colors.ENDC}")
            print(f"{Colors.DIM}       schedule stop <id>{Colors.ENDC}")
            return
        if args[0] == 'add':
            target = args[1]
            interval = int(args[2]) if len(args) > 2 else 3600
            self.framework.scheduler.add_job(target, interval)
        elif args[0] == 'list':
            self.framework.scheduler.list_jobs()
        elif args[0] == 'stop':
            if len(args) > 1:
                try:
                    job_id = int(args[1])
                    self.framework.scheduler.stop_job(job_id - 1)
                except ValueError:
                    print(f"{Colors.FAIL}[!] Invalid job ID.{Colors.ENDC}")

    def cmd_history(self, args):
        """عرض تاريخ الفحوصات"""
        self.framework.storage.get_history()

    def cmd_xss_exploit(self, args):
        """استغلال ثغرات XSS"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        xss_vulns = [v for v in self.framework.vulnerabilities if v['type'] == 'XSS']
        if xss_vulns:
            xss = NPXXSSExploit(self.framework)
            xss.run(xss_vulns)
        else:
            print(f"{Colors.DIM}[-] No XSS vulnerabilities found.{Colors.ENDC}")

    def cmd_update(self, args):
        """التحقق من التحديثات"""
        updater = NPXAutoUpdater(self.framework)
        updater.run()

    def cmd_suggest(self, args):
        """اقتراحات ذكية"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        helper = NPXSmartHelper(self.framework)
        helper.run(self.framework.vulnerabilities)

    def cmd_info(self, args):
        """عرض معلومات التكوين"""
        print(f"{Colors.OKCYAN}NPX Framework v1.0 Ultimate{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  DB: scan_results/npx_scan_history.db")
        print(f"  Output Dir: {self.framework.config.output_dir}")
        print(f"  Timeout: {self.framework.config.timeout}s")
        print(f"  Follow Redirects: {self.framework.config.follow_redirects}")
        print(f"  Verify SSL: {self.framework.config.verify_ssl}")

    def cmd_exit(self, args):
        """الخروج من البرنامج"""
        print(f"{Colors.DIM}Goodbye!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        """مسح الشاشة"""
        os.system('clear' if os.name == 'posix' else 'cls')

    # ============= الأوامر الجديدة =============

    def cmd_cloud(self, args):
        """فحص الموارد السحابية"""
        if not args:
            print(f"{Colors.FAIL}[!] Usage: cloud <domain>{Colors.ENDC}")
            return
        try:
            from modules.cloud_enum import CloudEnum
            ce = CloudEnum(args[0])
            print(f"{Colors.OKCYAN}[*] Scanning cloud resources for: {args[0]}{Colors.ENDC}")
            
            buckets = ce.enumerate_aws()
            if buckets:
                print(f"{Colors.OKGREEN}[+] Found S3 buckets:{Colors.ENDC}")
                for b in buckets:
                    print(f"  - {b}")
            else:
                print(f"{Colors.DIM}[-] No S3 buckets found.{Colors.ENDC}")
                
            azure = ce.enumerate_azure()
            if azure:
                print(f"{Colors.OKGREEN}[+] Found Azure storage:{Colors.ENDC}")
                for a in azure:
                    print(f"  - {a}")
            else:
                print(f"{Colors.DIM}[-] No Azure storage found.{Colors.ENDC}")
                
            gcp = ce.enumerate_gcp()
            if gcp:
                print(f"{Colors.OKGREEN}[+] Found GCP buckets:{Colors.ENDC}")
                for g in gcp:
                    print(f"  - {g}")
            else:
                print(f"{Colors.DIM}[-] No GCP buckets found.{Colors.ENDC}")
                
        except ImportError as e:
            print(f"{Colors.FAIL}[!] Missing dependencies: {e}{Colors.ENDC}")
            print(f"{Colors.DIM}Install: pip install boto3 azure-storage-blob requests{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_graphql(self, args):
        """فحص GraphQL Introspection"""
        if not args:
            print(f"{Colors.FAIL}[!] Usage: graphql <url>{Colors.ENDC}")
            return
        try:
            from modules.graphql_enum import GraphQLEnum
            ge = GraphQLEnum(args[0])
            print(f"{Colors.OKCYAN}[*] Running GraphQL introspection on: {args[0]}{Colors.ENDC}")
            
            result = ge.introspect()
            if result and 'data' in result:
                schema = ge.get_schema_dump()
                if schema:
                    print(f"{Colors.OKGREEN}[+] Schema dump successful!{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}[*] Found {len(schema)} types{Colors.ENDC}")
                    for i, (name, info) in enumerate(list(schema.items())[:10]):
                        fields = ', '.join(info.get('fields', [])[:3])
                        print(f"  {Colors.WARNING}{i+1}.{Colors.ENDC} {name} ({info.get('kind', 'Unknown')})")
                        if fields:
                            print(f"     Fields: {fields}{'...' if len(info.get('fields', [])) > 3 else ''}")
                    if len(schema) > 10:
                        print(f"{Colors.DIM}  ... and {len(schema)-10} more types{Colors.ENDC}")
                else:
                    print(f"{Colors.DIM}[-] No schema data found.{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[-] No introspection data. GraphQL endpoint may be protected.{Colors.ENDC}")
                print(f"{Colors.DIM}    Try: The endpoint might require authentication or introspection is disabled.{Colors.ENDC}")
                
        except ImportError as e:
            print(f"{Colors.FAIL}[!] Missing dependencies: {e}{Colors.ENDC}")
            print(f"{Colors.DIM}Install: pip install graphql-core requests{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_dns(self, args):
        """إعادة اكتشاف DNS"""
        if not args:
            print(f"{Colors.FAIL}[!] Usage: dns <domain>{Colors.ENDC}")
            return
        try:
            from modules.dns_recon import DNSRecon
            dr = DNSRecon(args[0])
            print(f"{Colors.OKCYAN}[*] DNS reconnaissance for: {args[0]}{Colors.ENDC}")
            
            result = dr.zone_transfer()
            if "possible" in result.lower():
                print(f"{Colors.WARNING}[!] {result}{Colors.ENDC}")
            else:
                print(f"{Colors.DIM}[-] {result}{Colors.ENDC}")
            
            subdomains = dr.subdomain_bruteforce()
            if subdomains:
                print(f"{Colors.OKGREEN}[+] Found subdomains:{Colors.ENDC}")
                for i, sub in enumerate(subdomains, 1):
                    print(f"  {Colors.WARNING}{i}.{Colors.ENDC} {sub}")
            else:
                print(f"{Colors.DIM}[-] No subdomains found with default wordlist.{Colors.ENDC}")
            
            records = dr.get_all_records()
            print(f"\n{Colors.OKCYAN}[*] DNS Records:{Colors.ENDC}")
            for rtype, values in records.items():
                if values:
                    print(f"  {Colors.WARNING}{rtype}:{Colors.ENDC} {', '.join(values[:3])}{'...' if len(values) > 3 else ''}")
                    
        except ImportError as e:
            print(f"{Colors.FAIL}[!] Missing dependencies: {e}{Colors.ENDC}")
            print(f"{Colors.DIM}Install: pip install dnspython{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_jwt(self, args):
        """تحليل JWT Token"""
        if not args:
            print(f"{Colors.FAIL}[!] Usage: jwt <token>{Colors.ENDC}")
            return
        try:
            from modules.jwt_tools import JWTTools
            jt = JWTTools(args[0])
            print(f"{Colors.OKCYAN}[*] Analyzing JWT token...{Colors.ENDC}")
            
            header = jt.get_header()
            if header:
                print(f"{Colors.OKGREEN}[+] Header:{Colors.ENDC}")
                print(json.dumps(header, indent=2))
            else:
                print(f"{Colors.FAIL}[-] Failed to parse header.{Colors.ENDC}")
                
            decoded = jt.decode()
            if decoded:
                print(f"{Colors.OKGREEN}[+] Payload:{Colors.ENDC}")
                print(json.dumps(decoded, indent=2))
                
                issues = jt.check_common_issues()
                if issues:
                    print(f"\n{Colors.WARNING}[!] Issues found:{Colors.ENDC}")
                    for issue in issues:
                        print(f"  {Colors.WARNING}⚠{Colors.ENDC} {issue}")
                else:
                    print(f"\n{Colors.OKGREEN}[✓] No obvious security issues found.{Colors.ENDC}")
                    
            else:
                print(f"{Colors.FAIL}[-] Failed to decode token. Invalid JWT format.{Colors.ENDC}")
                
        except ImportError as e:
            print(f"{Colors.FAIL}[!] Missing dependencies: {e}{Colors.ENDC}")
            print(f"{Colors.DIM}Install: pip install pyjwt{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_hashcat(self, args):
        """تشغيل Hashcat لكسر الهاشات المستخرجة"""
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        hashcat = NPXHashcatIntegration(self.framework)
        hashcat.run(self.framework.vulnerabilities)

# تصدير الفئة للاستخدام الخارجي
if __name__ == "__main__":
    # هذا الجزء ليس ضرورياً لأن الفئة تستخدم داخل الإطار
    pass
