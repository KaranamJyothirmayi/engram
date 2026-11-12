# Contributing to engram

Thank you for your interest! Here's everything you need to get started.

## Contributor License Agreement (CLA)

Before your first Pull Request can be merged, you must sign our [Contributor License Agreement](CLA.md).

**How to sign:** Post the following comment on your PR:

> `I have read the CLA Document and I hereby sign the CLA`

The CLA bot will detect this comment and mark your PR as compliant. You only need to sign once — all future PRs from your account are automatically recognized.

> **Why a CLA?** It ensures the project can remain open source and that all contributions are legally clear.

---

## Setup

```bash
git clone https://github.com/KaranamJyothirmayi/engram.git
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
6. Sign the CLA in the PR comment if prompted by the bot

## PR Guidelines

- One feature or fix per PR
- Tests required for all new code — coverage must not drop
- Update README if public API changes
- Do **not** report security vulnerabilities in issues — see [SECURITY.md](SECURITY.md)

## Security Issues

If you find a vulnerability, **do not open a public issue**. Follow the instructions in [SECURITY.md](SECURITY.md) for responsible disclosure.

## Questions

Open a [GitHub Discussion](https://github.com/KaranamJyothirmayi/engram/discussions) or comment on the issue.
