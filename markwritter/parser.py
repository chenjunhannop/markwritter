"""Parser with LLM-based intent recognition and keyword fallback."""

import json
from dataclasses import dataclass
from typing import Optional

from markwritter.config import get_config
from markwritter.llm_client import LLMClient
from markwritter.models import SkillDefinition


@dataclass
class ParsedIntent:
    """Result of parsing user input."""

    skill_name: Optional[str] = None
    params: dict[str, str] = None  # type: ignore
    confidence: float = 0.0
    reasoning: str = ""

    def __post_init__(self) -> None:
        if self.params is None:
            self.params = {}


class InputParser:
    """Parse natural language input using LLM with keyword fallback."""

    def __init__(
        self,
        available_skills: list[SkillDefinition],
        llm_client: Optional[LLMClient] = None,
        confidence_threshold: Optional[float] = None,
    ) -> None:
        """Initialize parser.

        Args:
            available_skills: List of available skills
            llm_client: LLM client for intent recognition. If None, uses keyword fallback only.
            confidence_threshold: Threshold for confidence matching. If None, reads from config.
        """
        self.skills = {s.name: s for s in available_skills}
        self.llm_client = llm_client
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
        else:
            self.confidence_threshold = get_config().parser.confidence_threshold

    def parse(self, user_input: str) -> ParsedIntent:
        """Parse user input and identify skill to invoke.

        Uses LLM for intent recognition when available, falls back to keyword matching.

        Args:
            user_input: Raw user input string

        Returns:
            ParsedIntent with skill_name, params, and confidence
        """
        # Try LLM-based parsing first
        if self.llm_client and self.skills:
            try:
                llm_result = self._parse_with_llm(user_input)
                if llm_result.confidence >= self.confidence_threshold:
                    return llm_result
            except Exception:
                # Fall back to keyword matching on LLM error
                pass

        # Fallback to keyword matching
        return self._parse_with_keywords(user_input)

    def _parse_with_llm(self, user_input: str) -> ParsedIntent:
        """Use LLM to parse intent and extract parameters."""
        # Build skills description for the prompt
        skills_desc = self._build_skills_description()

        prompt = f"""You are an intent recognition system for an AI agent framework.

Available skills:
{skills_desc}

User input: "{user_input}"

Analyze the user input and identify:
1. Which skill should be invoked (or null if no match)
2. What parameters to extract
3. Your confidence level (0.0-1.0)
4. Brief reasoning

Respond in JSON format:
{{
    "skill_name": "skill_name_or_null",
    "params": {{"param_name": "param_value"}},
    "confidence": 0.85,
    "reasoning": "brief explanation"
}}

Rules:
- Only return skill names from the available list
- Extract only parameters defined for that skill
- Use default values for missing optional parameters
- Confidence < 0.7 means no clear match"""

        response = self.llm_client.complete(prompt, temperature=0.1)

        # Parse JSON response
        try:
            # Extract JSON if wrapped in markdown
            content = response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())

            skill_name = result.get("skill_name")
            params = result.get("params", {})
            confidence = float(result.get("confidence", 0.0))
            reasoning = result.get("reasoning", "")

            # Validate skill exists
            if skill_name and skill_name not in self.skills:
                confidence = 0.0
                skill_name = None

            # Validate params against skill definition
            if skill_name:
                skill = self.skills[skill_name]
                valid_params = self._validate_params(skill, params)
                return ParsedIntent(
                    skill_name=skill_name,
                    params=valid_params,
                    confidence=confidence,
                    reasoning=reasoning,
                )

            return ParsedIntent(confidence=confidence, reasoning=reasoning)

        except json.JSONDecodeError:
            # LLM didn't return valid JSON, fallback
            return ParsedIntent(confidence=0.0, reasoning="Failed to parse LLM response")

    def _parse_with_keywords(self, user_input: str) -> ParsedIntent:
        """Fallback keyword-based parsing."""
        user_input_lower = user_input.lower()

        # Simple keyword matching
        for skill_name, skill in self.skills.items():
            # Check if skill name is mentioned
            if skill_name.lower() in user_input_lower:
                params = self._extract_params(skill, user_input)
                return ParsedIntent(
                    skill_name=skill_name,
                    params=params,
                    confidence=0.5,  # Lower confidence for keyword match
                    reasoning="Keyword match on skill name",
                )

            # Check if skill description keywords match
            desc_words = skill.description.lower().split()
            matches = sum(1 for word in desc_words if word in user_input_lower)
            if matches >= 2:
                params = self._extract_params(skill, user_input)
                return ParsedIntent(
                    skill_name=skill_name,
                    params=params,
                    confidence=0.3,
                    reasoning="Description keyword match",
                )

        return ParsedIntent(confidence=0.0, reasoning="No match found")

    def _build_skills_description(self) -> str:
        """Build a description of all available skills for the LLM prompt."""
        lines = []
        for skill in self.skills.values():
            line = f"- {skill.name}: {skill.description}"
            if skill.inputs:
                params = ", ".join(f"{inp.name} ({inp.type})" for inp in skill.inputs)
                line += f" [Parameters: {params}]"
            lines.append(line)
        return "\n".join(lines)

    def _validate_params(self, skill: SkillDefinition, params: dict[str, str]) -> dict[str, str]:
        """Validate and filter parameters against skill definition."""
        valid_params: dict[str, str] = {}
        defined_params = {inp.name: inp for inp in skill.inputs}

        # Only keep params defined in skill
        for name, value in params.items():
            if name in defined_params:
                valid_params[name] = str(value)

        # Apply defaults for optional params
        for inp in skill.inputs:
            if inp.name not in valid_params and inp.default is not None:
                valid_params[inp.name] = str(inp.default)

        return valid_params

    def _extract_params(self, skill: SkillDefinition, user_input: str) -> dict[str, str]:
        """Extract parameters from user input using regex patterns."""
        import re

        params: dict[str, str] = {}

        for input_def in skill.inputs:
            # Look for --param value pattern
            pattern = rf"--{input_def.name}\s+(\S+)"
            match = re.search(pattern, user_input)
            if match:
                params[input_def.name] = match.group(1)
            else:
                # Apply default if available
                if input_def.default is not None:
                    params[input_def.name] = str(input_def.default)

        return params
