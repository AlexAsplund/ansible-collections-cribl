# Cribl Ansible Collections

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ansible](https://img.shields.io/badge/Ansible-2.9%2B-blue.svg)](https://www.ansible.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## 📦 Latest Release

**Current Version**: `v4.20.0` | **Released**:  | [Download](https://github.com/AlexAsplund/ansible-collections-cribl/releases/tag/v4.20.0)

Generated from [Cribl API Spec 4.20.0](https://cdn.cribl.io/dl/4.20.0/cribl-apidocs-4.20.0-cee79842.yml)

---
## Project Structure

```
.
├── scripts/
│   ├── generate_modules.py              # CLI entry point
│   └── generator/                       # Modular generator
│       ├── openapi_parser.py            # Parse OpenAPI specs
│       ├── module_generator.py          # Generate imperative modules
│       ├── declarative_generator.py     # Generate declarative modules
│       ├── collection_manager.py        # Manage collection structure
│       └── templates.py                 # Code templates
├── schemas/
│   └── cribl-apidocs-4.15.0.yml        # OpenAPI specification
├── build/
│   └── ansible_collections/cribl/       # Generated collections
│       ├── core/                        # 276 modules
│       ├── stream/                      # 127 modules
│       ├── edge/                        # 19 modules
│       ├── search/                      # 80 modules
│       └── lake/                        # 11 modules
├── docs/                                # Documentation
├── tests/                               # Test suite
│   ├── docker/                          # Docker integration tests
│   ├── unit/                            # Unit tests
│   └── integration/                     # Integration tests
├── Makefile                             # Development commands
└── README.md                            # This file
```

---

## Requirements

- **Python**: 3.6 or higher
- **Ansible**: 2.9 or higher
- **PyYAML**: For OpenAPI parsing
- **Docker**: For integration tests (optional)
- **Cribl Instance**: Stream, Edge, Search, or Lake

---

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines
- Testing requirements
- Pull request process
- Development setup

---

## Support

- **Documentation**: [Cribl Docs](https://docs.cribl.io)
- **API Reference**: [Cribl API](https://docs.cribl.io/cribl-as-code/api-reference/)
- **Issues**: [GitHub Issues](https://github.com/AlexAsplund/ansible-collections-cribl/issues)
- **Cribl Community**: [Slack](https://cribl.io/community)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Roadmap

- [X] 513 imperative modules (all Cribl API endpoints)
- [X] **Automatic CRUD detection and declarative module generation**
- [X] 49 auto-generated declarative modules across all collections
- [X] Auto-generated unit tests and integration playbooks
- [X] Docker integration testing
- [X] Check mode and diff support
- [X] Cribl Cloud Support
- [X] Smart declarative functions targeting worker groups

---

## Acknowledgments

- Built for the [Cribl Community](https://cribl.io/community)
- Uses [Cribl&#39;s OpenAPI Specification](https://docs.cribl.io)
- Inspired by Infrastructure as Code best practices
