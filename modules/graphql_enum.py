# modules/graphql_enum.py
import requests
import json

class GraphQLEnum:
    def __init__(self, target):
        self.target = target
        self.introspection_query = """
        query {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    name
                    kind
                    description
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                        args {
                            name
                            type {
                                name
                                kind
                            }
                        }
                    }
                    inputFields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                    enumValues {
                        name
                        description
                    }
                }
            }
        }
        """
        
    def introspect(self):
        """Run GraphQL introspection query"""
        headers = {'Content-Type': 'application/json'}
        payload = {'query': self.introspection_query}
        
        try:
            response = requests.post(self.target, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None
    
    def get_schema_dump(self):
        """Get simplified schema dump"""
        result = self.introspect()
        if not result or 'data' not in result:
            return None
            
        schema = {}
        types = result['data'].get('__schema', {}).get('types', [])
        
        for t in types:
            if not t['name'].startswith('__'):
                schema[t['name']] = {
                    'kind': t.get('kind'),
                    'fields': [f.get('name') for f in t.get('fields', []) if f]
                }
        return schema
    
    def test_query(self, query):
        """Test custom GraphQL query"""
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query}
        
        try:
            response = requests.post(self.target, json=payload, headers=headers, timeout=10)
            return response.json()
        except:
            return None
