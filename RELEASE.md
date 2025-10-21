# Release Guide

This guide explains how to create and publish releases of the Cribl Ansible Collections to GitHub.

## Quick Release

```bash
# Linux/Mac
./scripts/release.sh 1.0.0 --push

# Windows
.\scripts\release.ps1 -Version 1.0.0 -Push
```

This will:
1. Update version in all files
2. Generate modules
3. Build collection tarballs
4. Create and push git tag to GitHub
5. Trigger GitHub Actions to create a release

## Table of Contents

- [Prerequisites](#prerequisites)
- [Release Process](#release-process)
- [Versioning](#versioning)
- [Automated Release (GitHub Actions)](#automated-release-github-actions)
- [Manual Release](#manual-release)
- [Publishing to Ansible Galaxy](#publishing-to-ansible-galaxy)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- Python 3.6+
- Ansible Core (for `ansible-galaxy` command)
- Git
- GitHub CLI (`gh`) - optional but recommended

```bash
# Install Ansible
pip install ansible-core

# Install GitHub CLI (optional)
# Mac: brew install gh
# Windows: winget install GitHub.cli
# Linux: https://github.com/cli/cli#installation
```

### Permissions

- Push access to the repository
- Permission to create tags and releases

## Release Process

### Step 1: Prepare for Release

Ensure all changes are committed and tests pass:

```bash
# Run tests
make test

# Check for uncommitted changes
git status

# Commit any outstanding changes
git add .
git commit -m "Prepare for release"
git push
```

### Step 2: Build Locally and Test

Test the build process locally first:

```bash
# Linux/Mac
./scripts/release.sh 1.0.0

# Windows
.\scripts\release.ps1 -Version 1.0.0
```

This creates the tarballs in `dist/` without pushing to GitHub.

### Step 3: Test Installation

Verify the built collections work:

```bash
# Install locally
ansible-galaxy collection install dist/cribl-core-1.0.0.tar.gz --force

# Test a module
ansible-doc cribl.core.user

# Run a test playbook
ansible-playbook examples/session_authentication_example.yml --syntax-check
```

### Step 4: Create Release

Once testing is complete, create the GitHub release:

```bash
# Linux/Mac
./scripts/release.sh 1.0.0 --push

# Windows
.\scripts\release.ps1 -Version 1.0.0 -Push
```

This will:
1. Update version numbers
2. Generate and build collections
3. Create an annotated git tag
4. Push the tag to GitHub
5. Trigger GitHub Actions workflow

### Step 5: Monitor Release

GitHub Actions will automatically:
1. Build the collections again (clean environment)
2. Create a GitHub Release
3. Upload tarballs as release assets
4. Generate release notes

Monitor progress:
```bash
# View workflow runs
gh run list --workflow=build-release.yml

# Watch specific run
gh run watch

# Or visit: https://github.com/your-org/your-repo/actions
```

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Version Update Locations

The `update_version.py` script updates versions in:

1. `scripts/generator_config.yml` - Generator configuration
2. `build/ansible_collections/cribl/*/galaxy.yml` - All collection metadata files

### Manual Version Update

If needed, manually update versions:

```bash
python scripts/update_version.py 1.0.0
```

## Automated Release (GitHub Actions)

### Trigger via Git Tag

Most common method:

```bash
# Create and push tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

GitHub Actions will automatically start the build and release process.

### Trigger via GitHub UI

1. Go to **Actions** tab in GitHub
2. Select **Build and Release Collections** workflow
3. Click **Run workflow**
4. Enter version number (e.g., `1.0.0`)
5. Click **Run workflow**

This creates a **draft release** for you to review before publishing.

### Trigger via GitHub CLI

```bash
gh workflow run build-release.yml -f version=1.0.0
```

## Manual Release

If you need to create a release manually without using the scripts:

### 1. Update Version

```bash
python scripts/update_version.py 1.0.0
```

### 2. Generate Modules

```bash
make generate
# OR
python scripts/generate_modules.py
```

### 3. Build Collections

```bash
make build
# OR manually:
mkdir -p dist
for collection in core stream edge search lake; do
  cd build/ansible_collections/cribl/$collection
  ansible-galaxy collection build --output-path ../../../../dist --force
  cd ../../../../
done
```

### 4. Create GitHub Release

Using GitHub CLI:

```bash
gh release create v1.0.0 \
  dist/*.tar.gz \
  --title "Release v1.0.0" \
  --notes "Release notes here"
```

Or via GitHub web interface:
1. Go to **Releases** → **Draft a new release**
2. Choose tag: `v1.0.0` (create new)
3. Set release title: `Release v1.0.0`
4. Add release notes
5. Upload tarballs from `dist/`
6. Click **Publish release**

## Publishing to Ansible Galaxy

After creating a GitHub release, you can publish to Ansible Galaxy:

### Prerequisites

1. Create an account on [Ansible Galaxy](https://galaxy.ansible.com/)
2. Get your API token from [Galaxy Settings](https://galaxy.ansible.com/me/preferences)

### Publish Collections

```bash
# Set your API token
export ANSIBLE_GALAXY_TOKEN="your-token-here"

# Publish all collections
for tarball in dist/cribl-*.tar.gz; do
  ansible-galaxy collection publish "$tarball"
done

# Or publish individually
ansible-galaxy collection publish dist/cribl-core-1.0.0.tar.gz
ansible-galaxy collection publish dist/cribl-stream-1.0.0.tar.gz
# ... etc
```

### Verify Publication

```bash
# Search on Galaxy
ansible-galaxy collection list cribl.core

# Install from Galaxy
ansible-galaxy collection install cribl.core
```

## Release Checklist

Use this checklist for each release:

- [ ] All tests passing (`make test`)
- [ ] All changes committed and pushed
- [ ] Version number decided (following semver)
- [ ] Local build tested (`./scripts/release.sh X.Y.Z`)
- [ ] Collections installed and verified locally
- [ ] Release notes prepared (or use auto-generated)
- [ ] Tag created and pushed (`./scripts/release.sh X.Y.Z --push`)
- [ ] GitHub Actions workflow completed successfully
- [ ] Release assets uploaded to GitHub
- [ ] Release published (not draft)
- [ ] (Optional) Published to Ansible Galaxy
- [ ] Release announcement made (if applicable)

## Release Assets

Each release includes 5 collection tarballs:

```
cribl-core-X.Y.Z.tar.gz      (~500KB)
cribl-stream-X.Y.Z.tar.gz    (~300KB)
cribl-edge-X.Y.Z.tar.gz      (~100KB)
cribl-search-X.Y.Z.tar.gz    (~200KB)
cribl-lake-X.Y.Z.tar.gz      (~50KB)
```

Users can download and install these directly:

```bash
ansible-galaxy collection install cribl-core-1.0.0.tar.gz
```

## Troubleshooting

### "Version already exists"

If you try to create a tag that already exists:

```bash
# List existing tags
git tag -l

# Delete local tag
git tag -d v1.0.0

# Delete remote tag (careful!)
git push origin :refs/tags/v1.0.0
```

### "GitHub Actions workflow failed"

Check the workflow logs:

```bash
# View recent runs
gh run list --workflow=build-release.yml

# View specific run details
gh run view <run-id>

# View logs
gh run view <run-id> --log
```

Common issues:
- **Module generation failed**: Check OpenAPI spec is valid
- **Build failed**: Ensure `ansible-galaxy` is installed in workflow
- **Upload failed**: Check GitHub token permissions

### "Tarball version mismatch"

If the built tarballs don't have the correct version:

```bash
# Clean everything
make clean

# Update version
python scripts/update_version.py 1.0.0

# Regenerate from scratch
make generate

# Rebuild
make build

# Verify
ls -lh dist/
```

### "Permission denied when pushing tag"

Ensure you have push access to the repository:

```bash
# Check remote
git remote -v

# Test push access
git push --dry-run
```

## Development Releases

For testing releases without affecting production:

### Pre-release Versions

Use pre-release suffixes:

```bash
# Alpha release
./scripts/release.sh 1.0.0-alpha1

# Beta release
./scripts/release.sh 1.0.0-beta1

# Release candidate
./scripts/release.sh 1.0.0-rc1
```

Mark as pre-release in GitHub:
1. Edit the release
2. Check **This is a pre-release**
3. Save

### Draft Releases

Create a draft release to review before publishing:

```bash
# Use manual workflow trigger (creates draft)
gh workflow run build-release.yml -f version=1.0.0

# Or via UI: mark as draft when creating
```

## Rollback

If you need to rollback a release:

### Remove GitHub Release

```bash
# Delete release (keeps tag)
gh release delete v1.0.0

# Or delete both release and tag
gh release delete v1.0.0 --yes
git push origin :refs/tags/v1.0.0
```

### Revert to Previous Version

```bash
# Check out previous tag
git checkout v0.9.0

# Create new release from previous version
./scripts/release.sh 1.0.1 --push
```

## Automation Ideas

Future improvements:

1. **Automated Changelog**: Generate from commit messages
2. **Version Bumping**: Auto-increment versions
3. **Release Schedule**: Automated releases on schedule
4. **Notification**: Slack/Discord notifications on release
5. **Asset Signing**: GPG sign release tarballs

## Related Files

- `.github/workflows/build-release.yml` - GitHub Actions workflow
- `scripts/release.sh` - Linux/Mac release script
- `scripts/release.ps1` - Windows release script
- `scripts/update_version.py` - Version update utility
- `Makefile` - Build commands

## Support

For issues or questions about releasing:

1. Check [GitHub Actions logs](https://github.com/your-org/your-repo/actions)
2. Review [CONTRIBUTING.md](CONTRIBUTING.md)
3. Open an issue with the `release` label

