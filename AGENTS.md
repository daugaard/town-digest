# AGENTS

This file guides automated agents working on this repository.

## Mission
Build a calm, chronological civic digest using modern Python and clean-code best practices.

## Core Principles
- Prefer clarity over cleverness. Code should read linearly and be easy to reason about.
- Make small, composable units. Keep functions focused with explicit inputs/outputs.
- Favor immutable data and pure functions where practical.
- Use explicit typing and structured data models to reduce ambiguity.
- Fail fast with clear errors; validate boundaries early.

## Python Standards
- Target Python 3.13+ features when they simplify code (e.g., `|` unions, `dataclass` slots, pattern matching where readable).
- Use type hints everywhere: function signatures, class attributes, and public module APIs.
- Prefer `pathlib.Path` over `os.path`.
- Avoid global state; if needed, isolate and document it.
- Keep side effects at the edges (I/O, network, DB). Core logic should be side-effect free.

## Code Style
- Follow PEP 8 with a bias toward readability.
- Use consistent naming: `snake_case` for functions/variables, `PascalCase` for classes.
- Write docstrings for public functions/classes and modules with non-obvious behavior.
- Avoid overly generic names (`data`, `info`, `tmp`) unless scoped tightly.

## Project Practices
- Add tests for new behavior and for any bug fixes.
- Prefer integration tests for pipelines and boundary-heavy logic.
- Structure code with clear module boundaries under `src/`.
- Keep the `readme.md` accurate when behavior or setup changes.

## Dependencies
- Minimize new dependencies. Justify any additions and prefer stdlib when reasonable.
- Keep dependency versions compatible with `pyproject.toml` and `uv.lock`.

## Review Checklist
- Type hints in place and consistent.
- Public APIs documented.
- Tests added/updated.
- No unused imports or dead code.
- Clear error handling at boundaries.

## Tooling Notes
- Use `uv` for dependency management and execution.
- Keep `pytest` green; do not disable tests to pass.
- Use `ruff` for linting.
- Run `uv run ruff check .` for CI-safe lint runs.
- Run `uv run ruff check . --fix` for autofixable lint issues.
