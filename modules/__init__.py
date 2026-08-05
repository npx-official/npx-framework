# modules/__init__.py
from .fuzzer import NPXFuzzerModule
from .sqli import NPXSQLiModule
from .xss import NPXXSSModule
from .lfi import NPXLFIModule
from .exploit import NPXExploitEngine
from .wordpress import NPXWordpressScanner
from .subdomain import NPXSubdomainTakeover
from .credential import NPXCredentialHarvester
from .hashcat import NPXHashcatIntegration
from .ssrf import NPXSSRFScanner
from .xxe import NPXXMLEngine
from .modern import NPXModernScanner
from .waf_bypass import NPXWAFBypassEngine
from .chain import NPXExploitChainBuilder
from .postexploit import NPXPostExploit
from .xss_exploit import NPXXSSExploit
from .nuclei import NPXNucleiIntegration
# الوحدات الجديدة
from .cloud_enum import CloudEnum
from .dns_recon import DNSRecon
from .graphql_enum import GraphQLEnum
from .jwt_tools import JWTTools
