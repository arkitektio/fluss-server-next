"""Workspace mutations executed against the schema: createWorkspace + updateWorkspace."""

import pytest

from reaktion.models import Flow, Workspace

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


CREATE_WORKSPACE = """
mutation ($input: CreateWorkspaceInput!) {
  createWorkspace(input: $input) { id title }
}
"""

UPDATE_WORKSPACE = """
mutation ($input: UpdateWorkspaceInput!) {
  updateWorkspace(input: $input) { id title }
}
"""

EMPTY_GRAPH = {"nodes": [], "edges": [], "globals": []}


async def test_create_workspace(aexecute):
    res = await aexecute(CREATE_WORKSPACE, {"input": {"title": "My Workspace"}})
    assert not res.errors, res.errors
    assert res.data["createWorkspace"]["title"] == "My Workspace"
    # createWorkspace also mints an initial flow.
    ws_id = res.data["createWorkspace"]["id"]
    assert await Workspace.objects.filter(id=ws_id).aexists()
    assert await Flow.objects.filter(workspace_id=ws_id).aexists()


async def test_create_workspace_autonames_when_title_missing(aexecute):
    res = await aexecute(CREATE_WORKSPACE, {"input": {}})
    assert not res.errors, res.errors
    assert res.data["createWorkspace"]["title"]  # namegenerator default


async def test_update_workspace(aexecute, make_workspace):
    ws = await make_workspace(title="Before")
    res = await aexecute(
        UPDATE_WORKSPACE,
        {"input": {"workspace": str(ws.id), "graph": EMPTY_GRAPH, "title": "After"}},
    )
    assert not res.errors, res.errors
    assert res.data["updateWorkspace"]["id"] == str(ws.id)
    # updateWorkspace upserts a Flow for the posted graph under the workspace.
    assert await Flow.objects.filter(workspace_id=ws.id, title="After").aexists()


async def test_create_workspace_stamps_organization(aexecute, authenticated_context):
    res = await aexecute(CREATE_WORKSPACE, {"input": {"title": "Org Stamped"}})
    assert not res.errors, res.errors
    ws = await Workspace.objects.aget(id=res.data["createWorkspace"]["id"])
    assert ws.organization_id == authenticated_context.request.organization.id
    assert ws.creator_id == authenticated_context.request.user.id
