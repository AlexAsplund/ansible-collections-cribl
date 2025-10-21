"""
OpenAPI Specification Parser

Handles loading and parsing OpenAPI/Swagger specifications.
"""

import yaml
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class OpenAPIParser:
    """Parse and extract information from OpenAPI specifications."""
    
    # Product categorization patterns
    PRODUCT_PATTERNS = {
        'edge': [r'^/edge/.*'],
        'search': [r'^/search/.*'],
        'lake': [r'^/products/lake/.*'],
        'stream': [
            r'^/system/inputs.*',
            r'^/system/outputs.*',
            r'^/pipelines.*',
            r'^/routes.*',
            r'^/packs.*',
            r'^/lib/.*',
            r'^/p/.*',
        ],
        'core': [
            r'^/system/(?!inputs|outputs).*',
            r'^/master/.*',
            r'^/auth/.*',
            r'^/health.*',
            r'^/version.*',
            r'^/jobs.*',
            r'^/ui/.*',
            r'^/security/.*',
            r'^/authorize/.*',
            r'^/ai/.*',
        ]
    }

    def __init__(self, spec_file: str):
        self.spec_file = Path(spec_file)
        self.spec = None

    def load(self) -> Dict:
        """Load the OpenAPI specification from file."""
        print(f"Loading OpenAPI spec from {self.spec_file}...")
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            self.spec = yaml.safe_load(f)
        print(f"Loaded spec version {self.spec['info']['version']}")
        return self.spec

    def get_endpoints(self) -> Dict:
        """Get all endpoints from the spec."""
        return self.spec.get('paths', {})

    def categorize_endpoint(self, endpoint: str) -> str:
        """Determine which product collection an endpoint belongs to."""
        for product, patterns in self.PRODUCT_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, endpoint):
                    return product
        return 'core'

    def get_operation_info(self, operation: Dict) -> Tuple[str, str]:
        """Extract operation summary and description."""
        summary = operation.get('summary', '').strip() or \
                  operation.get('description', '').split('\n')[0].strip()
        description = operation.get('description', '').strip() or summary
        return summary, description

    def should_generate(self, endpoint: str, method: str, operation: Dict) -> bool:
        """Check if module should be generated for this endpoint."""
        if operation.get('deprecated', False):
            return False
        if method.lower() not in ['get', 'post', 'put', 'patch', 'delete']:
            return False
        return True

    def extract_parameters(self, operation: Dict, endpoint: str) -> Dict:
        """Extract all parameters from an operation."""
        params = {}
        
        # Path parameters
        path_params = re.findall(r'\{([^}]+)\}', endpoint)
        for param in path_params:
            params[param] = {
                'description': f'The {param} identifier',
                'type': 'str',
                'required': True,
                'location': 'path'
            }
        
        # Query parameters
        for param in operation.get('parameters', []):
            if param.get('in') == 'query':
                params[param['name']] = {
                    'description': param.get('description', ''),
                    'type': self._convert_type(param.get('schema', {})),
                    'required': param.get('required', False),
                    'location': 'query'
                }
        
        # Request body parameters
        request_body = operation.get('requestBody', {})
        if request_body:
            body_params = self._extract_body_params(request_body)
            params.update(body_params)
        
        return params

    def _extract_body_params(self, request_body: Dict) -> Dict:
        """Extract parameters from request body schema."""
        params = {}
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})
        
        if '$ref' in schema:
            properties = self._resolve_schema_ref(schema['$ref'])
            for prop_name, prop_def in properties.items():
                params[prop_name] = {
                    'description': prop_def.get('description', prop_def.get('title', '')),
                    'type': self._convert_type(prop_def),
                    'required': False,
                    'location': 'body'
                }
        
        return params

    def _resolve_schema_ref(self, ref: str) -> Dict:
        """Resolve a $ref to actual schema properties."""
        ref_path = ref.split('/')
        schema = self.spec
        for part in ref_path:
            if part == '#':
                continue
            schema = schema.get(part, {})
        return schema.get('properties', {})

    def _convert_type(self, schema: Dict) -> str:
        """Convert OpenAPI type to Ansible module type."""
        type_map = {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'list',
            'object': 'dict'
        }
        return type_map.get(schema.get('type', 'str'), 'str')

