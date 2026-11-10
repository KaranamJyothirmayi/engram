# Contributing to engram

Thank you for your interest! Here's everything you need to get started.

## Setup

```bash
git clone https://github.com/KJyothirmayi-2025sl93025/engram.git
cd engram
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -v                      # all tests should pass
```

Optional spaCy support:

```bash
pip install ".[nlp]"
python -m spacy download en_core_web_sm
```

## Code Style

```bash
ruff check engram/ tests/    # lint
ruff format engram/ tests/   # auto-format
```

CI fails on ruff errors.

## Making a Contribution

1. Pick an issue (look for `good first issue` labels)
2. Create a branch: `git checkout -b feat/your-feature`
3. Write tests first, then implementation (TDD)
4. Run `pytest -v` and `ruff check` — both must pass
5. Open a PR against `main` and reference the issue (`Closes #N`)

## PR Guidelines

- One feature or fix per PR
- Tests required for all new code
- Update README if public API changes

## Questions

Open a [GitHub Discussion](https://github.com/KJyothirmayi-2025sl93025/engram/discussions) or comment on the issue.
