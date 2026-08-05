import time
import random
import http.cookiejar
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.config import NPXConfig
from core.colors import Colors

class NPXSessionManager:
    def __init__(self, config: NPXConfig):
        self.config = config
        self.session = None
        self.cookies = http.cookiejar.CookieJar()
        self.headers = {
            'User-Agent': config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.last_request_time = 0

    def get_session(self):
        if self.session is None:
            self.session = requests.Session()
            self.session.cookies = self.cookies
            self.session.headers.update(self.headers)
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            if self.config.use_proxy and self.config.proxy_list:
                proxy = random.choice(self.config.proxy_list)
                self.session.proxies = {"http": proxy, "https": proxy}
            self.session.verify = self.config.verify_ssl
        return self.session

    def send_request(self, method: str, url: str, **kwargs):
        session = self.get_session()
        if session is None:
            return None
        now = time.time()
        time_since_last = now - self.last_request_time
        delay = random.uniform(self.config.delay_min, self.config.delay_max)
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        self.last_request_time = time.time()
        if random.random() < 0.2:
            new_ua = f"Mozilla/5.0 (Windows NT {random.randint(6,10)}.0; Win64; x64) NPX-Scanner/1.0"
            session.headers.update({'User-Agent': new_ua})
        try:
            response = session.request(method, url, timeout=self.config.timeout, **kwargs)
            return response
        except Exception as e:
            print(f"{Colors.FAIL}[!] Request Error: {e}{Colors.ENDC}")
            return None

    def update_cookies(self, cookies_dict: dict):
        for name, value in cookies_dict.items():
            self.cookies.set_cookie(http.cookiejar.Cookie(
                version=0, name=name, value=value,
                port=None, port_specified=False,
                domain="", domain_specified=False, domain_initial_dot=False,
                path="/", path_specified=True,
                secure=False, expires=None, discard=True,
                comment=None, comment_url=None, rest=None
            ))
