"""Flow queries executed against the schema."""

import pytest

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


FLOW_QUERY = """
query ($id: ID!) {
  flow(id: $id) { id title hash }
}
"""

FLOWS_QUERY = """
query {
  flows { id title }
}
"""


async def test_flow_query(aexecute, make_flow):
    flow = await make_flow(title="My Flow")
    res = await aexecute(FLOW_QUERY, {"id": str(flow.id)})
    assert not res.errors, res.errors
    assert res.data["flow"]["id"] == str(flow.id)
    assert res.data["flow"]["title"] == "My Flow"


async def test_flows_list(aexecute, make_flow):
    flow = await make_flow(title="Listed Flow")
    res = await aexecute(FLOWS_QUERY)
    assert not res.errors, res.errors
    ids = [f["id"] for f in res.data["flows"]]
    assert str(flow.id) in ids


async def test_flow_query_not_found(aexecute):
    res = await aexecute(FLOW_QUERY, {"id": "999999"})
    assert res.errors
