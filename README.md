# Markwritter

A lightweight Agent orchestration framework.

## Overview

Markwritter is a minimal Agent orchestration framework that parses user intent, manages Skills, and delegates execution to subagents. The framework itself is a lightweight shell—all functionality is provided through pluggable Skills.

## Philosophy

- **Framework as Core**: The framework understands user intent, manages Skills, schedules execution
- **Skills as Extensions**: Specific functions are implemented through Skills, keeping the framework lean
- **Dialogue-Based Interaction**: Users express needs in natural language, the framework parses and routes
- **Subagent Execution**: Framework delegates tasks to subagents rather than executing directly

## Project Structure

```
markwritter/
├── markwritter/            # Framework core
│   ├── __init__.py
│   ├── cli.py             # Typer CLI entry
│   ├── core.py            # Framework orchestrator
│   ├── models.py          # Pydantic models
│   ├── parser.py          # Intent parser
│   ├── registry.py        # Skill registry
│   └── executor.py        # Subagent executor
├── skills/                # Skill definitions
│   └── hello/            # Example skill
│       ├── skill.yaml    # Skill metadata
│       └── run.py        # Skill implementation
├── tests/                # Test suite
│   └── test_framework.py
├── note/                 # Design documentation
│   ├── framework-design.md
│   ├── openclaw-analysis.md
│   ├── mvp-design.md     # (Legacy: old design)
│   └── core-design.md    # (Legacy: old design)
└── pyproject.toml        # Project configuration
```

## Quick Start

### Installation

```bash
pip install -e .
```

### CLI Usage

```bash
# List available skills
markwritter list-skills

# Run a skill directly
markwritter run hello name=World

# Interactive chat mode
markwritter chat
> hello
> hello --name Alice
```

## Creating a Skill

1. Create a directory under `skills/<skill-name>/`
2. Add `skill.yaml` defining inputs, outputs, and execution
3. Add `run.py` (or other script) implementing the skill

Example `skill.yaml`:

```yaml
name: hello
description: Simple greeting skill
version: 1.0.0

inputs:
  - name: name
    type: string
    description: Name to greet
    required: true
    default: World

output:
  type: string
  description: Greeting message

execution:
  command: python
  script: run.py
  timeout: 30
```

Example `run.py`:

```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="World")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()
```

## Architecture

```
User Input → Parser → Registry → Executor → Skill (Subagent)
                ↓
         Skill Definition (YAML)
```

- **Parser**: Extracts skill name and parameters from natural language
- **Registry**: Loads and manages skill definitions from `skills/` directory
- **Executor**: Runs skills as subagent subprocesses
- **Skill**: Independent agent that performs specific tasks

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Project Status

- [x] Phase 1: Core framework skeleton
- [x] Phase 2: Registry and Parser
- [x] Phase 3: Executor and subagent execution
- [x] Phase 4: CLI interface
- [ ] Phase 5: Advanced parser (LLM-based intent recognition)
- [ ] Phase 6: GUI interface

## License

MIT
