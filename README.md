# engram

> Persistent memory for AI agents — graph-backed, vector-searchable, with biologically-inspired memory decay.

[![CI](https://github.com/KaranamJyothirmayi/engram/actions/workflows/ci.yml/badge.svg)](https://github.com/KaranamJyothirmayi/engram/actions/workflows/ci.yml)
[![CodeQL](https://github.com/KaranamJyothirmayi/engram/actions/workflows/codeql.yml/badge.svg)](https://github.com/KaranamJyothirmayi/engram/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/KaranamJyothirmayi/engram/badge)](https://securityscorecards.dev/viewer/?uri=github.com/KaranamJyothirmayi/engram)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## What is engram?

**engram** is a persistent memory library for AI agents and applications. It stores information as discrete memories, each with a **strength** that decays over time and gets reinforced whenever it is recalled — modelled on the [Ebbinghaus forgetting curve](https://en.wikipedia.org/wiki/Forgetting_curve).

Most AI memory tools store every fact forever with equal weight. engram is different:

- **Old, unused memories fade.** Information you haven't accessed in weeks naturally weakens and can be pruned.
- **Frequently-recalled memories stay strong.** The act of recalling a memory reinforces it, just like human memory.
- **Different topics forget at different speeds.** You can configure a faster decay rate for news datasets and a slower rate for core facts.
- **Semantic search, not keyword matching.** Recall uses vector similarity so "Where was Marie Curie born?" finds "Marie Curie was born in Warsaw." even without exact words.
- **Entity-aware.** Named entities are extracted and linked in a knowledge graph, so related memories surface together.

The name comes from neuroscience: an *engram* is the physical trace a memory leaves in the brain.

---

## Why engram?

AI agents increasingly need memory that behaves more like human memory — not a flat log of everything ever said, but a living store where relevance and recency shape what surfaces. engram is designed for:

- **Conversational agents** that need to remember user preferences and past interactions without growing unboundedly.
- **Research assistants** that ingest documents and surface the most relevant, recently-reinforced knowledge.
- **Personal knowledge tools** where older, forgotten ideas naturally fade while frequently-revisited concepts stay sharp.
- **Multi-topic stores** where different datasets (work notes vs. casual reading) decay at different speeds.

---

## Install

```bash
pip install engram
```

For named-entity extraction (improves relationship linking between memories):

```bash
pip install "engram[nlp]"
python -m spacy download en_core_web_sm
```

---

## Quick Start

```python
import asyncio
import engram

async def main():
    # Store memories
    await engram.remember("Marie Curie was born in Warsaw.", dataset="science")
    await engram.remember("She discovered polonium and radium.", dataset="science")
    await engram.remember("The Eiffel Tower is in Paris.", dataset="geography")

    # Recall — semantic search, reinforces returned memories
    results = await engram.recall("Marie Curie birthplace", datasets=["science"])
    for r in results:
        print(f"[{r['strength']:.2f}] {r['text']}")

    # Inspect datasets
    datasets = await engram.list_datasets()
    for d in datasets:
        print(f"{d['name']}: {d['item_count']} memories")

    # Remove memories that have faded below 20% strength
    removed = await engram.prune(dataset="science", threshold=0.2)
    print(f"Pruned {removed} weak memories")

asyncio.run(main())
```

---

## API

### Core

| Function | Description |
|---|---|
| `remember(text, dataset="default", strength=1.0)` | Store text with initial strength between 0.0 and 1.0 |
| `recall(query, datasets, limit, offset)` | Search memories semantically; reinforces what's returned |
| `improve(text, dataset)` | Add content and reset all dataset strengths to 1.0 |
| `prune(dataset, threshold)` | Remove memories below strength threshold |
| `forget(dataset)` | Delete all memories in a dataset |
| `list_datasets()` | List all datasets with name and live item count |

Set `strength` when storing lower-priority information:

```python
await engram.remember("Nice to know.", dataset="work", strength=0.5)
```

Every sentence extracted from the text starts at that strength. The default remains
1.0; out-of-range or non-finite values raise `ValueError` before storing memories.
Normal decay, recall reinforcement and pruning still apply afterward.

### Configuration

| Function | Description |
|---|---|
| `configure(home, ...)` | Set the storage directory and options |
| `set_decay_rate(dataset, rate)` | Set a per-dataset decay rate; `None` reverts to global |
| `reset()` | Clear the in-memory store reference (useful in tests) |

---

## How Memory Decay Works

Memory strength follows the Ebbinghaus forgetting curve:

```
strength(t) = S₀ × e^(−k × hours_elapsed)
```

- **S₀** — initial strength (1.0 when first stored)
- **k** — decay rate (default `0.005`, configurable)
- **hours_elapsed** — time since the memory was last accessed

At the default rate, a memory reaches ~50% strength after ~6 days without access and ~10% after ~19 days.

### Reinforcement

Every `recall()` call boosts the strength of returned memories by **+0.3** (capped at 1.0), resetting their decay clock. Memories you access regularly stay strong indefinitely.

### Per-dataset decay rates

Different datasets can forget at different speeds:

```python
# News fades quickly — half-life of ~14 hours
await engram.set_decay_rate("news", decay_rate=0.05)

# Core facts fade slowly — half-life of ~138 days
await engram.set_decay_rate("fundamentals", decay_rate=0.0001)

# Or set at store time
await engram.remember("Breaking news.", dataset="news", decay_rate=0.05)
```

### Global configuration

```bash
# Override default decay rate
ENGRAM_DECAY_RATE=0.002 python your_script.py

# Override storage directory
ENGRAM_HOME=/path/to/dir python your_script.py
```

---

## Architecture

```
engram API  (remember / recall / improve / prune / forget / list_datasets)
    │
    ├── Extractor              ← sentence splitting + named-entity extraction
    │
    ├── MemoryGraph (NetworkX) ← entity relationship graph
    │                            related entities surface together in recall
    │
    ├── VectorIndex (ChromaDB) ← semantic similarity search
    │                            finds relevant memories without exact keywords
    │
    ├── DecayEngine            ← Ebbinghaus strength scoring
    │                            per-dataset or global decay rate
    │
    └── MetaStore (SQLite)     ← source of truth
                                 stores text, strength, timestamps, dataset,
                                 decay_rate, and memory metadata
```

Data is stored in `~/.engram/` by default. Override with `ENGRAM_HOME=/path/to/dir`.

Each dataset is fully isolated — memories in `"science"` never appear in `"geography"` recall results.

---

## Configuration Reference

| Option | Environment variable | Default | Description |
|---|---|---|---|
| Storage directory | `ENGRAM_HOME` | `~/.engram/` | Where SQLite and vector index files are stored |
| Global decay rate | `ENGRAM_DECAY_RATE` | `0.005` | Ebbinghaus k value for all datasets without a custom rate |

---

## Project Status

engram is at **v0.1.0** — the core memory engine is stable and tested. Active development is ongoing across four upcoming milestones:

| Milestone | Goal | Status |
|---|---|---|
| **v0.2** | API completeness — stats, bulk ingest, export/import, tagging | In progress |
| **v0.3** | Interfaces — CLI, REST API, MCP server | Planned |
| **v0.4** | Integrations — LangChain, LlamaIndex, OpenAI tools, TypeScript SDK | Planned |
| **v0.5** | Scale & production — PostgreSQL, encryption, multi-user | Planned |

See the full [ROADMAP.md](ROADMAP.md) for all 38 open issues with version targets.

---

## Contributing

Contributions are welcome across all milestones — from good first issues to advanced features.

- **Get started:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Find work:** [`good first issue`](https://github.com/KaranamJyothirmayi/engram/issues?q=label%3A%22good+first+issue%22) label
- **Roadmap:** [ROADMAP.md](ROADMAP.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Governance:** [GOVERNANCE.md](GOVERNANCE.md)
- **Code of Conduct:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Security:** [SECURITY.md](SECURITY.md) — please do not open public issues for vulnerabilities

All contributors must sign the [CLA](CLA.md) before their first PR can be merged.
The CLA bot will prompt you automatically.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
