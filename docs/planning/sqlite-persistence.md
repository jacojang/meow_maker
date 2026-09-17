---
status: deployed
updated: 2026-09-17
---

# SQLite Persistence (Roadmap Phase 2)

## Goal

A server restart or redeploy should no longer lose every player's run.
Currently both `InMemorySessionPlayers` (session token → player id) and
`InMemoryGameRepository` (player id → `GameRun`) are plain in-process
dicts, wiped on every restart — an accepted tradeoff through Phase 1, no
longer acceptable once this ships regularly (as this project has been
doing multiple times a day).

## Scope

**In**

- A SQLite-backed `SessionPlayers` implementation and a SQLite-backed
  `GameRepository` implementation, matching the existing `SessionPlayers`/
  `GameRepository` ABCs exactly — no changes to `api.py`'s use of either,
  since both are already injected via `Depends`.
- Switching the default providers (`get_session_players()`,
  `get_game_repository()`) to the SQLite-backed classes.
- Table creation on startup (idempotent, no separate migration step yet —
  there's no data to migrate, every existing run is already in-memory and
  already lost on every restart).

**Out**

- Any change to `api.py`, `GameRun`, or `CatStats` — this phase is a
  storage swap only, not a schema/mechanics change.
- Real accounts — session token still maps 1:1 to a player row, per
  roadmap.md's "Designing for accounts later" (a login later just changes
  what resolves to that row).
- Migrating existing in-memory data — there is none worth keeping.

## Mechanics

**Two tables**, per the roadmap's sketch, with one deliberate deviation
(below):

```sql
CREATE TABLE player (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE game (
    player_id TEXT PRIMARY KEY REFERENCES player(id),
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**Deviation from the roadmap sketch**: `game` stores the whole
`GameRun.to_dict()` result as one `state_json` column instead of one
column per stat. Reasoning: this project has added a new stat five times
already (Refinement, age, weight, plus the two derived-but-serialized
flags `is_sick`/`diet`), each a one-line change to `CatStats`/`GameRun`
today. Columns would turn every future stat into a migration; a JSON blob
keeps `to_dict()`/`from_dict()` as the only source of truth for the run's
shape, matching how they're already used for the in-memory dict store.
Nothing today needs to query or filter on an individual stat, so there's
no cost to this beyond the (currently unused) ability to do so — normalize
into columns later if that need actually shows up. Also drops the
sketch's surrogate `game.id` column: one active run per player is the
whole current model (`GameRepository.save` already overwrites), so
`player_id` alone is the natural primary key; a surrogate key would be
unused abstraction for a "many runs per player" case that doesn't exist
yet.

**Connection strategy**: open and close a plain `sqlite3.connect(path)`
inside each method call (`get`/`save`/`player_for`), rather than holding
one connection across the app's lifetime. Every API endpoint is a sync
`def` (FastAPI runs these in a thread pool), and `sqlite3` connections
aren't safe to share across threads — opening one per call sidesteps that
entirely, at a cost (a fresh connection per request) that doesn't matter
at this project's scale. Revisit only if profiling ever says otherwise.

**DB file location**: `server/data/meow_maker.db` by default, overridable
via the `MEOW_DB_PATH` env var (tests point it at a `pytest`-provided
`tmp_path`). The parent directory is created on first use if missing, so
no separate provisioning step is needed on the EC2 instance — the file
appears on first request after the first Phase-2 deploy and persists
across every deploy after that (`deploy/deploy.sh` never touches
`server/data/`, only `git pull`s and restarts).

**Table creation**: lazy, not at import time. `db.ensure_initialized(path)`
runs the `CREATE TABLE IF NOT EXISTS` schema at most once per path (tracked
in a module-level set) the first time either default provider —
`get_game_repository()` or `get_session_players()` — is actually called.
`main.py` itself never calls any db-init function. This is deliberate:
`server/tests/conftest.py` overrides both providers via
`app.dependency_overrides`, so `import app.main` (which every API test
triggers) must not touch disk — if init ran at import time instead, every
test run would create a real file under `server/data/`. No migration
framework yet, since there's no prior schema to migrate away from.

## Open questions

None — resolved above.

## Next stage

Straight to Coding — this is an infrastructure swap behind an existing
interface, not a new screen or mechanic; no separate Design doc needed.

Testing: new tests in `server/tests/test_db.py` covering the two SQLite
classes directly against a `tmp_path` file (save with one instance, read
with a fresh instance pointed at the same file, confirming data survives
"restart"). Existing API-level tests (`server/tests/test_api.py`) are
unaffected — they already inject `InMemory*` fakes via
`app.dependency_overrides` and stay that way for speed/isolation; that
dependency-injection seam is exactly what lets the default swap to SQLite
without touching a single existing test.
