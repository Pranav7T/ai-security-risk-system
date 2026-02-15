# Contributing to AI Security Risk System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Virtual environment (venv or conda)

### Setup Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/ai-security-risk-system.git
   cd ai-security-risk-system
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # Linux/macOS
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov flake8
   ```

## 📝 Code Style Guidelines

### Python Code Style
- Follow **PEP 8** style guidelines
- Use **meaningful variable names**
- Add **docstrings** to all functions and classes
- Keep **line length ≤ 120 characters**

### Example
```python
def validate_input(data):
    """
    Validate input data for prediction endpoint.
    
    Args:
        data (dict): Input data to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Implementation
    pass
```

### Linting
```bash
flake8 api/ --max-line-length=120
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
pytest --cov=api tests/

# Run specific test file
pytest tests/test_api.py
```

### Write Tests
```python
def test_health_endpoint():
    """Test health check endpoint"""
    from api.app import app
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

## 🔄 Pull Request Process

1. **Update your local branch**
   ```bash
   git pull origin main
   ```

2. **Test your changes**
   ```bash
   pytest
   flake8 api/
   ```

3. **Commit with meaningful messages**
   ```bash
   git commit -m "Add feature: describe what was added"
   git commit -m "Fix bug: describe what was fixed"
   git commit -m "Improve documentation: describe the improvement"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request on GitHub**
   - Provide a clear title and description
   - Reference any related GitHub issues
   - Link to relevant discussions

## 📋 Commit Message Guidelines

Use clear, descriptive commit messages:

```
<type>: <short description>

<optional longer description>

Example:
feat: Add API rate limiting endpoint
fix: Resolve JSON validation error for null values
docs: Update README with Docker instructions
refactor: Improve error handling in predict endpoint
test: Add unit tests for input validation
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation updates
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `perf`: Performance improvements
- `ci`: CI/CD configuration changes

## 🐛 Reporting Issues

### Make a Good Bug Report
Include:
1. **Title**: Clear, concise description
2. **Environment**: OS, Python version, relevant versions
3. **Steps to Reproduce**: Exact steps to trigger the bug
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Screenshots/Logs**: Relevant error messages or logs

### Example
```
Title: Health endpoint returns 500 on startup

Environment:
- Windows 10, Python 3.11, Flask 2.3.3

Steps to Reproduce:
1. Start the API with `python api/app.py`
2. Immediately call GET /health
3. Observe the response

Expected: 200 OK with status: healthy
Actual: 500 Internal Server Error

Logs:
FileNotFoundError: [Errno 2] No such file or directory: 'model/model.pkl'
```

## 🎯 Feature Requests

Suggest enhancements using GitHub Discussions:

1. **Clear Title**: "Feature: Add API authentication"
2. **Use Case**: Explain why this feature is needed
3. **Proposed Solution**: How should it work
4. **Alternatives**: Other approaches considered

## 📦 Project Structure

Keep the project structure clean:

```
ai-security-risk-system/
├── api/
│   └── app.py              # Main API
├── model/
│   ├── train_model.py      # Model training
│   ├── test.py             # Model testing
│   └── model.pkl           # Trained model
├── dataset/
│   └── security_data.csv   # Training data
├── tests/                  # Test files
│   ├── test_api.py
│   └── test_validation.py
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── Dockerfile              # Docker config
└── .github/
    └── workflows/          # CI/CD
```

## 💡 Development Tips

### Debug Mode
```python
from api.app import app
app.run(debug=True)
```

### Test Endpoints Locally
```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"failed_login_attempts": 3, "login_time_deviation": 0.5, "ip_change": 1, "device_change": 0, "transaction_amount_deviation": 0.8}'
```

### Check Dependencies
```bash
pip list
pip check
```

## 🔐 Security Guidelines

- **Never commit secrets** (.env, API keys, passwords)
- **Validate all inputs** before processing
- **Sanitize error messages** to avoid information leakage
- **Use environment variables** for sensitive config
- **Keep dependencies updated** for security patches

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [GitHub Guides](https://guides.github.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Questions?

- Check existing **GitHub Issues** and **Discussions**
- Review the **README.md** and **API_DOCUMENTATION.md**
- Start a **GitHub Discussion** for questions

## 🙏 Thank You!

Your contributions make this project better. Whether it's code, documentation, bug reports, or ideas, we appreciate your involvement!

---

**Last Updated:** February 15, 2026
