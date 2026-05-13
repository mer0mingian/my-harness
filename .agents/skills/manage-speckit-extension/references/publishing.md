# Publishing SpecKit Extensions

Complete guide to releasing and distributing SpecKit extensions.

## Pre-Publishing Checklist

Before publishing, ensure your extension meets these requirements:

### Required Files
- [ ] `extension.yml` - Valid manifest with all required fields
- [ ] `README.md` - Installation and usage instructions
- [ ] `LICENSE` - Open source license (MIT, Apache-2.0, etc.)
- [ ] At least one command file in `commands/`

### Quality Checks
- [ ] All commands tested and working
- [ ] Helper scripts tested (if included)
- [ ] Configuration templates provided (if needed)
- [ ] Hooks tested at correct workflow points (if included)
- [ ] Documentation complete and accurate
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)

### Repository Setup
- [ ] Git repository created
- [ ] README includes examples
- [ ] CHANGELOG documenting changes
- [ ] All files committed
- [ ] Repository is public (for community catalog)

## Publishing Process

### Step 1: Prepare Release

#### 1.1 Update Version

Update version in `extension.yml`:

```yaml
extension:
  version: "1.0.0"  # MAJOR.MINOR.PATCH
```

**Versioning guidelines:**
- **MAJOR**: Breaking changes (e.g., command renamed, manifest structure changed)
- **MINOR**: New features (e.g., new commands added)
- **PATCH**: Bug fixes (e.g., command logic fixed, documentation updated)

#### 1.2 Update CHANGELOG

**File**: `CHANGELOG.md`

```markdown
# Changelog

## [1.0.0] - 2024-01-15

### Added
- Initial release
- `speckit.my-ext.hello` command
- `speckit.my-ext.goodbye` command
- Configuration support

### Changed
- N/A

### Fixed
- N/A
```

#### 1.3 Update README

Ensure README includes:

```markdown
# My Extension

Brief description of what the extension does.

## Installation

```bash
specify extension add my-ext
```

## Usage

### Hello Command

```bash
/speckit.my-ext.hello world
```

Description of what the command does.

### Goodbye Command

```bash
/speckit.my-ext.goodbye
```

Description of what the command does.

## Configuration

Optional configuration file: `.specify/extensions/my-ext/config.yml`

```yaml
setting1: value1
setting2: value2
```

## Requirements

- SpecKit >= 0.1.0
- Docker >= 20.0.0 (if applicable)

## License

MIT
```

### Step 2: Create GitHub Release

#### 2.1 Commit and Tag

```bash
# Commit all changes
git add -A
git commit -m "Release v1.0.0"

# Create tag
git tag v1.0.0

# Push changes and tag
git push origin main
git push origin v1.0.0
```

#### 2.2 Create Release on GitHub

1. Go to repository on GitHub
2. Click "Releases" → "Create a new release"
3. Select tag: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Description:
   ```markdown
   ## What's New
   
   - Initial release of My Extension
   - Adds hello and goodbye commands
   - Configuration support
   
   ## Installation
   
   ```bash
   specify extension add my-ext
   ```
   
   ## Full Changelog
   
   See [CHANGELOG.md](CHANGELOG.md) for details.
   ```
6. Click "Publish release"

### Step 3: Submit to Community Catalog

#### 3.1 Prepare Submission

Gather required information:
- Extension name and ID
- Repository URL
- Release tag (e.g., `v1.0.0`)
- Brief description (1-2 sentences)
- Tags/categories (e.g., `docker`, `security`, `validation`)

#### 3.2 Submit to Catalog

1. Go to: https://github.com/github/spec-kit/issues/new?template=extension_submission.yml
2. Fill out submission form:
   - **Extension Name**: My Extension
   - **Extension ID**: my-ext
   - **Repository URL**: https://github.com/username/speckit-my-ext
   - **Release Tag**: v1.0.0
   - **Description**: Brief description of extension functionality
   - **Categories**: Select applicable categories (Tool Integration, Quality Gate, etc.)
   - **Tags**: Comma-separated tags (docker, deployment, ci-cd)
   - **License**: MIT
   - **Author**: Your Name
3. Submit issue
4. Wait for maintainer review (typically 1-3 days)

#### 3.3 Catalog Review Process

Maintainers will check:
- Valid `extension.yml` manifest
- Working commands
- Complete documentation
- Appropriate license
- No security issues

**Common rejection reasons:**
- Invalid manifest syntax
- Missing required files
- Broken commands
- Insufficient documentation
- License issues

### Step 4: Organization Catalog (Optional)

For private/internal extensions that can't be published publicly:

#### 4.1 Create Organization Catalog

**File**: `catalog.json`

```json
{
  "schema_version": "1.0",
  "catalog": {
    "name": "Acme Corp Extensions",
    "description": "Internal SpecKit extensions for Acme Corp",
    "url": "https://extensions.acme.com/speckit/catalog.json"
  },
  "extensions": [
    {
      "id": "my-ext",
      "name": "My Extension",
      "version": "1.0.0",
      "description": "My custom extension for internal use",
      "author": "DevOps Team",
      "repository": "https://github.com/acme/speckit-my-ext",
      "download_url": "https://github.com/acme/speckit-my-ext/archive/refs/tags/v1.0.0.zip",
      "license": "Proprietary",
      "tags": ["internal", "acme", "validation"],
      "requires": {
        "speckit_version": ">=0.1.0"
      },
      "commands": [
        "speckit.my-ext.hello",
        "speckit.my-ext.goodbye"
      ]
    }
  ]
}
```

#### 4.2 Host Catalog

Host `catalog.json` on:
- GitHub Pages (public repos)
- Internal web server
- Cloud storage (S3, Azure Blob)
- Company intranet

**Example: GitHub Pages**

```bash
# Create gh-pages branch
git checkout --orphan gh-pages
git rm -rf .
echo '{"schema_version":"1.0","catalog":{"name":"My Catalog"},"extensions":[]}' > catalog.json
git add catalog.json
git commit -m "Initialize catalog"
git push origin gh-pages

# Catalog URL: https://username.github.io/speckit-catalog/catalog.json
```

#### 4.3 Configure Team Access

Team members set catalog URL:

```bash
# Via environment variable
export SPECKIT_CATALOG_URL="https://extensions.acme.com/speckit/catalog.json"

# Or in user config
specify config set catalog_url "https://extensions.acme.com/speckit/catalog.json"

# Test access
specify extension search
```

## Post-Publishing

### Monitor Usage

Track extension usage and issues:

```bash
# Monitor GitHub Stars/Forks
# Monitor GitHub Issues/PRs
# Collect user feedback
```

### Update Extension

For updates:

1. Make changes to extension code
2. Update version in `extension.yml` (bump MAJOR/MINOR/PATCH)
3. Update CHANGELOG.md
4. Create new git tag and release
5. Update catalog entry (if applicable)

**Example update:**

```bash
# Make changes
vim commands/hello.md

# Update version
vim extension.yml  # Change version to 1.1.0

# Update changelog
cat >> CHANGELOG.md <<EOF

## [1.1.0] - 2024-02-01

### Added
- Support for custom greetings

### Fixed
- Bug in argument parsing
EOF

# Commit, tag, release
git add -A
git commit -m "Release v1.1.0"
git tag v1.1.0
git push origin main v1.1.0
```

### Deprecation Process

If deprecating an extension:

1. Mark as deprecated in README
2. Add deprecation notice in extension.yml
3. Update catalog entry
4. Provide migration path if applicable
5. Set end-of-life date

**Example deprecation notice:**

```markdown
# My Extension

⚠️ **DEPRECATED**: This extension is no longer maintained. 
Please migrate to [new-extension](https://github.com/username/new-extension) 
by 2025-01-01.

## Migration Guide

See [MIGRATION.md](MIGRATION.md) for migration instructions.
```

## Testing Before Publishing

### Local Testing Workflow

```bash
# 1. Install locally
specify extension add --dev /path/to/extension

# 2. Verify installation
specify extension list

# 3. Test all commands
/speckit.my-ext.hello world
/speckit.my-ext.goodbye

# 4. Test hooks (if applicable)
specify tasks create  # Should trigger after_tasks hook

# 5. Test configuration
cat .specify/extensions/my-ext/config.yml

# 6. Uninstall
specify extension remove my-ext
```

### CI/CD Testing

Add automated testing to CI pipeline:

**File**: `.github/workflows/test-extension.yml`

```yaml
name: Test Extension

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install SpecKit
        run: pipx install git+https://github.com/github/spec-kit.git
      
      - name: Validate manifest
        run: specify extension validate .
      
      - name: Install extension
        run: specify extension add --dev .
      
      - name: Test commands
        run: |
          specify extension list | grep "my-ext"
          # Add command tests here
      
      - name: Uninstall
        run: specify extension remove my-ext
```

## Distribution Alternatives

### Via PyPI (Python Extensions)

If extension includes Python code:

```bash
# Package extension
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Users install via pip
pip install speckit-my-ext
```

### Via npm (JavaScript Extensions)

If extension includes JavaScript code:

```bash
# Package extension
npm pack

# Publish to npm
npm publish

# Users install via npm
npm install -g speckit-my-ext
```

### Direct Download

Users can install from URL:

```bash
# Install from GitHub release
specify extension add https://github.com/username/speckit-my-ext/archive/v1.0.0.zip

# Install from direct URL
specify extension add https://example.com/extensions/my-ext-1.0.0.zip
```

## Licensing Considerations

### Open Source Licenses

Popular choices:
- **MIT**: Permissive, simple, widely used
- **Apache 2.0**: Permissive, includes patent grant
- **GPL**: Copyleft, requires derivative works to be open source

### Proprietary/Internal

For internal-only extensions:
- Use "Proprietary" or "Internal Use Only" license
- Host in private organization catalog
- Restrict repository access
- Do not submit to public community catalog

## Resources

- [SpecKit Extension Guidelines](https://github.com/github/spec-kit/blob/main/extensions/GUIDELINES.md)
- [Semantic Versioning](https://semver.org/)
- [Choose a License](https://choosealicense.com/)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)
