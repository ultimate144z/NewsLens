# Contributing to NewsLens

Thank you for considering contributing to NewsLens! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Python 3.13+
- Git
- Virtual environment knowledge
- Basic understanding of NLP/data analysis

### Development Setup

1. *Fork the repository*
   ```bash
   git clone https://github.com/ultimate144z/NewsLens.git
   cd NewsLens
   ```

2. *Create virtual environment*
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. *Install dependencies*
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. *Run tests*
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Your Changes

#### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and returns
- Add comprehensive docstrings (Google style)
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

#### Example Function with Proper Documentation

```python
def fetch_articles(source: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch articles from a specific news source.
    
    Args:
        source: Name of the news source (e.g., 'BBC News')
        limit: Maximum number of articles to fetch (default: 100)
        
    Returns:
        List of article dictionaries with keys: title, description, link, etc.
        Returns empty list if source is invalid or fetch fails.
        
    Raises:
        ValueError: If limit is negative
        
    Example:
        >>> articles = fetch_articles('BBC News', limit=50)
        >>> print(f"Fetched {len(articles)} articles")
    """
    if limit < 0:
        raise ValueError("Limit must be non-negative")
    
    # Implementation here
    pass
```

#### Error Handling
Always add comprehensive error handling:

```python
try:
    result = api_call()
except requests.exceptions.Timeout:
    logger.error("Request timed out")
    return default_value
except requests.exceptions.RequestException as e:
    logger.error(f"Request failed: {e}")
    return default_value
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return default_value
```

### 3. Add Tests

Every new feature should have corresponding tests:

```python
# tests/test_your_feature.py
import pytest
from src.your_module import your_function

def test_your_function_success():
    """Test successful execution"""
    result = your_function(valid_input)
    assert result is not None
    assert len(result) > 0

def test_your_function_invalid_input():
    """Test error handling"""
    with pytest.raises(ValueError):
        your_function(invalid_input)
```

Run tests:
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_your_feature.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### 4. Format Your Code

```bash
# Format with Black
black src/ app/ tests/

# Check with flake8
flake8 src/ app/ tests/ --max-line-length=100
```

### 5. Update Documentation

- Add docstrings to all new functions/classes
- Update README.md if adding major features
- Add examples to relevant documentation files
- Update DEVELOPMENT_LOG.md with your changes

### 6. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add multi-language sentiment analysis

- Added support for Spanish, French, German
- Updated model config to handle language selection
- Added language detection for auto-selection
- Tests for all supported languages"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Detailed description of what changed and why
- Link to related issues (if any)
- Screenshots (for UI changes)
- Test results

## 🧪 Testing Guidelines

### Test Coverage
- Aim for >80% code coverage
- Test both success and failure cases
- Test edge cases and boundary conditions

### Test Organization
```
tests/
├── test_ingestion.py      # Data collection tests
├── test_preprocessing.py  # Text processing tests
├── test_analysis.py       # NLP analysis tests
├── test_storage.py        # Database tests
└── test_analytics.py      # Analytics tests
```

### Running Specific Tests
```bash
# Run tests for a specific module
pytest tests/test_ingestion.py -v

# Run tests matching a pattern
pytest tests/ -k "sentiment" -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

## 📝 Documentation Standards

### Code Documentation
- All public functions/classes need docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises, Examples
- Add inline comments for complex logic

### README Updates
Update README.md when adding:
- New features
- New dependencies
- New configuration options
- Installation changes

## 🐛 Reporting Bugs

### Before Reporting
1. Check if the bug has already been reported
2. Test with the latest version
3. Isolate the issue to reproduce consistently

### Bug Report Template
```markdown
*Describe the bug*
Clear description of what the bug is.

*To Reproduce*
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

*Expected behavior*
What you expected to happen.

*Screenshots*
If applicable, add screenshots.

*Environment:*
 - OS: [e.g., Windows 11]
 - Python Version: [e.g., 3.13.9]
 - NewsLens Version: [e.g., 1.0]

*Additional context*
Any other relevant information.
```

## 💡 Suggesting Features

### Feature Request Template
```markdown
*Is your feature request related to a problem?*
Clear description of the problem.

*Describe the solution you'd like*
Clear description of what you want to happen.

*Describe alternatives you've considered*
Other solutions or features you've considered.

*Additional context*
Any other context, mockups, or examples.
```

## 🎨 UI/UX Contributions

For dashboard improvements:
- Follow existing color scheme
- Maintain responsive design
- Test on different screen sizes
- Add loading states for async operations
- Provide user feedback for all actions

## 📊 Performance Considerations

When contributing code:
- Profile performance-critical sections
- Avoid unnecessary database queries
- Use batch operations where possible
- Consider memory usage for large datasets
- Add caching for expensive computations

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize data before database insertion
- Report security issues privately

## 📬 Questions?

- Open a [discussion](https://github.com/yourusername/NewsLens/discussions)
- Check existing [issues](https://github.com/yourusername/NewsLens/issues)
- Read the [documentation](docs/)

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the project

Thank you for contributing to NewsLens! 🎉

