"""
Declarative Module Generator

Generates declarative, idempotent Ansible modules for common resources.
"""

from pathlib import Path
from typing import Dict, List, Optional
from .templates import DeclarativeTemplate, ExampleTemplate


class DeclarativeGenerator:
    """Generate declarative Ansible modules."""

    def __init__(self, base_output_dir: Path, parser=None):
        self.base_output_dir = base_output_dir
        self.template = DeclarativeTemplate()
        self.example_template = ExampleTemplate()
        self.parser = parser
        self.detected_resources = None

    def detect_and_generate(self, products: List[str] = None):
        """
        Auto-detect resources with CRUD operations and generate declarative modules.
        """
        if not self.parser:
            print("  [WARNING] No parser provided, skipping auto-detection")
            return []
        
        if products is None:
            products = ['core', 'stream', 'edge', 'search', 'lake']
        
        # Detect resources
        from .crud_detector import CRUDDetector
        detector = CRUDDetector(self.parser)
        self.detected_resources = detector.detect_resources()
        
        generated = []
        
        for product in products:
            if product not in self.detected_resources:
                continue
            
            resources = self.detected_resources[product]
            if not resources:
                continue
            
            print(f"\n  [{product.upper()}] Detected {len(resources)} resources with CRUD operations")
            
            modules_dir = self.base_output_dir / product / 'plugins' / 'modules'
            modules_dir.mkdir(parents=True, exist_ok=True)
            
            for resource in resources:
                # Use clean resource name for declarative modules (e.g., "user.py", "pipeline.py")
                module_name = resource['resource_name']
                module_file = modules_dir / f"{module_name}.py"
                
                # Get parameters from resource schema
                params = detector.get_resource_params(resource)
                extra_params_doc = detector.format_params_for_module(params)
                
                # Format params for argument_spec
                extra_params_spec = detector.format_params_for_argspec(params)
                
                # Determine update method (PATCH or PUT)
                update_method = resource.get('update_method', 'PATCH')
                
                code = self.template.create_resource_module(
                    resource_name=resource['resource_name'],
                    resource_name_title=resource['resource_title'],
                    product=product,
                    endpoint_base=resource['base_path'],
                    id_param=resource['id_param'],
                    extra_params_doc=extra_params_doc,
                    extra_params_spec=extra_params_spec,
                    update_method=update_method
                )
                
                with open(module_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                generated.append({
                    'product': product,
                    'module_name': module_name,
                    'resource': resource
                })
                print(f"    [OK] {module_name}")
        
        return generated
    
    def generate_all(self, products: List[str] = None):
        """Generate all declarative modules (wrapper for backward compatibility)."""
        generated = self.detect_and_generate(products)
        self.generate_examples(generated)
        return generated
    
    def generate_examples(self, generated_modules: List[Dict]):
        """Generate example playbooks for declarative modules."""
        if not generated_modules:
            return
        
        print("\nGenerating examples...")
        
        # Group by product
        by_product = {}
        for item in generated_modules:
            product = item['product']
            if product not in by_product:
                by_product[product] = []
            by_product[product].append(item)
        
        for product, modules in by_product.items():
            examples_dir = self.base_output_dir / product / 'examples'
            examples_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate individual examples
            for item in modules:
                module_name = item['module_name']
                resource = item['resource']
                
                example_content = self._generate_example_playbook(
                    product=product,
                    module_name=module_name,
                    resource=resource
                )
                
                example_file = examples_dir / f"{module_name}_example.yml"
                with open(example_file, 'w', encoding='utf-8') as f:
                    f.write(example_content)
            
            # Generate combined example
            combined_example = self._generate_combined_example(product, modules)
            combined_file = examples_dir / f"declarative_resources.yml"
            with open(combined_file, 'w', encoding='utf-8') as f:
                f.write(combined_example)
            
            print(f"    [EXAMPLES] Generated {len(modules) + 1} examples for {product}")
    
    def _generate_example_playbook(self, product: str, module_name: str, resource: Dict) -> str:
        """Generate an example playbook for a single module."""
        resource_title = resource['resource_title']
        id_param = resource['id_param']
        
        return self.example_template.single_module_example(
            product, module_name, resource_title, id_param
        )
    
    def _generate_combined_example(self, product: str, modules: List[Dict]) -> str:
        """Generate a combined example showing multiple resources."""
        # Start with header
        combined = self.example_template.combined_example_header(product)
        
        # Add tasks for first 5 modules
        for item in modules[:5]:
            module_name = item['module_name']
            resource = item['resource']
            id_param = resource['id_param']
            
            combined += self.example_template.combined_example_task(
                product, module_name, id_param
            )
        
        # Add footer with remaining modules
        remaining = [m['module_name'] for m in modules[5:]]
        combined += self.example_template.combined_example_footer(remaining)
        
        return combined

    def copy_base_classes(self, products: List[str] = None):
        """Copy declarative base classes to all collections."""
        if products is None:
            products = ['core', 'stream', 'edge', 'search', 'lake']
        
        # Find source file - prefer the canonical version in resources/
        possible_sources = [
            Path('resources/module_utils/cribl_declarative.py'),
            self.base_output_dir / 'stream' / 'plugins' / 'module_utils' / 'cribl_declarative.py',
            self.base_output_dir / 'core' / 'plugins' / 'module_utils' / 'cribl_declarative.py',
        ]
        
        source_file = None
        for src in possible_sources:
            if src.exists():
                source_file = src
                break
        
        # Create from template if no source found
        if not source_file:
            print("  [WARNING] No source file found, creating minimal template")
            temp_file = self.base_output_dir / 'core' / 'plugins' / 'module_utils' / 'cribl_declarative.py'
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            self._create_base_classes(temp_file)
            source_file = temp_file
        
        # Copy to all collections
        import shutil
        for product in products:
            target_dir = self.base_output_dir / product / 'plugins' / 'module_utils'
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / 'cribl_declarative.py'
            
            # Copy if it doesn't exist or is different from source
            if not target_file.exists() or target_file.resolve() != source_file.resolve():
                shutil.copy(source_file, target_file)
                print(f"  [COPY] Copied declarative base classes to {product}")

    def _create_base_classes(self, target_file: Path):
        """Create the cribl_declarative.py base classes."""
        # Read from the template in the repo if available
        template_file = Path('resources/module_utils/cribl_declarative.py')
        if template_file.exists():
            import shutil
            shutil.copy(template_file, target_file)
        else:
            # Create a minimal version
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('''# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# Declarative base classes for Cribl Ansible modules
# See: resources/module_utils/cribl_declarative.py

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Placeholder - copy the full implementation from the source repository
''')

