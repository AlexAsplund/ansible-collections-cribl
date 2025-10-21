#!/usr/bin/env python3
"""
Cribl Ansible Module Generator

Generates Ansible collections from Cribl OpenAPI specification.
Supports both imperative (API-mapped) and declarative (idempotent) modules.

Configuration is loaded from scripts/generator_config.yml

Usage:
    python scripts/generate_modules.py [--schema PATH_TO_SCHEMA]
"""

import sys
import yaml
import re
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generator import (
    OpenAPIParser,
    ModuleGenerator,
    DeclarativeGenerator,
    CollectionManager,
    DeclarativeTestGenerator
)


class CriblModuleGenerator:
    """Main generator orchestrator."""

    def __init__(self, spec_file: str, output_dir: str):
        self.parser = OpenAPIParser(spec_file)
        self.output_dir = Path(output_dir)
        self.collection_manager = CollectionManager(self.output_dir)
        self.stats = {
            'core': [],
            'stream': [],
            'edge': [],
            'search': [],
            'lake': []
        }

    def generate_imperative_modules(self, filter_product: str = None):
        """Generate imperative (API-mapped) modules."""
        self.parser.load()
        endpoints = self.parser.get_endpoints()
        
        print(f"\n{'='*70}")
        print(f"Generating Imperative Modules from {len(endpoints)} endpoints")
        print(f"{'='*70}\n")
        
        generated_count = 0
        skipped_count = 0
        
        for endpoint, methods in endpoints.items():
            product = self.parser.categorize_endpoint(endpoint)
            
            # Filter by product if specified
            if filter_product and product != filter_product:
                continue
            
            # Ensure collection structure exists
            version = getattr(self, 'version', '1.0.0')
            self.collection_manager.create_structure(product, version)
            self.collection_manager.copy_api_client(product)
            self.collection_manager.copy_auth_session_module(product)
            
            # Generate module for each HTTP method
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    continue
                
                if not self.parser.should_generate(endpoint, method, operation):
                    skipped_count += 1
                    continue
                
                generator = ModuleGenerator(
                    self.output_dir / product / 'plugins' / 'modules',
                    product
                )
                
                module_name = generator.sanitize_name(f"{endpoint}_{method}")
                summary, description = self.parser.get_operation_info(operation)
                params = self.parser.extract_parameters(operation, endpoint)
                
                print(f"  [{product.upper():6}] {module_name:<50} {method.upper():6} {endpoint}")
                
                try:
                    code = generator.generate(
                        module_name, endpoint, method, operation,
                        params, summary, description
                    )
                    generator.write_module(module_name, code)
                    self.stats[product].append(module_name)
                    generated_count += 1
                    
                except Exception as e:
                    print(f"    ERROR: {e}")
        
        self._print_summary(generated_count, skipped_count)
        return generated_count

    def generate_declarative_modules(self, filter_product: str = None):
        """Generate declarative (idempotent) modules."""
        print(f"\n{'='*70}")
        print("Auto-Detecting CRUD Resources & Generating Declarative Modules")
        print(f"{'='*70}\n")
        
        # Ensure spec is loaded
        if self.parser.spec is None:
            self.parser.load()
        
        products = [filter_product] if filter_product else None
        generator = DeclarativeGenerator(self.output_dir, parser=self.parser)
        
        # Generate modules (auto-detects CRUD resources)
        modules = generator.generate_all(products)
        
        # Copy base classes
        generator.copy_base_classes(products)
        
        # Generate tests
        if modules:
            print(f"\nGenerating tests for declarative modules...")
            test_generator = DeclarativeTestGenerator(Path('tests/unit'))
            test_generator.generate_tests(modules)
            
            # Generate integration playbook
            test_generator.generate_integration_playbook(
                modules,
                Path('tests/integration/test_all_declarative.yml')
            )
        
        print(f"\n{'='*70}")
        print(f"[+] Generated {len(modules)} declarative modules")
        print(f"{'='*70}\n")
        return len(modules)

    def generate_indexes(self):
        """Generate module index files."""
        for product, modules in self.stats.items():
            if modules:
                self.collection_manager.generate_module_index(product, modules)

    def clean(self, filter_product: str = None):
        """Clean generated modules."""
        products = [filter_product] if filter_product else ['core', 'stream', 'edge', 'search', 'lake']
        
        for product in products:
            print(f"Cleaning {product}...")
            self.collection_manager.clean_generated_modules(product)

    def _print_summary(self, generated: int, skipped: int):
        """Print generation summary."""
        print(f"\n{'='*70}")
        print(f"Summary: Generated {generated} modules, Skipped {skipped} endpoints")
        print(f"{'='*70}\n")
        
        for product, modules in sorted(self.stats.items()):
            if modules:
                print(f"  {product.title():8}: {len(modules):3} modules")


def extract_version_from_schema(schema_path: str) -> str:
    """
    Extract version from OpenAPI schema file.
    Strips the -<hex> suffix if present.
    
    Args:
        schema_path: Path to the OpenAPI schema file
        
    Returns:
        Version string (e.g., '4.14.0')
    """
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = yaml.safe_load(f)
        
        version = schema.get('info', {}).get('version', '1.0.0')
        
        # Strip the -<hex> suffix if present (e.g., '4.14.0-837595d5' -> '4.14.0')
        version = re.sub(r'-[a-f0-9]+$', '', version)
        
        return version
    except Exception as e:
        print(f"WARNING: Could not extract version from schema: {e}")
        print("Falling back to default version 1.0.0")
        return '1.0.0'


def load_config(schema_override: str = None):
    """
    Load configuration from generator_config.yml
    
    Args:
        schema_override: If provided, use this schema path instead of config file
    """
    config_path = Path(__file__).parent / 'generator_config.yml'
    
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Resolve paths relative to project root (parent of scripts/)
    project_root = Path(__file__).parent.parent
    
    # Override schema if provided
    if schema_override:
        config['spec_file'] = schema_override
    
    if 'spec_file' in config and config['spec_file']:
        # Only resolve relative paths
        spec_path = Path(config['spec_file'])
        if not spec_path.is_absolute():
            config['spec_file'] = str(project_root / config['spec_file'])
    
    if 'output_dir' in config and config['output_dir']:
        config['output_dir'] = str(project_root / config['output_dir'])
    
    # Extract version from schema (overrides config version if present)
    if 'spec_file' in config and config['spec_file']:
        config['version'] = extract_version_from_schema(config['spec_file'])
    
    return config


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Generate Ansible modules from Cribl OpenAPI specification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scripts/generate_modules.py
  python scripts/generate_modules.py --schema schemas/cribl-apidocs-4.14.0-837595d5.yml
        '''
    )
    parser.add_argument(
        '--schema',
        type=str,
        help='Path to OpenAPI schema file (overrides generator_config.yml)'
    )
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(schema_override=args.schema)
    
    spec_file = config.get('spec_file', 'schemas/cribl-apidocs-4.14.0-837595d5.yml')
    version = config.get('version', '1.0.0')
    output_dir = config.get('output_dir', 'build/ansible_collections/cribl')
    product_filter = config.get('products')
    clean = config.get('clean', True)
    generate_declarative = config.get('generate_declarative', True)
    generate_imperative = config.get('generate_imperative', True)
    
    print(f"\n{'='*70}")
    print("Cribl Ansible Module Generator")
    print(f"{'='*70}")
    print(f"Config:  {Path(__file__).parent / 'generator_config.yml'}")
    print(f"Schema:  {spec_file}")
    print(f"Version: {version} (detected from schema)")
    print(f"Output:  {output_dir}")
    print(f"Clean:   {clean}")
    print(f"{'='*70}\n")
    
    # Create generator
    generator = CriblModuleGenerator(spec_file, output_dir)
    generator.version = version  # Store version for use in collection creation
    
    # Ensure build directory exists
    Path(output_dir).parent.mkdir(parents=True, exist_ok=True)
    
    # Clean if requested
    if clean:
        print("Cleaning existing modules...")
        generator.clean(product_filter)
    
    # Generate imperative modules
    if generate_imperative:
        count = generator.generate_imperative_modules(product_filter)
        
        # Generate indexes
        if count > 0:
            generator.generate_indexes()
    
    # Generate declarative modules
    if generate_declarative:
        generator.generate_declarative_modules(product_filter)
    
    print("\n[SUCCESS] Generation complete!\n")


if __name__ == '__main__':
    main()

