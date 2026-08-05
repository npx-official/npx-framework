# modules/cloud_enum.py
import requests
import json
import re

class CloudEnum:
    def __init__(self, target):
        self.target = target.lower()
        self.buckets = []
        self.azure_storage = []
        
    def enumerate_aws(self):
        """Enumerate AWS S3 buckets"""
        patterns = [
            f"http://{self.target}.s3.amazonaws.com",
            f"http://s3.amazonaws.com/{self.target}",
            f"http://{self.target}.s3-website.amazonaws.com",
            f"http://s3.amazonaws.com/{self.target}-public",
            f"http://{self.target}.s3.us-east-1.amazonaws.com"
        ]
        
        for url in patterns:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    self.buckets.append(url)
                elif resp.status_code == 403:
                    # Bucket exists but is private
                    self.buckets.append(f"{url} (private)")
            except requests.exceptions.RequestException:
                continue
                
        return self.buckets
    
    def enumerate_azure(self):
        """Enumerate Azure storage accounts"""
        patterns = [
            f"https://{self.target}.blob.core.windows.net",
            f"https://{self.target}.file.core.windows.net",
            f"https://{self.target}.queue.core.windows.net",
            f"https://{self.target}.table.core.windows.net"
        ]
        
        for url in patterns:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    self.azure_storage.append(url)
                elif resp.status_code == 403:
                    self.azure_storage.append(f"{url} (exists but inaccessible)")
            except requests.exceptions.RequestException:
                continue
                
        return self.azure_storage
    
    def enumerate_gcp(self):
        """Enumerate Google Cloud Storage buckets (if needed)"""
        # GCP enumeration
        patterns = [
            f"https://storage.googleapis.com/{self.target}",
            f"https://{self.target}.storage.googleapis.com"
        ]
        gcp_buckets = []
        for url in patterns:
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    gcp_buckets.append(url)
            except:
                continue
        return gcp_buckets
