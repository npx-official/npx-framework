# modules/dns_recon.py
import dns.resolver
import dns.zone
import dns.query
import subprocess
import socket

class DNSRecon:
    def __init__(self, domain):
        self.domain = domain
        self.wordlist = [
            "www", "mail", "admin", "dev", "test", "api", "app", "blog",
            "shop", "store", "ftp", "ssh", "web", "ns1", "ns2", "dns",
            "vpn", "remote", "panel", "cpanel", "whm", "webmail",
            "autodiscover", "m", "mobile", "wap", "secure", "portal",
            "support", "help", "docs", "wiki", "git", "jenkins",
            "jira", "confluence", "nexus", "sonar", "monitor", "status",
            "cdn", "static", "assets", "media", "images", "video"
        ]
        
    def zone_transfer(self):
        """Attempt DNS zone transfer"""
        try:
            ns = dns.resolver.resolve(self.domain, 'NS')
            for server in ns:
                try:
                    # Try zone transfer
                    zone = dns.zone.from_xfr(dns.query.xfr(str(server), self.domain))
                    if zone:
                        return f"Zone transfer possible! Server: {server}"
                except:
                    continue
            return "No zone transfer possible"
        except:
            return "DNS resolution failed"
    
    def subdomain_bruteforce(self):
        """Brute force subdomains"""
        found = []
        for sub in self.wordlist:
            try:
                full_domain = f"{sub}.{self.domain}"
                dns.resolver.resolve(full_domain, 'A')
                found.append(full_domain)
            except:
                continue
        return found
    
    def get_all_records(self):
        """Get all DNS records for domain"""
        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'CNAME', 'TXT', 'SOA']
        
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, rtype)
                records[rtype] = [str(r) for r in answers]
            except:
                records[rtype] = []
                
        return records
