from dataclasses import dataclass, field
from typing import List
import json

@dataclass
class NPXConfig:
    target_url: str = ""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NPX-Scanner/1.0"
    threads: int = 20
    timeout: int = 10
    delay_min: float = 0.5
    delay_max: float = 2.0
    max_depth: int = 2
    output_dir: str = "./npx_output"
    follow_redirects: bool = True
    verify_ssl: bool = False
    use_proxy: bool = False
    proxy_list: List[str] = field(default_factory=list)
    cookies_file: str = ""
    headers_file: str = ""
    auth_token: str = ""

    def save_to_file(self, path: str):
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def load_from_file(self, path: str):
        with open(path, 'r') as f:
            data = json.load(f)
            for key, value in data.items():
                setattr(self, key, value)
