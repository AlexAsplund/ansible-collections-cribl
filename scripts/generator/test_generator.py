"""
Test Generator for Declarative Modules

Generates pytest tests for declarative Ansible modules.
"""

from pathlib import Path
from typing import Dict, List
from .templates import TestTemplate


class DeclarativeTestGenerator:
    """Generate tests for declarative Ansible modules."""
    
    def __init__(self, base_test_dir: Path):
        self.base_test_dir = base_test_dir
        self.base_test_dir.mkdir(parents=True, exist_ok=True)
        self.template = TestTemplate()
    
    def _clear_old_tests(self):
        """Clear old generated test files."""
        import glob
        pattern = str(self.base_test_dir / "test_*_declarative.py")
        for test_file in glob.glob(pattern):
            try:
                Path(test_file).unlink()
                print(f"    [CLEANUP] Removed old test file: {Path(test_file).name}")
            except Exception as e:
                print(f"    [WARNING] Could not remove {Path(test_file).name}: {e}")
    
    def generate_tests(self, generated_modules: List[Dict]):
        """
        Generate tests for all generated declarative modules.
        
        Args:
            generated_modules: List of dicts with module info from DeclarativeGenerator
        """
        if not generated_modules:
            return
        
        # Clear old test files first
        self._clear_old_tests()
        
        # Group by product
        by_product = {}
        for module_info in generated_modules:
            product = module_info['product']
            if product not in by_product:
                by_product[product] = []
            by_product[product].append(module_info)
        
        # Generate test file for each product
        for product, modules in by_product.items():
            self._generate_product_tests(product, modules)
    
    def _generate_product_tests(self, product: str, modules: List[Dict]):
        """Generate test file for a product's declarative modules."""
        test_file = self.base_test_dir / f"test_{product}_declarative.py"
        
        # Generate test content
        content = self._test_file_header(product)
        
        for module_info in modules:
            content += self._generate_module_test(module_info)
        
        # Write test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"    [TEST] Generated tests for {product}: {test_file.name}")
    
    def _test_file_header(self, product: str) -> str:
        """Generate test file header."""
        return self.template.test_file_header(product)
    
    def _generate_module_test(self, module_info: Dict) -> str:
        """Generate test methods for a single module."""
        module_name = module_info['module_name']
        resource = module_info['resource']
        resource_name = resource['resource_name']
        id_param = resource['id_param']
        # Sanitize resource name for use in Python function names
        sanitized_name = resource_name.replace('-', '_')
        
        return self.template.module_test(resource_name, id_param, sanitized_name)
    
    def generate_integration_playbook(self, generated_modules: List[Dict], output_file: Path):
        """Generate integration test playbook for all declarative modules."""
        # Group by product
        by_product = {}
        for module_info in generated_modules:
            product = module_info['product']
            if product not in by_product:
                by_product[product] = []
            by_product[product].append(module_info)
        
        # Generate playbook
        playbook = self.template.integration_playbook_header()
        
        for product, modules in sorted(by_product.items()):
            playbook += f'\n    # {product.upper()} Declarative Modules\n'
            
            # Add auth_session creation for this product
            playbook += self.template.integration_playbook_auth_session(product)
            
            for module_info in modules:
                module_name = module_info['module_name']
                resource = module_info['resource']
                id_param = resource['id_param']
                resource_name = resource['resource_name']
                
                playbook += self.template.integration_playbook_module_test(
                    product, module_name, id_param, resource_name
                )
        
        # Write playbook
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(playbook)
        
        print(f"    [TEST] Generated integration playbook: {output_file.name}")


