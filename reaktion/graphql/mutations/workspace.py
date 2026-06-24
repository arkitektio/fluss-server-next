from kante.types import Info
import strawberry
from reaktion import types, models, inputs
from reaktion.scoping import get_for_org
import logging
from reaktion.hashers import hash_graph
import namegenerator

logger = logging.getLogger(__name__)


@strawberry.input
class UpdateWorkspaceInput:
    workspace: strawberry.ID
    graph: inputs.GraphInput
    title: str | None = None
    description: str | None = None


def update_workspace(info: Info, input: UpdateWorkspaceInput) -> types.Workspace:
    # Scope to the request's organization: only own workspaces can be updated
    # (raises DoesNotExist for a cross-org / unknown workspace).
    workspace = get_for_org(models.Workspace, info, id=input.workspace)

    graph = strawberry.asdict(input.graph)

    flow, _ = models.Flow.objects.get_or_create(
        workspace=workspace,
        hash=hash_graph(graph),
        defaults=dict(
            title=input.title or namegenerator.gen(),
            description=input.description or "No description",
            creator=info.context.request.user,
            graph=graph,
            organization=info.context.request.organization
        ),
    )

    if input.title:
        flow.title = input.title
    if input.description:
        flow.description = input.description

    flow.save()

    return workspace


@strawberry.input
class CreateWorkspaceInput:
    graph: inputs.GraphInput | None = None
    title: str | None = None
    description: str | None = None
    vanilla: bool = False


def create_workspace(info: Info, input: CreateWorkspaceInput) -> types.Workspace:
    title = input.title or namegenerator.gen()
    workspace = models.Workspace.objects.create(
        title=title,
        description=input.description,
        creator=info.context.request.user,
        organization=info.context.request.organization
    )

    nodes = [
        {
            "id": "1",
            "kind": "ARGS",
            "ins": [[]],
            "outs": [[]],
            "cons": [],
            "voids": [],
            "position": {"x": 0, "y": 50},
            "constants": [],
            "constants_map": {},
            "globals_map": {},
            "title": "Input",
            "description": "The input to the workflow",
        },
        {
            "id": "2",
            "kind": "RETURNS",
            "ins": [[]],
            "outs": [[]],
            "cons": [],
            "voids": [],
            "position": {"x": 1500, "y": 50},
            "constants": [],
            "constants_map": {},
            "globals_map": {},
            "title": "Output",
            "description": "The output to the workflow",
        },
    ]

    graph = {
        "nodes": nodes,
        "edges": [],
        "globals": [],
    }

    models.Flow.objects.create(
        workspace=workspace,
        graph=graph,
        hash=hash_graph(graph),
        title=title,
        description=input.description,
        creator=info.context.request.user,
        organization=info.context.request.organization
    )

    return workspace
