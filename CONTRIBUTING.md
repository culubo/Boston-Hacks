# Contributing to Screen Privacy Blocker

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## Quick Start for Contributors

### 1. Fork and Clone
```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final
```

### 2. Set Up Development Environment
```bash
./setup.sh
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

---

## Contribution Guidelines

### Code Style

**Python:**
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and under 50 lines when possible

**Swift:**
- Follow Swift API Design Guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Use `// MARK:` to organize code sections

**Shell Scripts:**
- Use bash with `set -e` for error handling
- Add comments for non-obvious operations
- Include help text for user-facing scripts

### Commit Messages

Use lowercase, descriptive commit messages:

```bash
# Good:
git commit -m "add multi-monitor support"
git commit -m "fix memory leak in OCR processing"
git commit -m "update documentation for new features"

# Bad:
git commit -m "Fixed stuff"
git commit -m "WIP"
git commit -m "Update"
```

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

Examples:
- `feature/multi-monitor-support`
- `fix/websocket-connection-issue`
- `docs/update-installation-guide`

---

## Areas to Contribute

### High Priority

1. **Multi-Monitor Support** - Extend capture to multiple displays
2. **Performance Optimization** - Reduce CPU/memory usage
3. **PaddleOCR Integration** - Replace Tesseract for faster OCR
4. **Custom Patterns** - Allow users to define custom detection patterns
5. **UI Improvements** - Better visual feedback and settings

### Medium Priority

1. **Detection History** - Log and review past detections
2. **Whitelist/Blacklist** - Exclude specific applications
3. **Configurable Blocking Styles** - Blur, pixelate, custom colors
4. **Recording Mode** - Save detection logs for review
5. **Browser Extension** - Integrate with web browsers

### Low Priority / Nice to Have

1. **Cross-platform Support** - Linux/Windows versions
2. **Mobile Companion App** - Control from phone
3. **Team Sharing** - Share detection policies across teams
4. **Analytics Dashboard** - Visualize detection patterns
5. **Plugin System** - Allow third-party extensions

---

## Testing Your Changes

### Test Locally

1. **Run the application:**
 ```bash
 ./run.sh
 ```

2. **Test detection:**
 - Open a text editor
 - Type sensitive information (API keys, passwords, etc.)
 - Verify detection works correctly

3. **Test edge cases:**
 - Rapid screen changes
 - Large amounts of text
 - Different screen resolutions
 - Multiple applications

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Screen capture works properly
- [ ] OCR detects text correctly
- [ ] ML model classifies correctly
- [ ] Overlays appear in correct positions
- [ ] No memory leaks during extended use
- [ ] Permissions are handled correctly
- [ ] Clean shutdown without errors

---

## Reporting Bugs

When reporting bugs, include:

1. **macOS version:** `sw_vers`
2. **Python version:** `python3 --version`
3. **Detailed description** of the issue
4. **Steps to reproduce**
5. **Expected behavior**
6. **Actual behavior**
7. **Error messages or logs**
8. **Screenshots** (if applicable)

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue

## Environment
- macOS Version: X.X.X
- Python Version: X.X.X
- Installed via: setup.sh / manual

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Logs/Screenshots
```
Error messages or screenshots here
```

## Additional Context
Any other relevant information
```

---

## Feature Requests

We welcome feature requests! When suggesting a feature:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** or implementation approach
4. **Consider alternatives** and their trade-offs
5. **Estimate complexity** (if possible)

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Problem it Solves
What problem does this feature address?

## Proposed Solution
How should this work?

## Alternatives Considered
What other approaches could work?

## Additional Context
Any other relevant information
```

---

## Documentation

Help improve our documentation:

- Fix typos or unclear instructions
- Add examples or use cases
- Improve code comments
- Update outdated information
- Add troubleshooting tips

Documentation files:
- `README.md` - Main documentation
- `QUICKSTART.md` - Quick start guide
- `INSTALL.md` - Installation guide
- `CONTRIBUTING.md` - This file

---

## Pull Request Process

### Before Submitting

1. **Test thoroughly** on your local machine
2. **Update documentation** if needed
3. **Add comments** to complex code
4. **Ensure clean commit history**
5. **Rebase on latest main** if needed

### Submitting a PR

1. **Push your branch:**
 ```bash
 git push origin feature/your-feature-name
 ```

2. **Create Pull Request** on GitHub

3. **Fill out PR template** with:
 - Description of changes
 - Related issue numbers
 - Testing performed
 - Screenshots (if UI changes)

4. **Wait for review** and address feedback

### PR Title Format

```
[Type] Brief description

Examples:
[Feature] Add multi-monitor support
[Fix] Resolve WebSocket connection timeout
[Docs] Update installation instructions
[Refactor] Simplify OCR processing logic
```

### PR Review Process

- Maintainers will review within 3-5 days
- Address requested changes promptly
- Be open to feedback and discussion
- Squash commits if requested
- Ensure CI passes (if applicable)

---

## Code Organization

### Project Structure

```
blocker/
├── macos_app/ # Swift application
│ └── ScreenBlocker/
│ ├── CaptureBridge.swift
│ ├── OverlayManager.swift
│ └── ...
├── src/detector/ # Python detection engine
│ ├── recv_ws.py
│ ├── overlay_server.py
│ └── pattern_detector.py
├── Backend/ML Model/ # ML model and features
│ ├── final_model.pkl
│ ├── predict_one.py
│ └── features.py
├── scripts/ # Utility scripts
├── docs/ # Documentation
└── [setup files]
```

### Adding New Features

1. **Swift Components:**
 - Add to appropriate Swift file
 - Use `// MARK:` to organize
 - Follow existing patterns

2. **Python Components:**
 - Create new module if substantial
 - Import in appropriate files
 - Add to requirements.txt if new dependency

3. **Shell Scripts:**
 - Make executable with `chmod +x`
 - Add to README if user-facing

---

## Code of Conduct

### Our Pledge

We're committed to making this project welcoming and inclusive for everyone.

### Expected Behavior

- Be respectful and considerate
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility for mistakes
- Put the project's interests first

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

---

## Getting Help

Stuck or have questions?

1. **Check the documentation** first
2. **Search existing issues** on GitHub
3. **Open a new issue** with your question
4. **Be specific** about what you need help with

---

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Appreciated in the community!

---

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for contributing to Screen Privacy Blocker!** 

Your contributions help make the internet a more secure place for everyone.

