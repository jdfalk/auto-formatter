# file: CHANGELOG.md

# Changelog

All notable changes to the Auto Formatter action will be documented in this
file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-20

### Added

#### Core Features

- **Multi-language auto-formatting** support for Python, Go,
  JavaScript/TypeScript, CSS, Markdown, HTML
- **Smart skip detection** to avoid redundant formatting runs
- **Configurable language selection** with granular control
- **Automatic tool installation** for all supported formatters
- **PR comment integration** with detailed formatting status

#### Python Support

- **ruff format** for code formatting (replaces black)
- **ruff check** with auto-fix for linting
- **isort** for import sorting with Google style
- **Configurable line length** (default: 88)
- **Google Python style standards** compliance

#### Go Support

- **gofumpt** for stricter formatting than gofmt
- **goimports** for import management
- **golines** for long line handling (max 120 chars)
- **go mod tidy** for dependency cleanup

#### JavaScript/TypeScript Support

- **prettier** for consistent code formatting
- **eslint** with auto-fix capabilities
- **Support for .js, .jsx, .ts, .tsx, .vue** files
- **Configurable formatting options**

#### CSS Support

- **prettier** for CSS, SCSS, Sass, Less files
- **stylelint** with auto-fix for CSS linting
- **Configurable style rules**

#### Markdown Support

- **prettier** for consistent markdown formatting
- **markdownlint** with auto-fix capabilities
- **Configurable line length and prose wrapping**

#### HTML Support

- **prettier** for HTML file formatting
- **Configurable indentation and whitespace handling**

#### Additional Language Support

- **YAML/YML** formatting with prettier
- **TOML** file formatting
- **XML and SVG** file formatting
- **JSON** file formatting with proper indentation

#### Issue Management System

- **Enhanced issue_manager.py** script with formatting integration
- **Copilot review comment** ticket management
- **Duplicate issue detection** and cleanup
- **CodeQL security alert** issue generation
- **Formatting analysis** and issue reporting
- **GitHub webhook event** handling

#### Configuration Features

- **Flexible input parameters** for customization
- **Working directory** support for monorepos
- **Custom commit messages** for auto-format commits
- **Skip options** for conditional formatting
- **Output values** for workflow integration

#### Quality Integration

- **Pre-commit hook** compatibility
- **CI/CD pipeline** integration examples
- **Code quality check** workflow templates
- **Security scanning** integration

### Configuration Files Added

- `.ruff.toml` - Python formatting and linting configuration
- `.prettierrc.json` - JavaScript/CSS/Markdown/HTML formatting
- `.prettierignore` - Files to exclude from prettier formatting
- `.eslintrc.json` - JavaScript/TypeScript linting configuration
- `.stylelintrc.json` - CSS linting configuration
- `.markdownlint.json` - Markdown linting configuration

### Workflow Templates

- `auto-format.yml` - Complete auto-formatting workflow
- Multi-stage pipeline with formatting and quality checks
- Example configurations for various use cases

### Documentation

- **Comprehensive README.md** with usage examples
- **Configuration guide** for all supported languages
- **Integration examples** for common scenarios
- **Troubleshooting guide** for common issues
- **Development setup** instructions

### Technical Features

- **Automatic tool installation** across multiple package managers
- **Smart change detection** to avoid unnecessary commits
- **Error handling** and graceful degradation
- **Performance optimization** for large repositories
- **Cross-platform support** (Linux, macOS, Windows)

## [Unreleased]

### Planned Features

- **Rust** formatting support with rustfmt
- **C/C++** formatting support with clang-format
- **Java** formatting support with google-java-format
- **PHP** formatting support with PHP-CS-Fixer
- **Ruby** formatting support with RuboCop
- **Shell script** formatting with shfmt
- **Dockerfile** linting and formatting
- **Terraform** formatting with terraform fmt
- **GitHub App** version for enhanced permissions
- **Custom formatter** plugin system
- **Formatting diff** reports in PR comments
- **Performance metrics** and timing reports

### Improvements

- Enhanced error reporting with actionable suggestions
- Better handling of binary files and large files
- Incremental formatting for changed files only
- Integration with more CI/CD platforms
- Enhanced configuration validation
- Automated configuration file generation

---

## Development

### Version Numbering

- **Major version** (x.0.0): Breaking changes or major feature additions
- **Minor version** (1.x.0): New features, backward compatible
- **Patch version** (1.0.x): Bug fixes, minor improvements

### Release Process

1. Update version numbers in action.yml and package files
2. Update CHANGELOG.md with new features and changes
3. Create and test release candidate
4. Create GitHub release with detailed notes
5. Update marketplace listing

### Breaking Changes

- Major version updates may include breaking changes
- Deprecated features will be announced one version in advance
- Migration guides provided for breaking changes
