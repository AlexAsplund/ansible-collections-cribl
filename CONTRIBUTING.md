# Contributing to Cribl Ansible Collections

Thank you for your interest in contributing! This document provides guidelines for contributing to the Cribl Ansible Collections project.

## Ways to Contribute

- Report bugs
- Suggest features or enhancements
- Improve documentation
- Submit pull requests

## Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ansible-cribl-collection.git
   cd ansible-cribl-collection
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.6+
- Ansible 2.9+
- PyYAML (`pip install pyyaml`)

### Generating Modules

```bash
# Generate all collections
python generate_modules.py --clean

# Generate specific collection
python generate_modules.py --product core --clean
```

### Testing Your Changes

```bash
# Syntax check
python -m py_compile ansible_collections/cribl/*/plugins/modules/*.py

# Build collection
cd ansible_collections/cribl/core
ansible-galaxy collection build

# Test playbooks
ansible-playbook examples/authentication.yml --check
```

## Coding Standards

### Python Code

- Follow PEP 8 style guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Ansible Playbooks

- Use meaningful task names
- Include comments for complex logic
- Follow Ansible best practices
- Test with `--check` mode

### Module Documentation

All generated modules include:
- `DOCUMENTATION` - Module parameters and options
- `EXAMPLES` - Usage examples
- `RETURN` - Return value documentation

## Pull Request Process

1. **Update documentation** if needed
2. **Test your changes** thoroughly
3. **Update examples** if adding new features
4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** with:
   - Clear description of changes
   - Why the change is needed
   - How it was tested
   - Any breaking changes

## Reporting Bugs

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: How to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**:
  - Python version
  - Ansible version
  - Cribl version
  - OS

## Suggesting Features

For feature requests, please include:

- **Use case**: Why is this feature needed?
- **Description**: What should the feature do?
- **Examples**: How would it be used?

## Code Review Process

- Maintainers will review pull requests
- Feedback will be provided for improvements
- Once approved, changes will be merged

## Questions?

- Open an issue for questions
- Check existing issues and PRs first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing!