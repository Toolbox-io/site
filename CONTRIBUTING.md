# Contributing to Toolbox.io

Thank you for your interest in contributing to Toolbox.io! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/your-username/Toolbox.io/issues) page
- Search existing issues before creating new ones
- Use clear, descriptive titles
- Include steps to reproduce bugs
- Specify your environment (OS, browser, device)

### Suggesting Features
- Open a discussion or issue with the "enhancement" label
- Describe the use case and expected behavior
- Consider if the feature aligns with the project's goals

### Code Contributions
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 🛠️ Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 24
- Python 3.12
- Git

### Local Development
```bash
# Clone your fork
git clone https://github.com/Toolbox-io/site.git

# Set up environment
cp env.example .env
# Edit .env with your values

# Start development environment
docker-compose up -d

# For frontend development
cd frontend
npm install
npm run build
```

## 📝 Coding Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings for functions and classes
- Use meaningful variable names
- Keep functions focused and small

### TypeScript (Frontend)
- Use strict TypeScript configuration
- Follow ESLint rules
- Use meaningful variable and function names
- Add JSDoc comments for complex functions
- Prefer const over let when possible

### Kotlin (Android)
- Follow Kotlin coding conventions
- Use meaningful variable names
- Add KDoc comments for public functions
- Prefer immutable data structures
- Use proper error handling

### SCSS (Styling)
- Use BEM methodology for CSS classes
- Nest styles according to HTML hierarchy
- Use variables for colors and measurements
- Keep styles modular and reusable

## 🧪 Testing

### Backend Testing
```bash
cd backend/main
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Android Testing
```bash
cd ../Android
./gradlew test
```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows project coding standards
- [ ] Tests pass locally
- [ ] Documentation is updated if needed
- [ ] No sensitive data is included
- [ ] Commit messages are clear and descriptive

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

## 🐛 Bug Reports

When reporting bugs, please include:

### Required Information
- **OS**: Operating system and version
- **Browser**: Browser and version (for web issues)
- **Device**: Android version and device model (for app issues)
- **Steps**: Step-by-step reproduction instructions
- **Expected**: What you expected to happen
- **Actual**: What actually happened
- **Screenshots**: If applicable

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
- Browser: [e.g. Chrome 91, Firefox 89]
- Android: [e.g. Android 11, API 30]
- Device: [e.g. Samsung Galaxy S21]

**Additional context**
Add any other context about the problem here.
```

## ✨ Feature Requests

When suggesting features, please include:

### Required Information
- **Use Case**: Why is this feature needed?
- **User Story**: As a [user type], I want [goal] so that [benefit]
- **Acceptance Criteria**: What needs to be implemented?
- **Mockups**: Visual representations if applicable

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 🔒 Security

### Reporting Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email security issues to: security@toolbox-io.ru
- Use GitHub's private vulnerability reporting if available
- Include detailed reproduction steps
- Allow reasonable time for response before disclosure

### Security Guidelines
- Never commit sensitive data (API keys, passwords, tokens)
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Keep dependencies updated

## 📚 Documentation

### Code Documentation
- Add docstrings to Python functions and classes
- Add JSDoc comments to TypeScript functions
- Add KDoc comments to Kotlin functions
- Update README.md for significant changes

### API Documentation
- Update API_DOCS.md for new endpoints
- Include request/response examples
- Document error codes and messages
- Keep documentation current with code changes

## 🏷️ Labels and Milestones

### Issue Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `priority: high` - High priority
- `priority: medium` - Medium priority
- `priority: low` - Low priority

### Pull Request Labels
- `ready for review` - Ready for code review
- `needs testing` - Requires testing
- `breaking change` - Breaking change
- `documentation` - Documentation changes

## 🎯 Getting Help

### Community Support
- **GitHub Discussions**: For questions and general discussion
- **Issues**: For bug reports and feature requests
- **Email**: support@toolbox-io.ru

### Development Help
- Check existing issues and discussions
- Review the codebase and documentation
- Ask specific questions with context
- Be patient and respectful

## 📄 License

By contributing to Toolbox.io, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Toolbox.io! 🚀
