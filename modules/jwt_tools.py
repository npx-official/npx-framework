# modules/jwt_tools.py
import jwt
import base64
import json
import time

class JWTTools:
    def __init__(self, token):
        self.token = token.strip()
        
    def decode(self):
        """Decode JWT without signature verification"""
        try:
            return jwt.decode(self.token, options={"verify_signature": False})
        except jwt.InvalidTokenError:
            return None
    
    def get_header(self):
        """Extract JWT header"""
        try:
            header = jwt.get_unverified_header(self.token)
            return header
        except:
            return None
    
    def get_payload(self):
        """Extract JWT payload"""
        try:
            payload = jwt.decode(self.token, options={"verify_signature": False})
            return payload
        except:
            return None
    
    def verify_signature(self, secret):
        """Verify JWT signature with a secret"""
        try:
            jwt.decode(self.token, secret, algorithms=['HS256'])
            return True
        except:
            return False
    
    def brute_force_secret(self, wordlist_path):
        """Brute force JWT secret using wordlist"""
        try:
            with open(wordlist_path, 'r') as f:
                for line in f:
                    secret = line.strip()
                    try:
                        jwt.decode(self.token, secret, algorithms=['HS256'])
                        return f"Found secret: {secret}"
                    except:
                        continue
            return "Secret not found in wordlist"
        except FileNotFoundError:
            return "Wordlist file not found"
    
    def check_common_issues(self):
        """Check for common JWT security issues"""
        issues = []
        header = self.get_header()
        payload = self.get_payload()
        
        if header:
            if header.get('alg') == 'none':
                issues.append("Algorithm 'none' is insecure")
            if not header.get('kid'):
                issues.append("No kid (Key ID) specified")
        
        if payload:
            if 'exp' not in payload:
                issues.append("No expiration time (exp) set")
            elif payload['exp'] < time.time():
                issues.append("Token has expired")
            if 'iat' not in payload:
                issues.append("No issued at time (iat) set")
        
        return issues
