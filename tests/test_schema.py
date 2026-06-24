"""Schema smoke tests: the schema must build and expose the core mutations
and queries. No database required."""

from fluss_server.schema import schema


def test_schema_builds():
    sdl = schema.as_str()
    assert sdl


def test_core_mutations_exposed():
    sdl = schema.as_str()
    for field in [
        "createWorkspace",
        "updateWorkspace",
        "createRun",
        "closeRun",
        "deleteRun",
        "snapshot",
        "deleteSnapshot",
        "track",
    ]:
        assert f"{field}(" in sdl, f"{field} missing from schema"


def test_core_queries_exposed():
    sdl = schema.as_str()
    for field in ["flow(", "run(", "workspace(", "reactiveTemplate(", "snapshot("]:
        assert field in sdl, f"{field} missing from schema"
