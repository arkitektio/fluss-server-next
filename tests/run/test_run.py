"""Run lifecycle executed against the schema.

Covers the full chain: createRun -> track -> snapshot -> closeRun ->
deleteSnapshot -> deleteRun, plus the run/runForAssignation queries.
"""

import pytest

from reaktion.models import Run, RunEvent, Snapshot

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


CREATE_RUN = """
mutation ($input: CreateRunInput!) {
  createRun(input: $input) { id status taskId }
}
"""

CLOSE_RUN = """
mutation ($input: CloseRunInput!) {
  closeRun(input: $input) { id status }
}
"""

DELETE_RUN = """
mutation ($input: DeleteRunInput!) {
  deleteRun(input: $input)
}
"""

TRACK = """
mutation ($input: TrackInput!) {
  track(input: $input) { id kind source }
}
"""

SNAPSHOT = """
mutation ($input: SnapshotRunInput!) {
  snapshot(input: $input) { id t }
}
"""

DELETE_SNAPSHOT = """
mutation ($input: DeleteSnapshotInput!) {
  deleteSnapshot(input: $input)
}
"""

RUN_QUERY = """
query ($id: ID!) {
  run(id: $id) { id status taskId }
}
"""

RUN_FOR_TASK = """
query ($id: ID!) {
  runForTask(id: $id) { id taskId }
}
"""


async def _create_run(aexecute, flow, task_id="task-1"):
    res = await aexecute(
        CREATE_RUN,
        {"input": {"flow": str(flow.id), "taskId": task_id, "snapshotInterval": 5}},
    )
    assert not res.errors, res.errors
    return res.data["createRun"]


async def test_create_run(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow)
    assert run["status"] == "RUNNING"
    assert run["taskId"] == "task-1"
    assert await Run.objects.filter(id=run["id"]).aexists()


async def test_track_event(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow)
    res = await aexecute(
        TRACK,
        {
            "input": {
                "run": run["id"],
                "reference": "ref-1",
                "t": 1,
                "kind": "NEXT",
                "causedBy": [],
                "source": "node-1",
                "handle": "out-0",
            }
        },
    )
    assert not res.errors, res.errors
    assert res.data["track"]["kind"] == "NEXT"
    assert await RunEvent.objects.filter(run_id=run["id"], source="node-1").aexists()


async def test_snapshot_and_delete(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow)
    res = await aexecute(SNAPSHOT, {"input": {"run": run["id"], "events": [], "t": 3}})
    assert not res.errors, res.errors
    snap_id = res.data["snapshot"]["id"]
    assert res.data["snapshot"]["t"] == 3
    assert await Snapshot.objects.filter(id=snap_id).aexists()

    res = await aexecute(DELETE_SNAPSHOT, {"input": {"snapshot": snap_id}})
    assert not res.errors, res.errors
    assert res.data["deleteSnapshot"] == snap_id
    assert not await Snapshot.objects.filter(id=snap_id).aexists()


async def test_close_run(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow)
    res = await aexecute(CLOSE_RUN, {"input": {"run": run["id"]}})
    assert not res.errors, res.errors
    assert res.data["closeRun"]["status"] == "COMPLETED"


async def test_delete_run(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow)
    res = await aexecute(DELETE_RUN, {"input": {"run": run["id"]}})
    assert not res.errors, res.errors
    assert res.data["deleteRun"] == run["id"]
    assert not await Run.objects.filter(id=run["id"]).aexists()


async def test_full_lifecycle(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow, task_id="lifecycle")

    track = await aexecute(
        TRACK,
        {
            "input": {
                "run": run["id"],
                "reference": "ref",
                "t": 0,
                "kind": "NEXT",
                "causedBy": [],
                "source": "node-1",
                "handle": "out-0",
            }
        },
    )
    assert not track.errors, track.errors

    snap = await aexecute(SNAPSHOT, {"input": {"run": run["id"], "events": [], "t": 1}})
    assert not snap.errors, snap.errors

    close = await aexecute(CLOSE_RUN, {"input": {"run": run["id"]}})
    assert not close.errors, close.errors
    assert close.data["closeRun"]["status"] == "COMPLETED"


async def test_run_queries(aexecute, make_flow):
    flow = await make_flow()
    run = await _create_run(aexecute, flow, task_id="queryable")

    by_id = await aexecute(RUN_QUERY, {"id": run["id"]})
    assert not by_id.errors, by_id.errors
    assert by_id.data["run"]["id"] == run["id"]

    by_task = await aexecute(RUN_FOR_TASK, {"id": "queryable"})
    assert not by_task.errors, by_task.errors
    assert by_task.data["runForTask"]["id"] == run["id"]
