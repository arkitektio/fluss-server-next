from kante.types import Info
import strawberry
from reaktion import types, models, inputs, enums
import logging

logger = logging.getLogger(__name__)



def create_run(info: Info, input: inputs.CreateRunInput) -> types.Run:
    run, created = models.Run.objects.update_or_create(
        flow_id=input.flow,
        assignation=input.assignation,
        defaults=dict(snapshot_interval=input.snapshot_interval, status=enums.RunStatus.RUNNING.value),
    )

    return run


def close_run(info: Info, input: inputs.CloseRunInput) -> types.Run:
    run = models.Run.objects.get(id=input.run)
    run.status = enums.RunStatus.COMPLETED.value

    return run


def delete_run(info: Info, input: inputs.DeleteRunInput) -> strawberry.ID:
    run = models.Run.objects.get(id=input.run)
    run.delete()
    return input.run

def snapshot(info: Info, input: inputs.SnapshotRunInput) -> types.Snapshot:
    snapshot = models.Snapshot.objects.create(
        run_id=input.run,
        t=input.t
    )
    return snapshot


def delete_snapshot(info: Info, input: inputs.DeleteSnapshotInput) -> strawberry.ID:
    snapshot = models.Snapshot.objects.get(id=input.snapshot)
    snapshot.delete()
    return input.snapshot


def track(info: Info, input: inputs.TrackInput) -> types.RunEvent:
    event = models.RunEvent.objects.create(
        reference=input.reference,
        run_id=input.run,
        t=input.t,
        kind=input.kind,
        value=input.value,
        caused_by=input.caused_by,
        source=input.source,
        handle=input.handle

    )
    return event