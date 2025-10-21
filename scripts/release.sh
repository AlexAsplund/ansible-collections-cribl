#!/bin/bash
#
# Release script for Cribl Ansible Collections
#
# Usage:
#   ./scripts/release.sh 1.0.0          # Create release locally
#   ./scripts/release.sh 1.0.0 --push   # Create and push tag to GitHub
#

set -e

VERSION=$1
PUSH_TAG=${2:-}

if [ -z "$VERSION" ]; then
    echo "Error: Version not specified"
    echo "Usage: $0 <version> [--push]"
    echo "Example: $0 1.0.0"
    exit 1
fi

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?(-[a-z0-9]+)?$ ]]; then
    echo "Error: Invalid version format '$VERSION'"
    echo "Expected format: X.Y.Z (e.g., 1.0.0)"
    echo "or X.Y.Z-<suffix> (e.g., 1.0.0-alpha1)"
    exit 1
fi

echo "=========================================="
echo "Creating release for version $VERSION"
echo "=========================================="
echo ""

# Check if we're in the project root
if [ ! -f "scripts/generate_modules.py" ]; then
    echo "Error: Must be run from project root"
    exit 1
fi

# Check for uncommitted changes
if [ "$PUSH_TAG" = "--push" ]; then
    if ! git diff-index --quiet HEAD --; then
        echo "Error: You have uncommitted changes. Commit or stash them first."
        git status --short
        exit 1
    fi
fi

echo "Step 1: Updating version in config files..."
python scripts/update_version.py "$VERSION"
echo ""

echo "Step 2: Generating modules..."
python scripts/generate_modules.py
echo ""

echo "Step 3: Building collection tarballs..."
mkdir -p dist
for collection in core stream edge search lake; do
    if [ -d "build/ansible_collections/cribl/$collection" ]; then
        echo "  Building cribl.$collection..."
        cd build/ansible_collections/cribl/$collection
        ansible-galaxy collection build --output-path ../../../../dist --force
        cd ../../../../
    fi
done
echo ""

echo "Step 4: Verifying built collections..."
echo "Tarballs in dist/:"
ls -lh dist/cribl-*-${VERSION}.tar.gz 2>/dev/null || {
    echo "Error: No tarballs found with version $VERSION"
    echo "Found:"
    ls -lh dist/*.tar.gz 2>/dev/null || echo "  (none)"
    exit 1
}
echo ""

echo "=========================================="
echo "✓ Release build complete!"
echo "=========================================="
echo ""
echo "Version: $VERSION"
echo "Tarballs: dist/"
echo ""

if [ "$PUSH_TAG" = "--push" ]; then
    echo "Creating and pushing git tag..."
    
    # Create annotated tag
    git tag -a "v${VERSION}" -m "Release version ${VERSION}"
    
    echo "Pushing tag to GitHub..."
    git push origin "v${VERSION}"
    
    echo ""
    echo "=========================================="
    echo "✓ Tag pushed to GitHub!"
    echo "=========================================="
    echo ""
    echo "GitHub Actions will now:"
    echo "  1. Build the collections"
    echo "  2. Create a GitHub Release"
    echo "  3. Upload tarballs as release assets"
    echo ""
    echo "Monitor progress at:"
    echo "  https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
    echo ""
else
    echo "=========================================="
    echo "Next steps:"
    echo "=========================================="
    echo ""
    echo "To create a GitHub release:"
    echo "  1. Review the built tarballs in dist/"
    echo "  2. Test installation: make install-collections"
    echo "  3. Run: $0 $VERSION --push"
    echo ""
    echo "Or manually:"
    echo "  git tag -a v${VERSION} -m 'Release version ${VERSION}'"
    echo "  git push origin v${VERSION}"
    echo ""
    echo "Or trigger workflow manually:"
    echo "  gh workflow run build-release.yml -f version=${VERSION}"
    echo ""
fi

