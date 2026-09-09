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


def _node(node_id: str, kind: str, ins: list, outs: list) -> dict:
    return {"id": node_id, "kind": kind, "position": {"x": 0, "y": 0}, "ins": ins, "outs": outs, "constants": [], "voids": [], "constantsMap": {}, "globalsMap": {}}


async def test_update_workspace_rejects_a_malformed_port(aexecute, make_workspace):
    """A LIST port without its item child is rejected by the graph validation, not stored."""
    ws = await make_workspace(title="Strict")
    bad = {"nodes": [_node("1", "ARGS", [[]], [[{"key": "xs", "kind": "LIST", "nullable": False}]])], "edges": [], "globals": []}
    res = await aexecute(UPDATE_WORKSPACE, {"input": {"workspace": str(ws.id), "graph": bad}})
    assert res.errors and "exactly one child" in res.errors[0].message
    assert not await Flow.objects.filter(workspace_id=ws.id, title="Untitled Workspace").aexists()


async def test_update_workspace_round_trips_a_valid_graph(aexecute, make_workspace):
    """A valid graph is normalised, stored and read back through the flow's typed graph."""
    ws = await make_workspace(title="Round trip")
    out_port = {"key": "xs", "kind": "LIST", "nullable": False, "children": [{"key": "...", "kind": "STRUCTURE", "identifier": "@mikro/image", "nullable": False}]}
    graph = {"nodes": [_node("1", "ARGS", [[]], [[out_port]]), _node("2", "RETURNS", [[]], [[]])], "edges": [], "globals": []}
    res = await aexecute(UPDATE_WORKSPACE, {"input": {"workspace": str(ws.id), "graph": graph, "title": "Typed"}})
    assert not res.errors, res.errors

    flow = await Flow.objects.aget(workspace_id=ws.id, title="Typed")
    node = flow.graph["nodes"][0]
    assert node["outs"][0][0]["children"][0]["identifier"] == "@mikro/image"
    assert node["title"] is None  # optional on both write and read

    read = await aexecute("query($id: ID!) { flow(id: $id) { graph { nodes { id kind outs { key kind children { key identifier } } } } } }", {"id": str(flow.id)})
    assert not read.errors, read.errors
    assert read.data["flow"]["graph"]["nodes"][0]["outs"][0][0]["children"][0]["identifier"] == "@mikro/image"
