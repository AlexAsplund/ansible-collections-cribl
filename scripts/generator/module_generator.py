"""
Module Generator

Generates imperative Ansible modules from OpenAPI operations.
"""

import re
from pathlib import Path
from typing import Dict, List
from .templates import ModuleTemplate


class ModuleGenerator:
    """Generate imperative Ansible modules."""

    def __init__(self, output_dir: Path, product: str):
        self.output_dir = output_dir
        self.product = product
        self.template = ModuleTemplate()

    def sanitize_name(self, endpoint: str) -> str:
        """Convert API endpoint to valid module name."""
        name = endpoint.strip('/')
        
        # Remove product prefixes
        if self.product == 'edge':
            name = re.sub(r'^edge/', '', name)
        elif self.product == 'search':
            name = re.sub(r'^search/', '', name)
        elif self.product == 'lake':
            name = re.sub(r'^products/lake/', '', name)
        
        # Replace path parameters and special chars
        name = re.sub(r'\{[^}]+\}', 'id', name)
        name = name.replace('/', '_')
        name = re.sub(r'[^a-z0-9_]', '_', name.lower())
        name = re.sub(r'_+', '_', name).strip('_')
        
        # No prefix needed - clean module names are better
        return name

    def generate(self, module_name: str, endpoint: str, method: str,
                operation: Dict, params: Dict, summary: str, description: str) -> str:
        """Generate complete module code."""
        code_parts = [
            self.template.header(),
            self._generate_documentation(module_name, endpoint, method, summary, description, params),
            self.template.examples(module_name, summary, self.product),
            self.template.returns(),
            self.template.imports(self.product),
            self._generate_main_function(endpoint, method, params)
        ]
        
        return ''.join(code_parts)

    def _generate_documentation(self, module_name: str, endpoint: str, method: str,
                                summary: str, description: str, params: Dict) -> str:
        """Generate DOCUMENTATION block."""
        params_doc = self._format_params_doc(params)
        return self.template.documentation(
            module_name, summary, description, 
            endpoint, method, self.product, params_doc
        )

    def _format_params_doc(self, params: Dict) -> str:
        """Format parameters for documentation."""
        docs = []
        for name, info in params.items():
            doc = f"""    {name}:
        description:
            - {info['description'] or f'The {name} parameter'}
        type: {info['type']}
        required: {str(info['required']).lower()}"""
            docs.append(doc)
        return '\n'.join(docs)

    def _generate_main_function(self, endpoint: str, method: str, params: Dict) -> str:
        """Generate main() function."""
        arg_spec = self._format_arg_spec(params)
        path_params = re.findall(r'\{([^}]+)\}', endpoint)
        
        code = self.template.main_function_start(arg_spec)
        # Define endpoint first, before any substitution
        code += f'\n        endpoint = "{endpoint}"\n'
        code += self._generate_endpoint_substitution(endpoint, path_params)
        code += self._generate_data_preparation(params, path_params)
        code += self.template.api_call_without_endpoint_def(method)
        
        return code

    def _format_arg_spec(self, params: Dict) -> str:
        """Format argument_spec dict."""
        specs = []
        for name, info in params.items():
            spec = f"            {name}=dict(type='{info['type']}', required={info['required']})"
            specs.append(spec)
        return ',\n'.join(specs)

    def _generate_endpoint_substitution(self, endpoint: str, path_params: List[str]) -> str:
        """Generate path parameter substitution code."""
        if not path_params:
            return ''
        
        code = '\n'
        for param in path_params:
            code += f'''        {param} = module.params.get('{param}')
        endpoint = endpoint.replace('{{{{ {param} }}}}', str({param}))
'''
        return code

    def _generate_data_preparation(self, params: Dict, path_params: List[str]) -> str:
        """Generate data dictionary preparation code."""
        code = '''
        data = {}
'''
        for name in params.keys():
            if name not in path_params:
                code += f'''        if module.params.get('{name}') is not None:
            data['{name}'] = module.params['{name}']
'''
        return code

    def write_module(self, module_name: str, code: str):
        """Write module to file."""
        module_file = self.output_dir / f"{module_name}.py"
        with open(module_file, 'w', encoding='utf-8') as f:
            f.write(code)

