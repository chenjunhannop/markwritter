"""Core framework orchestrator."""

from typing import Optional

from markwritter.config import get_config
from markwritter.executor import SkillExecutor
from markwritter.llm_client import LLMClient
from markwritter.parser import InputParser
from markwritter.registry import SkillRegistry


class Framework:
    """Main framework orchestrator."""

    def __init__(self, registry: SkillRegistry) -> None:
        self.registry = registry
        self.executor = SkillExecutor(registry.skills_dir)
        self.llm_client: Optional[LLMClient] = None
        self._parser: Optional[InputParser] = None

    def _get_parser(self) -> InputParser:
        """Get or create parser with LLM support."""
        if self._parser is None:
            # Try to initialize LLM client if not already done
            if self.llm_client is None:
                try:
                    config = get_config()
                    if config.llm.default_model:
                        self.llm_client = LLMClient(config.llm)
                except Exception:
                    # LLM not available, use keyword fallback
                    pass

            self._parser = InputParser(
                self.registry.list_all(),
                llm_client=self.llm_client,
            )
        return self._parser

    def process_input(self, user_input: str) -> str:
        """Process user input and execute appropriate skill."""
        # Parse intent using LLM-enhanced parser
        parser = self._get_parser()
        intent = parser.parse(user_input)

        if intent.skill_name is None or intent.confidence < 0.5:
            return (
                "I couldn't understand what you want to do. Available commands:\n"
                + self._get_help_text()
            )

        # Get skill definition
        skill = self.registry.get(intent.skill_name)
        if skill is None:
            return f"Skill '{intent.skill_name}' not found."

        # Execute skill
        result = self.executor.execute_sync(skill, intent.params)

        if result.success:
            return (
                result.output
                if result.output
                else f"Skill '{intent.skill_name}' executed successfully."
            )
        else:
            error_msg = result.error if result.error else "Unknown error"
            return f"Error executing '{intent.skill_name}': {error_msg}"

    def run_skill(self, skill_name: str, params: dict[str, str]) -> str:
        """Run a specific skill by name."""
        skill = self.registry.get(skill_name)
        if skill is None:
            return f"Skill '{skill_name}' not found."

        result = self.executor.execute_sync(skill, params)

        if result.success:
            return (
                result.output if result.output else f"Skill '{skill_name}' executed successfully."
            )
        else:
            error_msg = result.error if result.error else "Unknown error"
            return f"Error: {error_msg}"

    def list_skills(self) -> list[dict[str, str]]:
        """List all available skills."""
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
            }
            for skill in self.registry.list_all()
        ]

    def _get_help_text(self) -> str:
        """Generate help text with available skills."""
        skills = self.list_skills()
        if not skills:
            return "  (No skills loaded)"

        lines = []
        for skill in skills:
            lines.append(f"  - {skill['name']}: {skill['description']}")
        return "\n".join(lines)
