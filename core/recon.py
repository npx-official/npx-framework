import re
import urllib.parse
from bs4 import BeautifulSoup
from core.colors import Colors

class NPXReconEngine:
    def __init__(self, session_manager):
        self.session = session_manager
        self.discovered_urls = {
            'internal': set(),
            'external': set(),
            'javascript': set(),
            'hidden': set()
        }
        self.subdomains = set()
        self.technologies = {}

    def crawl_sitemap(self, base_url=None):
        if base_url is None:
            base_url = self.session.config.target_url
        if not base_url:
            return
        print(f"{Colors.OKCYAN}[*] Crawling: {base_url}{Colors.ENDC}")
        response = self.session.send_request("GET", base_url)
        if not response or response.status_code != 200:
            return
        html = response.text
        links = self.extract_links_from_html(base_url, html)
        self.discovered_urls['internal'].update(links.get('internal', set()))
        self.discovered_urls['external'].update(links.get('external', set()))
        self.discovered_urls['javascript'].update(links.get('js', set()))
        # اكتشاف النطاقات الفرعية
        self.subdomains.update(self.discover_subdomains(base_url, html))

    def extract_links_from_html(self, url: str, html_content: str):
        links = {'internal': set(), 'external': set(), 'js': set()}
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup.find_all(['a', 'link', 'script', 'img', 'form']):
                href = tag.get('href') or tag.get('src')
                if not href:
                    continue
                if href.startswith('javascript:') or href.startswith('data:'):
                    continue
                full_url = urllib.parse.urljoin(url, href)
                if any(ext in href for ext in ['.js', '.json', '.mjs']):
                    links['js'].add(full_url)
                elif self.is_internal_link(url, full_url):
                    links['internal'].add(full_url)
                else:
                    links['external'].add(full_url)
        except Exception as e:
            print(f"{Colors.DIM}[!] BS4 parse error: {e}{Colors.ENDC}")
        return links

    def is_internal_link(self, base_url: str, target_url: str) -> bool:
        if not target_url:
            return False
        base_domain = urllib.parse.urlparse(base_url).netloc
        target_domain = urllib.parse.urlparse(target_url).netloc
        return base_domain == target_domain

    def discover_subdomains(self, url: str, html_content: str) -> set:
        found = set()
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            return found
        domain_parts = parsed.netloc.split('.')
        if len(domain_parts) >= 2:
            base_domain = '.'.join(domain_parts[-2:])
        else:
            base_domain = parsed.netloc
        pattern = r'([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9])\.' + re.escape(base_domain)
        for match in re.finditer(pattern, html_content, re.IGNORECASE):
            sub = match.group(1) + '.' + base_domain
            if sub != parsed.netloc:
                found.add(sub)
        return found

    def detect_technologies(self, response):
        # placeholder
        return {}
