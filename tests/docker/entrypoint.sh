#!/bin/bash
set -e

echo "🔨 Building Ansible Collections..."

# Change to project root
cd /ansible

# Check if modules are already built
if [ ! -d "build/ansible_collections/cribl/core/plugins/modules" ]; then
    echo "📦 Generating modules from OpenAPI spec..."
    python scripts/generate_modules.py
    
    echo "✅ Modules generated successfully"
else
    echo "✅ Modules already built (skipping generation)"
fi

# Show collection status
echo ""
echo "📚 Available Cribl Collections:"
ls -1 build/ansible_collections/cribl/ 2>/dev/null || echo "  (none - build failed)"

echo ""
echo "✨ Ansible test environment ready!"
echo ""

# Execute the command passed to docker run
exec "$@"

