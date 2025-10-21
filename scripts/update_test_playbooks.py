#!/usr/bin/env python3
"""
Update test playbooks to use session-based authentication.
This script adds auth_session module usage to playbooks that use direct username/password auth.
"""

import re
from pathlib import Path
import yaml


def should_add_session(content: str) -> bool:
    """Check if playbook needs session auth added."""
    # Already has auth_session
    if 'auth_session:' in content:
        return False
    # Has direct username/password auth
    if 'username: "{{ cribl_username }}"' in content and 'password: "{{ cribl_password }}"' in content:
        return True
    return False


def add_session_task(content: str) -> str:
    """Add session creation task after vars section."""
    
    # Find the tasks: section
    tasks_pattern = r'(  tasks:\n)'
    
    session_task = '''  tasks:
    - name: Create Cribl authentication session
      cribl.core.auth_session:
        base_url: "{{ cribl_url }}"
        username: "{{ cribl_username }}"
        password: "{{ cribl_password }}"
        validate_certs: false
      register: cribl_session
      no_log: true

'''
    
    # Replace tasks: with session creation task
    if re.search(tasks_pattern, content):
        content = re.sub(tasks_pattern, session_task, content, count=1)
    
    return content


def replace_auth_params(content: str) -> str:
    """Replace username/password/base_url params with session."""
    
    # Pattern to match module calls with auth parameters
    pattern = r'''(      cribl\.[^:]+:)\n        base_url: "{{ cribl_url }}"\n        username: "{{ cribl_username }}"\n        password: "{{ cribl_password }}"\n        validate_certs: false\n'''
    
    replacement = r'\1\n        session: "{{ cribl_session.session }}"\n'
    
    content = re.sub(pattern, replacement, content)
    
    return content


def update_playbook(file_path: Path):
    """Update a single playbook file."""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    if should_add_session(content):
        # Add session creation task
        content = add_session_task(content)
        
        # Replace all auth parameters with session
        content = replace_auth_params(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Updated {file_path}")
        else:
            print(f"  [-] No changes needed for {file_path}")
    else:
        print(f"  [-] Skipping {file_path} (already has session or no direct auth)")


def main():
    """Update all test playbooks."""
    test_dir = Path('tests/docker/playbooks')
    
    if not test_dir.exists():
        print(f"Error: {test_dir} does not exist")
        return
    
    playbooks = list(test_dir.glob('*.yml'))
    
    print(f"Found {len(playbooks)} playbooks to process\n")
    
    for playbook in playbooks:
        try:
            update_playbook(playbook)
        except Exception as e:
            print(f"  [ERROR] Error processing {playbook}: {e}")
    
    print("\nDone!")


if __name__ == '__main__':
    main()

