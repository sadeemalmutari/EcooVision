# Contributing to EcooVision

First off, thank you for considering contributing to EcooVision! It's people like you that make EcooVision such a great project.

## Code of Conduct

By participating in this project, you agree to maintain our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Be constructive in criticism
- Focus on what is best for the community

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:

1. **Check existing issues** to ensure it hasn't been reported
2. **Test with latest version** to confirm it's still an issue
3. **Gather information** to help reproduce the bug

When submitting a bug report:

1. Use a clear, descriptive title
2. Describe the exact steps to reproduce
3. Include expected vs. actual behavior
4. Provide relevant system information
5. Add screenshots if applicable

Use this template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.10.0]
- Django version: [e.g. 5.1.4]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

We welcome enhancement suggestions! Before submitting:

1. Check if similar enhancement exists
2. Consider the scope - is it appropriate for the project?
3. Provide use cases and examples

When submitting an enhancement:

1. Use a clear, descriptive title
2. Explain the motivation and use case
3. Describe your proposed solution
4. Provide examples or mockups if applicable

### Pull Requests

Follow these steps for pull requests:

1. **Fork the repository**
2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   
3. **Make your changes**
   - Follow our coding standards
   - Add tests if applicable
   - Update documentation
   
4. **Test your changes**
   ```bash
   python manage.py test
   python -m pytest EviTrain/tests/
   ```
   
5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```
   
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
   
7. **Create Pull Request**

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Virtual environment (venv)

### Installation

```bash
# Clone your fork
git clone https://github.com/yourusername/EcooVision.git
cd EcooVision

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
cd EviTrain && pip install -r requirements.txt && cd ..

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## Coding Standards

### Python Style Guide

We follow PEP 8:

```bash
# Use black for formatting
black --check .
black .

# Use flake8 for linting
flake8 .

# Use mypy for type checking
mypy src/
```

### Code Guidelines

1. **Naming Conventions**
   - Use descriptive names
   - Constants: UPPER_CASE
   - Classes: PascalCase
   - Functions/Variables: snake_case

2. **Documentation**
   - Add docstrings to all functions/classes
   - Use Google-style docstrings
   - Comment complex logic

3. **Imports**
   ```python
   # Standard library
   import os
   from datetime import datetime
   
   # Third-party
   import django
   from django.shortcuts import render
   
   # Local
   from main.views import HomeView
   ```

4. **Type Hints**
   ```python
   def calculate_savings(hours: float, rate: float) -> float:
       return hours * rate
   ```

### Git Commit Messages

Use conventional commits:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(prediction): add weather-based exit duration predictor

fix(recognition): handle multiple faces in frame

docs(readme): update installation instructions
```

## Testing

### Running Tests

```bash
# Django tests
python manage.py test

# Pytest
pytest

# Specific test
pytest tests/test_models.py

# With coverage
pytest --cov=src tests/
```

### Writing Tests

Follow the AAA pattern:

```python
def test_exit_duration_prediction():
    # Arrange
    model = load_model()
    sample_data = create_sample()
    
    # Act
    prediction = model.predict(sample_data)
    
    # Assert
    assert prediction >= 0
    assert prediction <= 48
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def process_weather_data(weather_code: int) -> str:
    """Convert weather code to description.
    
    Args:
        weather_code: Numeric weather code (0-16)
    
    Returns:
        Weather description string
    
    Raises:
        ValueError: If weather_code is out of range
    
    Example:
        >>> process_weather_data(0)
        'Sunny'
    """
    # Implementation
```

## Project Structure

Key directories:

- `EviTrain/` - Machine learning models and Streamlit app
- `facerecognition/` - Face recognition module
- `main/` - Django main app
- `elec/` - Energy calculator
- `templates/` - HTML templates
- `media/` - Uploaded files

## Review Process

1. Submit pull request
2. Automated checks run (CI/CD)
3. Code review by maintainers
4. Address feedback
5. Merge when approved

## Questions?

- Open a discussion in GitHub
- Contact: support@ecoovision.ai
- Join our Discord community

Thank you for contributing! 🎉

