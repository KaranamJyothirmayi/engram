# Project Roadmap

This roadmap reflects the current direction of engram based on open issues and community interest.
It is a living document — priorities shift based on contributions and feedback.

> **Note:** Dates are targets, not commitments. Issues move between milestones based on community
> contributions. Want to help? Pick any issue tagged
> [`good first issue`](https://github.com/KaranamJyothirmayi/engram/labels/good%20first%20issue).

Status key: 🔵 In Progress · ✅ Completed · 📋 Planned

---

## v0.1.0 — Foundation ✅ Released

Core memory engine: `remember`, `recall`, `prune`, `forget`, `improve`.
Ebbinghaus exponential decay, sentence-level extraction, SQLite storage,
vector index for semantic search, knowledge graph for entity relationships.

---

## v0.2 — API Completeness 📋

> Goal: make the core Python API complete and production-ready before adding interfaces.

| Issue | Title | Labels |
|---|---|---|
| [#5](https://github.com/KaranamJyothirmayi/engram/issues/5) | Add `list_datasets()` function | 🔵 In Progress (PR [#9](https://github.com/KaranamJyothirmayi/engram/pull/9)) |
| [#6](https://github.com/KaranamJyothirmayi/engram/issues/6) | Improve test coverage | 🔵 In Progress (PR [#10](https://github.com/KaranamJyothirmayi/engram/pull/10)) |
| [#8](https://github.com/KaranamJyothirmayi/engram/issues/8) | Make decay rate configurable per-dataset | 🔵 In Progress (PR [#11](https://github.com/KaranamJyothirmayi/engram/pull/11)) |
| [#12](https://github.com/KaranamJyothirmayi/engram/issues/12) | Add `stats()` API — dataset health metrics | `enhancement` `good first issue` |
| [#13](https://github.com/KaranamJyothirmayi/engram/issues/13) | Add `remember_many()` — bulk ingest | `enhancement` `good first issue` |
| [#14](https://github.com/KaranamJyothirmayi/engram/issues/14) | Add `update()` API — edit memory text in place | `enhancement` |
| [#15](https://github.com/KaranamJyothirmayi/engram/issues/15) | Add duplicate detection | `enhancement` |
| [#16](https://github.com/KaranamJyothirmayi/engram/issues/16) | Add `list_memories()` — filter by strength range | `enhancement` `good first issue` |
| [#17](https://github.com/KaranamJyothirmayi/engram/issues/17) | Add memory tagging — key-value metadata | `enhancement` |
| [#18](https://github.com/KaranamJyothirmayi/engram/issues/18) | Make recall reinforcement boost configurable | `enhancement` `good first issue` |
| [#19](https://github.com/KaranamJyothirmayi/engram/issues/19) | Add `export()` and `import()` — JSON serialization | `enhancement` |

---

## v0.3 — Interfaces 📋

> Goal: every major interface ships — CLI, REST API, and MCP server.

| Issue | Title | Labels |
|---|---|---|
| [#1](https://github.com/KaranamJyothirmayi/engram/issues/1) | Add a REST API with FastAPI | `enhancement` |
| [#2](https://github.com/KaranamJyothirmayi/engram/issues/2) | Add a CLI (`engram remember/recall/forget/prune`) | `enhancement` `good first issue` |
| [#4](https://github.com/KaranamJyothirmayi/engram/issues/4) | Add an MCP server for Claude/Cursor integration | `enhancement` |
| [#20](https://github.com/KaranamJyothirmayi/engram/issues/20) | Add pagination to `recall()` — limit/offset | `enhancement` `good first issue` |
| [#21](https://github.com/KaranamJyothirmayi/engram/issues/21) | Add OpenAPI schema and auto-generated docs | `enhancement` `docs` |
| [#22](https://github.com/KaranamJyothirmayi/engram/issues/22) | Add `engram stats` CLI subcommand | `enhancement` |
| [#23](https://github.com/KaranamJyothirmayi/engram/issues/23) | Add `engram shell` — interactive REPL mode | `enhancement` |
| [#24](https://github.com/KaranamJyothirmayi/engram/issues/24) | Add streaming `recall()` — async generator | `enhancement` |

---

## v0.4 — Integrations 📋

> Goal: engram works as a drop-in memory layer across the AI/LLM ecosystem.

| Issue | Title | Labels |
|---|---|---|
| [#7](https://github.com/KaranamJyothirmayi/engram/issues/7) | Add a TypeScript/JavaScript client SDK | `enhancement` |
| [#25](https://github.com/KaranamJyothirmayi/engram/issues/25) | LangChain integration — `EngramMemory` | `enhancement` `integration` |
| [#26](https://github.com/KaranamJyothirmayi/engram/issues/26) | LlamaIndex integration — `EngramMemoryBuffer` | `enhancement` `integration` |
| [#27](https://github.com/KaranamJyothirmayi/engram/issues/27) | OpenAI tool/function calling integration | `enhancement` `integration` |
| [#28](https://github.com/KaranamJyothirmayi/engram/issues/28) | Add Jupyter notebook examples | `docs` `good first issue` |
| [#29](https://github.com/KaranamJyothirmayi/engram/issues/29) | Add Docker image + docker-compose example | `enhancement` `maintenance` |
| [#30](https://github.com/KaranamJyothirmayi/engram/issues/30) | Add GitHub Codespaces / devcontainer support | `maintenance` `good first issue` |
| [#31](https://github.com/KaranamJyothirmayi/engram/issues/31) | Add async context manager — `engram.session()` | `enhancement` |
| [#32](https://github.com/KaranamJyothirmayi/engram/issues/32) | Add webhook support for memory events | `enhancement` |

---

## v0.5 — Scale & Production 📋

> Goal: production-ready for server deployments, multi-user apps, and observability.

| Issue | Title | Labels |
|---|---|---|
| [#3](https://github.com/KaranamJyothirmayi/engram/issues/3) | Add file ingestion support (`.txt`, `.pdf`) | `enhancement` `good first issue` |
| [#33](https://github.com/KaranamJyothirmayi/engram/issues/33) | Add PostgreSQL backend | `enhancement` |
| [#34](https://github.com/KaranamJyothirmayi/engram/issues/34) | Add Alembic schema migrations | `maintenance` |
| [#35](https://github.com/KaranamJyothirmayi/engram/issues/35) | Add encryption at rest | `enhancement` `security` |
| [#36](https://github.com/KaranamJyothirmayi/engram/issues/36) | Add multi-user/tenant support | `enhancement` |
| [#37](https://github.com/KaranamJyothirmayi/engram/issues/37) | Add Prometheus metrics endpoint | `enhancement` |
| [#38](https://github.com/KaranamJyothirmayi/engram/issues/38) | Add performance benchmark suite | `testing` `maintenance` |

---

## Backlog — Community Driven

> No committed version. Contributions welcome — open a discussion on the issue before starting.

| Issue | Title | Labels |
|---|---|---|
| [#39](https://github.com/KaranamJyothirmayi/engram/issues/39) | Add custom decay function plugin | `enhancement` |
| [#40](https://github.com/KaranamJyothirmayi/engram/issues/40) | Add property-based tests with Hypothesis | `testing` |
| [#41](https://github.com/KaranamJyothirmayi/engram/issues/41) | Add memory importance scoring on `remember()` | `enhancement` `good first issue` |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
Browse [`good first issue`](https://github.com/KaranamJyothirmayi/engram/labels/good%20first%20issue)
for beginner-friendly tasks across all milestones.
