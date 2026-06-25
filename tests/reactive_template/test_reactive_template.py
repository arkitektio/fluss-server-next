"""ReactiveTemplate queries executed against the schema."""

import pytest

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


TEMPLATE_QUERY = """
query ($id: ID!) {
  reactiveTemplate(id: $id) { id title implementation ins { key } constants { key } }
}
"""

TEMPLATES_QUERY = """
query {
  reactiveTemplates { id title implementation }
}
"""


async def test_reactive_template_query(aexecute, make_reactive_template):
    tpl = await make_reactive_template(title="Zip", description="zips streams")
    res = await aexecute(TEMPLATE_QUERY, {"id": str(tpl.id)})
    assert not res.errors, res.errors
    assert res.data["reactiveTemplate"]["id"] == str(tpl.id)
    assert res.data["reactiveTemplate"]["implementation"] == "ZIP"
    # ins/outs/constants resolvers iterate the JSON columns (empty by default).
    assert res.data["reactiveTemplate"]["ins"] == []
    assert res.data["reactiveTemplate"]["constants"] == []


async def test_reactive_templates_list(aexecute, make_reactive_template):
    tpl = await make_reactive_template()
    res = await aexecute(TEMPLATES_QUERY)
    assert not res.errors, res.errors
    ids = [t["id"] for t in res.data["reactiveTemplates"]]
    assert str(tpl.id) in ids
