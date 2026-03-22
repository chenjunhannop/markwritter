"""CLI entry point for Markwritter framework."""

from pathlib import Path
from typing import Optional

import typer

from markwritter.core import Framework
from markwritter.logger import setup_logging
from markwritter.registry import SkillRegistry

app = typer.Typer(
    name="markwritter",
    help="A lightweight Agent orchestration framework",
    add_completion=False,
)

# Global framework instance
_framework: Optional[Framework] = None


def get_framework() -> Framework:
    """Get or create framework instance."""
    global _framework
    if _framework is None:
        setup_logging()  # Initialize logging
        skills_dir = Path("./skills").resolve()
        registry = SkillRegistry(skills_dir)
        _framework = Framework(registry)
    return _framework


@app.command()
def run(
    skill_name: str = typer.Argument(..., help="Name of the skill to run"),
    args: Optional[list[str]] = typer.Argument(None, help="Arguments in key=value format"),
) -> None:
    """Run a specific skill with arguments."""
    framework = get_framework()

    # Parse arguments
    params = {}
    if args:
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                params[key] = value

    result = framework.run_skill(skill_name, params)
    typer.echo(result)


@app.command()
def list_skills() -> None:
    """List all available skills."""
    framework = get_framework()
    skills = framework.list_skills()

    if not skills:
        typer.echo("No skills found.")
        return

    typer.echo("Available skills:")
    for skill in skills:
        typer.echo(f"  - {skill['name']}: {skill['description']}")


@app.command()
def chat() -> None:
    """Start interactive chat mode."""
    framework = get_framework()

    typer.echo("Markwritter Chat Mode")
    typer.echo("Type 'exit' or 'quit' to exit")
    typer.echo("-" * 40)

    while True:
        try:
            user_input = typer.prompt("> ")
            user_input = user_input.strip()

            if user_input.lower() in ("exit", "quit", "q"):
                break

            if not user_input:
                continue

            result = framework.process_input(user_input)
            typer.echo(result)

        except KeyboardInterrupt:
            break
        except EOFError:
            break

    typer.echo("\nGoodbye!")


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
