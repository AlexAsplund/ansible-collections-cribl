# Module Generator Scripts

This directory contains the module generation system for Cribl Ansible Collections.

## Quick Start

```bash
# Generate all modules (using config file)
python scripts/generate_modules.py

# Or specify a schema file directly
python scripts/generate_modules.py --schema schemas/cribl-apidocs-4.14.0-837595d5.yml

# Configuration is in scripts/generator_config.yml
# Default: Always clean, always generate declarative + imperative modules
```

## Configuration

The generator is configured via `generator_config.yml`:

```yaml
spec_file: schemas/cribl-apidocs-4.14.0-837595d5.yml  # OpenAPI spec
output_dir: build/ansible_collections/cribl            # Output directory
products: null                                         # null = all, or ['core', 'stream']
clean: true                                            # Clean before generation
generate_declarative: true                             # Generate declarative modules
generate_imperative: true                              # Generate imperative modules
```

**Note:** Version is automatically detected from the OpenAPI schema's `info.version` field. 
Any `-<hex>` suffix is automatically stripped (e.g., `4.14.0-837595d5` becomes `4.14.0`).

## Documentation

For complete generator documentation, see:
- **[Generator Guide](../docs/GENERATOR.md)** - Complete usage guide
- **[Examples](../docs/EXAMPLES.md)** - Usage examples

## Structure

```
scripts/
├── generate_modules.py          # CLI entry point
└── generator/                   # Modular generator package
    ├── __init__.py              # Package initialization
    ├── openapi_parser.py        # OpenAPI specification parser
    ├── module_generator.py      # Imperative module generator
    ├── declarative_generator.py # Declarative module generator
    ├── collection_manager.py    # Collection structure manager
    └── templates.py             # Module code templates
```

## Requirements

- Python 3.6+
- PyYAML
- Jinja2 (optional, for advanced templating)

Install dependencies:
```bash
pip install -r ../requirements-dev.txt
```

## Usage

The generator runs using the configuration in `generator_config.yml`:

```bash
# Generate all modules (from project root)
python scripts/generate_modules.py

# Or specify a schema file directly
python scripts/generate_modules.py --schema schemas/cribl-apidocs-4.14.0-837595d5.yml

# Or from scripts directory
cd scripts
python generate_modules.py
```

To customize behavior, edit `scripts/generator_config.yml`:

```yaml
# Generate only core collection
products: ['core']

# Skip imperative modules
generate_imperative: false

# Don't clean before generation
clean: false
```

## Output

Generated modules are placed in:
```
../build/ansible_collections/cribl/
├── core/      # 276 modules
├── stream/    # 127 modules  
├── edge/      # 19 modules
├── search/    # 80 modules
└── lake/      # 11 modules
```

## Development

To modify the generator:

1. Edit files in `generator/` package
2. Update templates in `generator/templates.py`
3. Test changes: `pytest ../tests/unit/test_generator.py`
4. Regenerate modules to verify

## Support

For issues or questions:
- See [Contributing Guide](../CONTRIBUTING.md)
- Check [Generator Documentation](../docs/GENERATOR.md)
- Open an issue on GitHub

