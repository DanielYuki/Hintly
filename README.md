# Hintly - Google Classroom Agent Skills Exploration

An educational project exploring **Anthropic Agent Skills** with Google Classroom integration.

## Overview

Hintly consists of three focused Agent Skills:

| Skill | Purpose |
|-------|---------|
| `classroom-explorer` | Navigate and browse Google Classroom data |
| `classroom-analyzer` | Analyze and summarize educational content |
| `classroom-solver` | Solve activities and assignments |

## Quick Start

```bash
# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Authenticate with Google Classroom
python skills/classroom-explorer/scripts/auth.py --setup
```

## Project Structure

```
hintly/
├── core/                # Shared utilities
├── skills/              # Agent Skills
│   ├── classroom-explorer/
│   ├── classroom-analyzer/
│   └── classroom-solver/
├── notebooks/           # Interactive notebooks
├── outputs/             # Generated reports/solutions
└── tests/               # Unit tests
```

## Skills Usage

Each skill has a `SKILL.md` that Claude reads to understand its capabilities.

### Explorer

```bash
python skills/classroom-explorer/scripts/list_courses.py
```

### Analyzer

```bash
python skills/classroom-analyzer/scripts/analyze_material.py --course-id <ID> --material-id <ID>
```

### Solver

```bash
python skills/classroom-solver/scripts/solve_activity.py --course-id <ID> --activity-id <ID>
```

## Development

```bash
# Install with dev dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check --fix .
```

## Phase 2: DSPy (Future)

```bash
# Install DSPy support
uv sync --extra dspy
```

## License

MIT
