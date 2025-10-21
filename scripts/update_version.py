#!/usr/bin/env python3
"""
Update version in all galaxy.yml files.

Note: Version is automatically detected from the OpenAPI schema.
This script is used for release management to update galaxy.yml files
after modules have been generated.

Usage:
    python scripts/update_version.py 1.0.0
"""

import sys
import re
from pathlib import Path


def update_galaxy_version(galaxy_file: Path, new_version: str) -> bool:
    """Update version in a galaxy.yml file."""
    if not galaxy_file.exists():
        print(f"  ⚠️  File not found: {galaxy_file}")
        return False
    
    content = galaxy_file.read_text(encoding='utf-8')
    
    # Replace version line
    new_content = re.sub(
        r'^version:\s*[0-9]+\.[0-9]+\.[0-9]+.*$',
        f'version: {new_version}',
        content,
        flags=re.MULTILINE
    )
    
    if content != new_content:
        galaxy_file.write_text(new_content, encoding='utf-8')
        print(f"  ✓ Updated: {galaxy_file.relative_to(Path.cwd())}")
        return True
    else:
        print(f"  ℹ️  No change: {galaxy_file.relative_to(Path.cwd())}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_version.py <version>")
        print("Example: python scripts/update_version.py 1.0.0")
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+(-[a-z0-9]+)?$', new_version):
        print(f"Error: Invalid version format '{new_version}'")
        print("Expected format: X.Y.Z (e.g., 1.0.0)")
        print("or X.Y.Z-<suffix> (e.g., 1.0.0-alpha1)")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Updating galaxy.yml version to: {new_version}")
    print(f"{'='*60}\n")
    print("Note: Version is auto-detected from OpenAPI schema during generation.")
    print("This script updates galaxy.yml files for release management.\n")
    
    project_root = Path(__file__).parent.parent
    updated_count = 0
    
    # Update galaxy.yml files in build directory
    print("Updating galaxy.yml files in build/:")
    build_dir = project_root / 'build' / 'ansible_collections' / 'cribl'
    
    if build_dir.exists():
        for collection_dir in build_dir.iterdir():
            if collection_dir.is_dir():
                galaxy_file = collection_dir / 'galaxy.yml'
                if update_galaxy_version(galaxy_file, new_version):
                    updated_count += 1
    else:
        print("  ⚠️  Build directory not found. Run 'make generate' first.")
    
    print(f"\n{'='*60}")
    if updated_count > 0:
        print(f"✓ Updated {updated_count} galaxy.yml file(s) to version {new_version}")
    else:
        print("ℹ️  No files were updated")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()

