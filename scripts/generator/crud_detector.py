"""
CRUD Resource Detector

Analyzes OpenAPI specification to detect resources that support full CRUD operations
and should have declarative modules generated.
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class CRUDDetector:
    """Detect resources with CRUD operations from OpenAPI spec."""
    
    def __init__(self, parser):
        """Initialize with OpenAPI parser."""
        self.parser = parser
        self.resources = {}
    
    def detect_resources(self) -> Dict[str, List[Dict]]:
        """
        Detect all resources that have CRUD operations.
        
        Returns:
            Dict mapping product to list of resource definitions
        """
        endpoints = self.parser.get_endpoints()
        resource_map = {}
        
        # Group endpoints by base resource path
        for endpoint, methods in endpoints.items():
            base_path, resource_id = self._extract_base_path(endpoint)
            
            if not base_path:
                continue
            
            if base_path not in resource_map:
                resource_map[base_path] = {
                    'base_path': base_path,
                    'id_path': endpoint if resource_id else None,
                    'operations': {},
                    'schemas': {}
                }
            
            # Store operations
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    continue
                
                # Determine operation type
                if resource_id:
                    # Operations on specific resource
                    if method.lower() == 'get':
                        resource_map[base_path]['operations']['get_one'] = operation
                        resource_map[base_path]['id_path'] = endpoint
                    elif method.lower() in ['patch', 'put']:
                        resource_map[base_path]['operations']['update'] = operation
                        resource_map[base_path]['update_method'] = method.upper()
                    elif method.lower() == 'delete':
                        resource_map[base_path]['operations']['delete'] = operation
                else:
                    # Operations on collection
                    if method.lower() == 'get':
                        resource_map[base_path]['operations']['list'] = operation
                    elif method.lower() == 'post':
                        resource_map[base_path]['operations']['create'] = operation
                        # Extract schema from POST operation
                        schema = self._extract_schema(operation)
                        if schema:
                            resource_map[base_path]['schemas']['create'] = schema
        
        # Filter resources that have sufficient CRUD operations
        crud_resources = self._filter_crud_resources(resource_map)
        
        # Categorize by product
        result = {
            'core': [],
            'stream': [],
            'edge': [],
            'search': [],
            'lake': []
        }
        
        for resource in crud_resources:
            product = self.parser.categorize_endpoint(resource['base_path'])
            resource['product'] = product
            result[product].append(resource)
        
        return result
    
    def _extract_base_path(self, endpoint: str) -> Tuple[Optional[str], bool]:
        """
        Extract base resource path and whether this is an ID path.
        
        Args:
            endpoint: API endpoint like /system/users or /system/users/{id}
        
        Returns:
            (base_path, has_id)
        """
        # Check if endpoint has an ID parameter
        has_id = '{' in endpoint
        
        if has_id:
            # Remove ID parameter to get base path
            base_path = re.sub(r'/\{[^}]+\}$', '', endpoint)
            return base_path, True
        else:
            return endpoint, False
    
    def _extract_schema(self, operation: Dict) -> Optional[Dict]:
        """Extract schema from operation request body."""
        request_body = operation.get('requestBody', {})
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        schema = json_content.get('schema', {})
        
        if '$ref' in schema:
            return self.parser._resolve_schema_ref(schema['$ref'])
        elif 'properties' in schema:
            return schema.get('properties', {})
        
        return None
    
    def _filter_crud_resources(self, resource_map: Dict) -> List[Dict]:
        """
        Filter resources that have sufficient CRUD operations.
        
        A resource must have:
        - list or get_one operation
        - create operation
        - At least one of: update or delete
        """
        crud_resources = []
        
        for base_path, resource in resource_map.items():
            ops = resource['operations']
            
            # Must have read operation
            has_read = 'list' in ops or 'get_one' in ops
            
            # Must have create
            has_create = 'create' in ops
            
            # Must have update or delete
            has_modify = 'update' in ops or 'delete' in ops
            
            # Must have ID path for get/update/delete
            has_id_path = resource.get('id_path') is not None
            
            if has_read and has_create and has_modify and has_id_path:
                # Extract ID parameter name
                id_match = re.search(r'\{([^}]+)\}', resource['id_path'])
                resource['id_param'] = id_match.group(1) if id_match else 'id'
                
                # Generate resource name
                resource['resource_name'] = self._generate_resource_name(base_path)
                
                # Generate title case name
                resource['resource_title'] = self._generate_title(resource['resource_name'])
                
                crud_resources.append(resource)
        
        return crud_resources
    
    def _generate_resource_name(self, base_path: str) -> str:
        """
        Generate a resource name from base path.
        
        Examples:
            /system/users -> user
            /master/groups -> worker_group (special case)
            /pipelines -> pipeline
            /system/outputs -> output
            /parquet-schema -> parquet_schema
        """
        # Remove leading slash and split
        parts = base_path.strip('/').split('/')
        
        # Get the last part
        name = parts[-1]
        
        # Remove pluralization
        if name.endswith('ies'):
            name = name[:-3] + 'y'
        elif name.endswith('ses'):
            name = name[:-2]
        elif name.endswith('s') and not name.endswith('ss'):
            name = name[:-1]
        
        # Replace hyphens with underscores for valid Python module names
        name = name.replace('-', '_')
        
        # Special cases
        if base_path == '/master/groups':
            return 'worker_group'
        elif base_path == '/system/roles':
            return 'role'
        elif base_path == '/system/teams':
            return 'team'
        elif base_path == '/system/certificates':
            return 'certificate'
        elif base_path == '/system/secrets':
            return 'secret'
        
        return name
    
    def _generate_title(self, resource_name: str) -> str:
        """Generate title case name from resource name."""
        # Convert snake_case to TitleCase
        parts = resource_name.split('_')
        return ''.join(word.capitalize() for word in parts)
    
    def get_resource_params(self, resource: Dict) -> Dict[str, Dict]:
        """
        Extract parameters for a resource from its schema.
        
        Returns:
            Dict of parameter definitions
        """
        params = {}
        
        resource_name = resource.get('resource_name', '')
        
        # Special handling for inputs and outputs - they have many type-specific parameters
        # Use a generic 'conf' dict parameter instead of extracting all individual parameters
        if resource_name in ['input', 'output']:
            params['conf'] = {
                'type': 'dict',
                'description': f'Configuration parameters for the {resource_name}. Parameters vary by type.',
                'required': False
            }
            return params
        
        # Get schema from create operation
        schema = resource.get('schemas', {}).get('create', {})
        
        for prop_name, prop_def in schema.items():
            if prop_name == resource.get('id_param', 'id'):
                # ID is handled separately
                continue
            
            param_type = self.parser._convert_type(prop_def)
            description = prop_def.get('description', '') or prop_def.get('title', '')
            
            params[prop_name] = {
                'type': param_type,
                'description': description,
                'required': False  # Will be determined from required array
            }
        
        return params
    
    def format_params_for_module(self, params: Dict) -> str:
        """
        Format parameters for Ansible module documentation (YAML format).
        
        Returns YAML-formatted string for module documentation.
        """
        lines = []
        
        for name, info in params.items():
            lines.append(f"    {name}:")
            lines.append(f"        description:")
            
            # Handle description
            desc = info['description'] or f'The {name} parameter'
            lines.append(f"            - {desc}")
            
            lines.append(f"        type: {info['type']}")
            
            # Add elements for lists
            if info['type'] == 'list':
                lines.append(f"        elements: str")
            
            lines.append(f"        required: false")
        
        return '\n'.join(lines)
    
    def format_params_for_argspec(self, params: Dict) -> str:
        """
        Format parameters for Ansible argument_spec (Python dict format).
        
        Returns Python code string for argument_spec.
        """
        lines = []
        
        for name, info in params.items():
            param_def = f"        {name}=dict(type='{info['type']}', required=False)"
            lines.append(param_def)
        
        return ',\n'.join(lines) if lines else ''


