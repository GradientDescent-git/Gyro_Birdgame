# Contributing to VisionBird

Thank you for your interest in contributing to VisionBird!

## Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/GradientDescent-git/Gyro_Birdgame.git
   cd Gyro_Birdgame
   ```

2. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest pytest-cov ruff mypy
   ```

3. **Running Tests & Linter**:
   ```bash
   python -m pytest tests/ -v
   ruff check app/ tests/
   ```

## Pull Request Guidelines
- Ensure all tests pass cleanly.
- Maintain scale-invariant feature extraction and hysteresis thresholds.
- Do not introduce breaking API changes without updating unit tests.
