import os
import sys
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
            'schedule': self.cmd_schedule,
            'history': self.cmd_history,
            'xss_exploit': self.cmd_xss_exploit,
            'update': self.cmd_update,
            'suggest': self.cmd_suggest,
        }
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
{Colors.DIM}  Type 'help' for available commands.{Colors.ENDC}
"""
        print(banner)

    def run(self):
        while True:
            try:
                cmd = input(f"{Colors.OKGREEN}npx> {Colors.ENDC}").strip()
                if not cmd:
                    continue
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
            except Exception as e:
                print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")

    def cmd_scan(self, args):
        if not args:
            print(f"{Colors.FAIL}[!] Usage: scan <target_url>{Colors.ENDC}")
            return
        target = args[0]
        self.framework.config.target_url = target
        print(f"{Colors.OKCYAN}[*] Target set to: {target}{Colors.ENDC}")

        # Recon
        self.framework.recon.crawl_sitemap()
        internal_urls = self.framework.recon.discovered_urls['internal']
        if not internal_urls:
            internal_urls.add(target)  # على الأقل الصفحة الرئيسية

        # Modules
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
        sub.run(self.framework.recon.subdomains)

        cred = NPXCredentialHarvester(self.framework)
        cred.run(internal_urls)

        # تخزين النتائج
        self.framework.vulnerabilities = sqli.vulnerabilities + xss.vulnerabilities + lfi.vulnerabilities
        self.framework.exploits = exploit.exploited

        # حفظ في قاعدة البيانات
        modules_used = ['Fuzzer', 'SQLi', 'XSS', 'LFI', 'Exploit', 'Wordpress', 'Subdomain', 'Credentials']
        self.framework.storage.save_scan(target, modules_used, len(self.framework.vulnerabilities), self.framework.vulnerabilities)

        # اقتراحات
        helper = NPXSmartHelper(self.framework)
        helper.run(self.framework.vulnerabilities)

        print(f"{Colors.OKGREEN}[+] Scan completed! Use 'report' to generate HTML/PDF report.{Colors.ENDC}")

    def cmd_help(self, args):
        help_text = f"""
{Colors.OKCYAN}Commands:{Colors.ENDC}
  {Colors.WARNING}help{Colors.ENDC}          Show this help
  {Colors.WARNING}scan <url>{Colors.ENDC}    Full scan
  {Colors.WARNING}modules{Colors.ENDC}       List modules
  {Colors.WARNING}report{Colors.ENDC}        Generate report (HTML+PDF)
  {Colors.WARNING}nuclei <url>{Colors.ENDC}  Run Nuclei
  {Colors.WARNING}bypass{Colors.ENDC}        WAF bypass
  {Colors.WARNING}chain{Colors.ENDC}         Build exploit chain
  {Colors.WARNING}api{Colors.ENDC}           Start REST API
  {Colors.WARNING}postexploit{Colors.ENDC}   Post-exploit
  {Colors.WARNING}ssrf{Colors.ENDC}          SSRF scan
  {Colors.WARNING}xxe{Colors.ENDC}           XXE scan
  {Colors.WARNING}schedule{Colors.ENDC}      Manage scheduled scans
  {Colors.WARNING}history{Colors.ENDC}       View scan history
  {Colors.WARNING}xss_exploit{Colors.ENDC}   Inject XSS payloads
  {Colors.WARNING}update{Colors.ENDC}        Check updates
  {Colors.WARNING}suggest{Colors.ENDC}       Smart suggestions
  {Colors.WARNING}info{Colors.ENDC}          Show config
  {Colors.WARNING}clear{Colors.ENDC}         Clear screen
  {Colors.WARNING}exit{Colors.ENDC}          Exit
"""
        print(help_text)

    def cmd_modules(self, args):
        print(f"{Colors.OKCYAN}Available Modules:{Colors.ENDC}")
        print("  - Fuzzer, SQLi, XSS, LFI, Exploit, WAF Bypass, Credentials, Hashcat")
        print("  - Chain, Nuclei, API, Post-Exploit, SSRF, XXE, Modern (GraphQL)")
        print("  - Scheduler, Storage, XSS Exploit, Auto-Updater, Smart Helper, Advanced Report")

    def cmd_report(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] No scan results. Run 'scan' first.{Colors.ENDC}")
            return
        adv = NPXAdvancedReport(self.framework)
        adv.run(self.framework.vulnerabilities, self.framework.exploits)

    def cmd_nuclei(self, args):
        if not args:
            print(f"{Colors.FAIL}[!] Usage: nuclei <url>{Colors.ENDC}")
            return
        from modules.nuclei import NPXNucleiIntegration
        nuclei = NPXNucleiIntegration(self.framework)
        nuclei.run(args[0])

    def cmd_bypass(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        waf = NPXWAFBypassEngine(self.framework)
        waf.run(self.framework.recon.discovered_urls['internal'], self.framework.vulnerabilities)

    def cmd_api(self, args):
        api = NPXRESTAPI(self.framework)
        api.start()

    def cmd_chain(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        chain = NPXExploitChainBuilder(self.framework)
        chain.run(self.framework.vulnerabilities)

    def cmd_postexploit(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        pe = NPXPostExploit(self.framework)
        pe.run(self.framework.vulnerabilities)

    def cmd_ssrf(self, args):
        ssrf = NPXSSRFScanner(self.framework)
        ssrf.run(self.framework.recon.discovered_urls['internal'])

    def cmd_xxe(self, args):
        xxe = NPXXMLEngine(self.framework)
        xxe.run(self.framework.recon.discovered_urls['internal'])

    def cmd_schedule(self, args):
        if len(args) < 2:
            print(f"{Colors.FAIL}[!] Usage: schedule add <target> <seconds>{Colors.ENDC}")
            return
        if args[0] == 'add':
            target = args[1]
            interval = int(args[2]) if len(args) > 2 else 3600
            self.framework.scheduler.add_job(target, interval)
        elif args[0] == 'list':
            self.framework.scheduler.list_jobs()
        elif args[0] == 'stop':
            if len(args) > 1:
                self.framework.scheduler.stop_job(int(args[1])-1)

    def cmd_history(self, args):
        self.framework.storage.get_history()

    def cmd_xss_exploit(self, args):
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
        updater = NPXAutoUpdater(self.framework)
        updater.run()

    def cmd_suggest(self, args):
        if not hasattr(self.framework, 'vulnerabilities'):
            print(f"{Colors.FAIL}[!] Run 'scan' first.{Colors.ENDC}")
            return
        helper = NPXSmartHelper(self.framework)
        helper.run(self.framework.vulnerabilities)

    def cmd_info(self, args):
        print(f"{Colors.OKCYAN}NPX Framework v1.0 Ultimate{Colors.ENDC}")
        print(f"  Target: {self.framework.config.target_url or 'Not set'}")
        print(f"  Threads: {self.framework.config.threads}")
        print(f"  DB: npx_scan_history.db")

    def cmd_exit(self, args):
        print(f"{Colors.DIM}Goodbye!{Colors.ENDC}")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system('clear' if os.name == 'posix' else 'cls')
