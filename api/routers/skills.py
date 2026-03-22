"""Skills API router."""

from fastapi import APIRouter, HTTPException

from api.models.skill import SkillResponse
from api.services.framework_bridge import get_framework

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/", response_model=list[SkillResponse])
async def list_skills():
    """List all available skills."""
    framework = get_framework()
    skills = framework.registry.list_all()
    return [SkillResponse.from_definition(s) for s in skills]


@router.get("/{skill_name}", response_model=SkillResponse)
async def get_skill(skill_name: str):
    """Get a specific skill by name."""
    framework = get_framework()
    skill = framework.registry.get(skill_name)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse.from_definition(skill)
