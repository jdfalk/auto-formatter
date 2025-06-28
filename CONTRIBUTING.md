<!-- file: CONTRIBUTING.md -->

# Contributing to Auto Formatter

We welcome contributions to the Auto Formatter GitHub Action! This document
provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- **Python 3.8+** for the issue manager script
- **Node.js 18+** for JavaScript tooling
- **Go 1.20+** for testing Go formatting (optional)
- **Git** for version control

### Quick Start

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/auto-formatter.git
   cd auto-formatter
   ```

2. **Install dependencies**

   ```bash
   make install
   # or manually:
   pip install -r requirements-dev.txt
   npm install
   ```

3. **Run tests**

   ```bash
   make test
   ```

4. **Format and lint code**

   ```bash
   make format
   make lint
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

   - Follow the coding standards outlined below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**

   ```bash
   make test
   make lint
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new formatting feature"
   ```

5. **Push and create a pull request**

   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools

Examples:

```bash
feat: add support for Rust formatting
fix: resolve issue with Python line length detection
docs: update README with new configuration options
style: format code with prettier
test: add tests for Go formatting functionality
```

## Coding Standards

### Python Code

- **Follow PEP 8** style guidelines
- **Use type hints** for function parameters and return values
- **Document functions** with Google-style docstrings
- **Line length**: Maximum 88 characters
- **Import sorting**: Use isort with Google profile

Example:

```python
def process_formatting_request(
    language: str,
    file_paths: List[str],
    config: Dict[str, Any]
) -> FormattingResult:
    """
    Process a formatting request for the specified language.

    Args:
        language: The programming language to format
        file_paths: List of file paths to format
        config: Configuration options for formatting

    Returns:
        FormattingResult containing status and details

    Raises:
        FormattingError: If formatting fails
    """
    # Implementation here
    pass
```

### JavaScript/TypeScript Code

- **Use Prettier** for consistent formatting
- **Follow ESLint** rules for code quality
- **Use TypeScript** when possible for type safety
- **Document functions** with JSDoc comments

### YAML/Configuration Files

- **Use 2-space indentation**
- **Quote strings** when necessary
- **Keep lines under 100 characters**
- **Add comments** for complex configurations

## Testing Guidelines

### Python Tests

- **Use pytest** for test framework
- **Aim for 80%+ code coverage**
- **Mock external dependencies** (GitHub API, subprocess calls)
- **Test both success and failure cases**

Example test structure:

```python
class TestFormattingManager:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_api = MagicMock()
        self.manager = FormattingManager(self.mock_api)

    def test_format_python_files_success(self):
        """Test successful Python file formatting."""
        # Test implementation
        pass

    def test_format_python_files_no_files(self):
        """Test behavior when no Python files found."""
        # Test implementation
        pass
```

### Action Testing

- **Test action.yml syntax** with action-validator
- **Test workflows** locally with act (when possible)
- **Provide example workflows** in the examples/ directory
- **Document expected inputs and outputs**

## Adding New Language Support

To add support for a new programming language:

1. **Update action.yml**

   - Add new input parameters if needed
   - Update action description

2. **Modify the formatting steps**

   - Add tool installation in the "Install formatters" step
   - Add a new formatting step for the language

3. **Update configuration files**

   - Add default configuration files for the language
   - Update .prettierignore or similar ignore files

4. **Add tests**

   - Create tests for the new language formatting
   - Test both success and error cases

5. **Update documentation**
   - Add language to README.md
   - Update CHANGELOG.md
   - Add example configuration

### Example: Adding Rust Support

```yaml
# In action.yml
- name: Run Rust formatting
  if:
    steps.check_commit.outputs.skip == 'false' && (contains(inputs.languages,
    'rust') || contains(inputs.languages, 'all'))
  shell: bash
  run: |
    cd ${{ inputs.working-directory }}
    echo "Formatting Rust files..."

    if find . -name "*.rs" -type f | grep -q .; then
      echo "Found Rust files, applying formatting..."
      rustfmt --edition 2021 $(find . -name "*.rs")
      echo "Rust formatting complete"
    else
      echo "No Rust files found"
    fi
```

## Documentation

### README Updates

- **Keep examples current** and working
- **Document all input parameters**
- **Provide troubleshooting guides**
- **Include performance considerations**

### Code Documentation

- **Document public APIs** thoroughly
- **Include usage examples** in docstrings
- **Explain complex algorithms** with comments
- **Keep comments up-to-date** with code changes

## Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. **Update version numbers**

   - action.yml
   - package.json
   - CHANGELOG.md

2. **Run release preparation**

   ```bash
   make release
   ```

3. **Create release commit**

   ```bash
   git add .
   git commit -m "chore: prepare release v1.2.3"
   ```

4. **Create and push tag**

   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin main --tags
   ```

5. **Create GitHub release**
   - Go to GitHub releases page
   - Create new release from tag
   - Add release notes from CHANGELOG.md

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Request Reviews**: Code review and feedback

### Useful Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Action Creation Guide](https://docs.github.com/en/actions/creating-actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

### Common Issues

**Action not working locally**

- Use [act](https://github.com/nektos/act) for local testing
- Check action.yml syntax with action-validator
- Verify all required inputs are provided

**Tests failing**

- Ensure all dependencies are installed
- Check Python path configuration
- Verify mock configurations are correct

**Formatting not applied**

- Check file patterns and ignore rules
- Verify formatter installation
- Review action logs for error messages

Thank you for contributing to Auto Formatter!
