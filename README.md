# engram

> Persistent memory for AI agents — graph-backed, vector-searchable, with biologically-inspired memory decay.

[![CI](https://github.com/KaranamJyothirmayi/engram/actions/workflows/ci.yml/badge.svg)](https://github.com/KaranamJyothirmayi/engram/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)

## What is engram?

Most AI memory tools store facts forever with equal weight. **engram** is different: memory fades over time unless reinforced — modelled on the [Ebbinghaus forgetting curve](https://en.wikipedia.org/wiki/Forgetting_curve).

Every stored memory has a **strength** that decays exponentially with elapsed time and gets boosted every time it's recalled. Old, unused memories become weak candidates for pruning. Frequently-accessed memories stay strong.

## Install

```bash
pip install engram
```

For named-entity extraction (improves relationship linking):

```bash
pip install "engram[nlp]"
python -m spacy download en_core_web_sm
```

## Quick Start

```python
import asyncio
import engram

async def main():
    await engram.remember("Marie Curie was born in Warsaw.", dataset="science")

    results = await engram.recall(
        "Where was Marie Curie born?",
        datasets=["science"],
    )
    for r in results:
        print(f"[{r['strength']:.2f}] {r['text']}")

    # Remove memories that have faded below 20% strength
    removed = await engram.prune(dataset="science", threshold=0.2)

asyncio.run(main())
```

## API

| Function | Description |
|---|---|
| `remember(text, dataset)` | Store text as memory (strength = 1.0) |
| `recall(query, datasets)` | Search memories; reinforces what's returned |
| `improve(text, dataset)` | Add content and reset all dataset strengths to 1.0 |
| `prune(dataset, threshold)` | Remove memories below strength threshold |
| `forget(dataset)` | Delete all memories in a dataset |

## How Memory Decay Works

```
strength(t) = S₀ × e^(−k × hours_elapsed)
```

- Default decay rate `k = 0.005` (~50% strength after ~6 days of no access)
- `recall()` reinforces retrieved memories (+0.3, capped at 1.0)
- Configure: `ENGRAM_DECAY_RATE=0.002 python your_script.py`

## Architecture

```
engram API (remember / recall / improve / prune / forget)
    ├── MemoryGraph (NetworkX)    ← entity relationship graph
    ├── VectorIndex (ChromaDB)   ← semantic similarity search
    ├── DecayEngine              ← Ebbinghaus strength scoring
    └── MetaStore (SQLite)       ← metadata + per-memory strength
```

Data stored in `~/.engram/` by default. Override: `ENGRAM_HOME=/path/to/dir`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Good first issues are labeled
[`good first issue`](https://github.com/KaranamJyothirmayi/engram/issues?q=label%3A%22good+first+issue%22).

## License

Apache 2.0 — see [LICENSE](LICENSE).
