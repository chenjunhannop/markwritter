"""Explore API routes.

Provides endpoints for knowledge graph functionality.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from markwritter.explore.graph import (
    InvalidVaultError,
    KnowledgeGraph,
    NodeNotFoundError,
)

router = APIRouter()

# Global vault path - will be set by app initialization
_vault_path: str | None = None


def set_vault_path(path: str) -> None:
    """Set the vault path for explore endpoints."""
    global _vault_path
    _vault_path = path


def get_knowledge_graph() -> KnowledgeGraph:
    """Get KnowledgeGraph instance with configured vault.

    Raises:
        HTTPException: If vault is not configured
    """
    if _vault_path is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not configured",
        )
    try:
        return KnowledgeGraph(_vault_path)
    except InvalidVaultError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


# ==============================================================================
# Response Models
# ==============================================================================


class GraphNodeResponse(BaseModel):
    """Response model for a graph node."""

    id: str
    title: str
    path: str
    tags: list[str] = Field(default_factory=list)
    connections_count: int = 0


class GraphEdgeResponse(BaseModel):
    """Response model for a graph edge."""

    source: str
    target: str
    type: str = "wikilink"
    weight: float = 1.0


class GraphDataResponse(BaseModel):
    """Response model for full graph data."""

    nodes: list[GraphNodeResponse] = Field(default_factory=list)
    edges: list[GraphEdgeResponse] = Field(default_factory=list)


class NodeGraphResponse(BaseModel):
    """Response model for single node graph data."""

    node: GraphNodeResponse
    edges: list[GraphEdgeResponse] = Field(default_factory=list)


class RelatedNoteResponse(BaseModel):
    """Response model for a related note."""

    path: str
    title: str | None = None
    tags: list[str] = Field(default_factory=list)


# ==============================================================================
# Endpoints
# ==============================================================================


@router.get(
    "/graph",
    response_model=GraphDataResponse,
    summary="Get full knowledge graph",
    description="Retrieve the complete knowledge graph with all nodes and edges",
)
async def get_full_graph() -> GraphDataResponse:
    """Get the complete knowledge graph.

    Returns:
        GraphDataResponse with all nodes and edges
    """
    kg = get_knowledge_graph()
    graph = kg.build_graph()

    return GraphDataResponse(
        nodes=[
            GraphNodeResponse(
                id=n.id,
                title=n.title,
                path=n.path,
                tags=n.tags,
                connections_count=n.connections_count,
            )
            for n in graph.nodes
        ],
        edges=[
            GraphEdgeResponse(
                source=e.source,
                target=e.target,
                type=e.type,
                weight=e.weight,
            )
            for e in graph.edges
        ],
    )


@router.get(
    "/graph/{note_path:path}",
    response_model=NodeGraphResponse,
    summary="Get node graph data",
    description="Get graph data for a specific note including its connections",
)
async def get_node_graph(note_path: str) -> NodeGraphResponse:
    """Get graph data for a specific note.

    Args:
        note_path: Relative path to the note

    Returns:
        NodeGraphResponse with node and its edges

    Raises:
        HTTPException: If note not found
    """
    kg = get_knowledge_graph()

    try:
        node = kg.get_node(note_path)
    except NodeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {note_path}",
        )

    # Get edges (both outgoing and incoming)
    graph = kg.build_graph()
    edges = [e for e in graph.edges if e.source == note_path or e.target == note_path]

    return NodeGraphResponse(
        node=GraphNodeResponse(
            id=node.id,
            title=node.title,
            path=node.path,
            tags=node.tags,
            connections_count=node.connections_count,
        ),
        edges=[
            GraphEdgeResponse(
                source=e.source,
                target=e.target,
                type=e.type,
                weight=e.weight,
            )
            for e in edges
        ],
    )


@router.get(
    "/related/{note_path:path}",
    response_model=list[RelatedNoteResponse],
    summary="Get related notes",
    description="Find notes related to the specified note within given depth",
)
async def get_related_notes(
    note_path: str,
    depth: int = Query(
        default=1,
        ge=1,
        le=10,
        description="Traversal depth (1 = direct connections)",
    ),
) -> list[RelatedNoteResponse]:
    """Find notes related to the specified note.

    Args:
        note_path: Relative path to the note
        depth: Maximum traversal depth (1-10)

    Returns:
        List of related notes

    Raises:
        HTTPException: If note not found
    """
    kg = get_knowledge_graph()

    try:
        related = kg.find_related_notes(note_path, depth)
    except NodeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {note_path}",
        )

    return [
        RelatedNoteResponse(
            path=note.path,
            title=note.title,
            tags=note.tags,
        )
        for note in related
    ]
