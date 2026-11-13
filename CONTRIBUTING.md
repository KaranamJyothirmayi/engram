# Contributing to engram

Thank you for your interest! Here's everything you need to get started.

## Contributor License Agreement (CLA)

Before your first Pull Request can be merged, you must sign our [Contributor License Agreement](CLA.md).

**How to sign:** Post the following comment on your PR:

> `I have read the CLA Document and I hereby sign the CLA`

The CLA bot will detect this comment and mark your PR as compliant. You only need to sign once — all future PRs from your account are automatically recognized.

> **Why a CLA?** It ensures the project can remain open source and that all contributions are legally clear.

---

## Get Started

### 1. Fork and clone

```bash
git clone https://github.com/YOUR_USERNAME/engram.git
cd engram
```

### 2. Set up your environment

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Verify everything works

```bash
pytest -v                      # all tests should pass
ruff check engram/ tests/      # no lint errors
```

### 4. Optional: spaCy NLP support

```bash
pip install ".[nlp]"
python -m spacy download en_core_web_sm
```

### 5. Pick an issue and start

Browse [`good first issue`](https://github.com/KaranamJyothirmayi/engram/labels/good%20first%20issue)
for beginner-friendly tasks. Leave a comment on the issue you want to work on so others know it's taken.

---

## Making a Contribution

1. Create a branch: `git checkout -b feat/your-feature`
2. Write tests first, then implementation
3. Run `pytest -v` and `ruff check` — both must pass
4. Add an entry to `CHANGELOG.md` under `## Unreleased` (see Documentation Guidelines below)
5. Open a PR against `main` referencing the issue (`Closes #N`)
6. Sign the CLA when prompted by the bot

---

## Code Style

```bash
ruff check engram/ tests/    # lint
ruff format engram/ tests/   # auto-format
```

CI fails on ruff errors. We use `ruff` for both linting and formatting — no other tools needed.

---

## AI Use Policy and Guidelines

We welcome AI-assisted contributions, but you are responsible for every line you submit.

**The core rule:** You must be able to explain any change you propose. The answer to
"Why did you make change X?" should never be "I'm not sure — the AI did it."
Submitting unreviewed AI-generated code wastes maintainer time and will be closed without review.

**As a coding assistant:**
- Read and understand the relevant code before asking an AI to modify it.
- LLMs often misrepresent how libraries work internally — verify against the actual source.
- Break AI-generated changes into coherent commits with meaningful messages.
- Do not include AI-generated comments that merely repeat what the code already says.

**For PR descriptions:**
- Write your own description — explain the *why*, not just the what.
- If you used AI assistance, disclose it (e.g. "AI-assisted contribution, reviewed and tested by me").
- Verify accuracy: do not paste AI-generated descriptions without reading them.

---

## Documentation Guidelines

Documentation improvements are a great first contribution. We welcome fixes for anything
unclear, confusing, or inaccurate.

**What we accept:**
- Fixes for incorrect or misleading content
- Expanding examples or clarifying edge cases
- Updating docs when public API changes

**What we generally decline:**
- Purely stylistic rewrites with no factual change
- Large restructures without prior discussion (open an issue first)

**Changelog requirement:**

Every PR that changes behaviour, adds a feature, or fixes a bug must include an entry
in `CHANGELOG.md` under the `## Unreleased` section. Format:

```
## Unreleased

- feat: add `list_datasets()` async API (#9)
- fix: stale item_count after pruning (#9)
- test: edge-case coverage for memory API (#10)
```

Use `feat:`, `fix:`, `test:`, `docs:`, or `chore:` prefixes.
Tests-only PRs and pure doc typo fixes are exempt.

---

## PR Guidelines

- One feature or fix per PR
- Tests required for all new code — coverage must not drop below 65%
- Update README if public API changes
- Add a `CHANGELOG.md` entry under `## Unreleased`
- Do **not** report security vulnerabilities in issues — see [SECURITY.md](SECURITY.md)

---

## Security Issues

If you find a vulnerability, **do not open a public issue**. Follow the instructions in
[SECURITY.md](SECURITY.md) for responsible disclosure.

---

## Questions

Open a [GitHub Discussion](https://github.com/KaranamJyothirmayi/engram/discussions)
or comment on the relevant issue.
