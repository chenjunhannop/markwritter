"""Skills API router."""

from fastapi import APIRouter, HTTPException

from markwritter.api.models.skill import SkillResponse, SkillRunRequest, SkillRunResponse
from markwritter.api.services.framework_bridge import get_framework

router = APIRouter(prefix="/skills", tags=["skills"])


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


@router.post(
    "/{skill_name}/run",
    response_model=SkillRunResponse,
    summary="Run a skill",
    description="Execute a skill with the provided parameters",
)
async def run_skill(skill_name: str, request: SkillRunRequest) -> SkillRunResponse:
    """Run a specific skill with parameters.

    Args:
        skill_name: Name of the skill to run
        request: Request containing parameters for the skill

    Returns:
        SkillRunResponse with execution result
    """
    framework = get_framework()
    skill = framework.registry.get(skill_name)

    if skill is None:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    try:
        result = framework.executor.execute_sync(skill, request.params)

        return SkillRunResponse(
            success=result.success,
            output=result.output,
            error=result.error,
        )
    except Exception as e:
        return SkillRunResponse(
            success=False,
            output="",
            error=str(e),
        )
