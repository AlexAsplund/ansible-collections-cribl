#!/usr/bin/env python3
"""Update documentation to use new module names and session auth."""

from pathlib import Path
import sys


def update_file(file_path: Path):
    """Update a single file with new module names."""
    try:
        print(f"Processing {file_path}...")
        content = file_path.read_text(encoding='utf-8')
        
        # Replace module names
        original_content = content
        content = content.replace('cribl.core.cribl_', 'cribl.core.')
        content = content.replace('cribl.stream.cribl_', 'cribl.stream.')
        content = content.replace('cribl.edge.cribl_', 'cribl.edge.')
        content = content.replace('cribl.search.cribl_', 'cribl.search.')
        content = content.replace('cribl.lake.cribl_', 'cribl.lake.')
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"  [OK] Updated {file_path}")
            return True
        else:
            print(f"  [-] No changes for {file_path}")
            return False
    except Exception as e:
        print(f"  [ERROR] Failed to update {file_path}: {e}")
        return False


def main():
    """Update all documentation files."""
    docs = [
        Path('docs/EXAMPLES.md'),
        Path('docs/API_REFERENCE.md'),
        Path('docs/DECLARATIVE.md'),
        Path('docs/GENERATOR.md'),
    ]
    
    updated = 0
    for doc in docs:
        if doc.exists():
            if update_file(doc):
                updated += 1
        else:
            print(f"[SKIP] {doc} does not exist")
    
    print(f"\n[DONE] Updated {updated} files")


if __name__ == '__main__':
    main()

