# Auto Formatter

A comprehensive GitHub Action for automatically formatting code across multiple
programming languages and file types. This action provides consistent code
formatting for Python, Go, JavaScript/TypeScript, CSS, Markdown, HTML, and
many other common file formats.

## Features

### Supported Languages & Tools

- **Python**: ruff format + ruff check + isort (Google style standards)
- **Go**: gofumpt + goimports + golines (with line length limits)
- **JavaScript/TypeScript**: prettier + eslint (with auto-fix)
- **CSS/SCSS/Sass/Less**: prettier + stylelint (with auto-fix)
- **Markdown**: prettier + markdownlint (with auto-fix)
- **HTML**: prettier formatting
- **Additional formats**: YAML, TOML, XML, JSON (via prettier)

### Key Capabilities

- 🔄 **Automatic formatting** on pull requests and pushes
- 🚫 **Skip redundant runs** - detects recent auto-format commits
- 💬 **PR comments** with formatting status and details
- ⚙️ **Configurable** language selection and formatting options
- 📊 **Quality integration** with linting and security checks
- 🔧 **Issue management** for formatting problems and code reviews

## Quick Start

### Basic Usage

Create `.github/workflows/auto-format.yml` in your repository:

```yaml
name: Auto Format

on:
  pull_request:
    types: [opened, synchronize]
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          ref: ${{ github.head_ref }}
          fetch-depth: 0

      - name: Auto Format Code
        uses: jdfalk/auto-formatter@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          languages: 'all'
```

### Advanced Configuration

```yaml
      - name: Auto Format Code
        uses: jdfalk/auto-formatter@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          languages: 'python,go,nodejs,css,markdown'
          python-line-length: 88
          commit-message: 'style: auto-format with custom message'
          add-pr-comment: true
          working-directory: '.'
```

## Configuration Options

### Input Parameters

| Parameter            | Description                      | Default               | Options                                                    |
| -------------------- | -------------------------------- | --------------------- | ---------------------------------------------------------- |
| `token`              | GitHub token for pushing changes | `${{ github.token }}` | GitHub token                                               |
| `languages`          | Languages to format              | `'all'`               | `all`, `python`, `go`, `nodejs`, `css`, `markdown`, `html` |
| `python-line-length` | Python max line length           | `88`                  | Any number                                                 |
| `commit-message`     | Custom commit message            | Auto-generated        | Any string                                                 |
| `skip-if-no-changes` | Skip commit if no changes        | `true`                | `true`, `false`                                            |
| `add-pr-comment`     | Add PR status comment            | `true`                | `true`, `false`                                            |
| `working-directory`  | Working directory                | `'.'`                 | Any path                                                   |

### Language-Specific Configuration

#### Python (.ruff.toml)
```toml
[format]
line-length = 88
quote-style = "double"
indent-style = "space"

[lint]
select = ["E", "F", "I", "B", "C4", "UP"]
ignore = ["E501"]
```

#### JavaScript/TypeScript (.prettierrc.json)
```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

#### CSS (.stylelintrc.json)
```json
{
  "extends": ["stylelint-config-standard"],
  "rules": {
    "color-named": "never",
    "function-url-quotes": "always"
  }
}
```

## Issue Management Integration

The action includes an enhanced issue management system:

### Features

- **Copilot Review Tickets**: Automatically manages GitHub Copilot review comments
- **Duplicate Issue Cleanup**: Identifies and closes duplicate issues
- **CodeQL Security Alerts**: Creates issues for security vulnerabilities
- **Formatting Analysis**: Detects and reports code formatting inconsistencies

### Usage

```bash
# Check for formatting issues
python scripts/issue_manager.py format-check

# Process issue updates
python scripts/issue_manager.py update-issues

# Handle GitHub webhook events
python scripts/issue_manager.py event-handler

# Close duplicate issues
python scripts/issue_manager.py close-duplicates --dry-run
```

## Examples

### Format Only Python and Go

```yaml
- uses: jdfalk/auto-formatter@v1
  with:
    languages: 'python,go'
    python-line-length: 120
```

### Custom Commit Messages

```yaml
- uses: jdfalk/auto-formatter@v1
  with:
    commit-message: 'feat: apply automated code formatting'
    add-pr-comment: false
```

### Monorepo with Subdirectory

```yaml
- uses: jdfalk/auto-formatter@v1
  with:
    working-directory: 'backend/'
    languages: 'python,go'
```

## Output Values

| Output         | Description                             |
| -------------- | --------------------------------------- |
| `changes-made` | Whether formatting changes were applied |
| `skipped`      | Whether formatting was skipped          |

Example usage:

```yaml
- name: Auto Format
  id: format
  uses: jdfalk/auto-formatter@v1

- name: Check if changes were made
  if: steps.format.outputs.changes-made == 'true'
  run: echo "Code was formatted!"
```

## Integration with Other Tools

### Pre-commit Hooks

The action can work alongside pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
```

### Code Quality Pipeline

```yaml
jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: jdfalk/auto-formatter@v1

  quality:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - name: Run quality checks
        run: |
          ruff check .
          golangci-lint run
          npm run lint
```

## Troubleshooting

### Common Issues

**Action skips formatting unexpectedly**
- Check if the last commit message contains "style: auto-format"
- Use workflow dispatch with `force-format: true`

**Permission denied when pushing**
- Ensure `contents: write` permission is set
- Verify the token has repository access

**Formatters not found**
- The action installs formatters automatically
- Check the action logs for installation errors

**Large repositories timeout**
- Increase the job timeout: `timeout-minutes: 30`
- Consider formatting only changed files

### Debug Mode

Enable debug logging by setting:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/jdfalk/auto-formatter.git
cd auto-formatter

# Install development dependencies
pip install -r requirements-dev.txt
npm install

# Run tests
python -m pytest
npm test
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**Made with ❤️ for better code formatting across all languages**
