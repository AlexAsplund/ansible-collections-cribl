"""
Cribl Ansible Module Generator

A modular generator for creating Ansible collections from OpenAPI specifications.
"""

from .openapi_parser import OpenAPIParser
from .module_generator import ModuleGenerator
from .declarative_generator import DeclarativeGenerator
from .collection_manager import CollectionManager
from .crud_detector import CRUDDetector
from .test_generator import DeclarativeTestGenerator

__all__ = [
    'OpenAPIParser',
    'ModuleGenerator',
    'DeclarativeGenerator',
    'CollectionManager',
    'CRUDDetector',
    'DeclarativeTestGenerator',
]

