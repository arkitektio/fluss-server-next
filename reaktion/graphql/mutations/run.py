from kante.types import Info
import strawberry
from reaktion import types, models, inputs
import logging

logger = logging.getLogger(__name__)



def create_run(info: Info, input: inputs.CreateRunInput) -> types.Run:
    run, created = models.Run.objects.update_or_create(
        flow_id=input.flow,
        assignation_id=input.assignation,
        defaults=dict(snapshot_interval=input.snapshot_interval),
    )

    return run


def delete_run(info: Info, input: inputs.DeleteRunInput) -> strawberry.ID:
    run = models.Run.objects.get(id=input.run)
    run.delete()
    return input.run

def snapshot(info: Info, input: inputs.SnapshotRunInput) -> types.RunSnapshot:
    snapshot = models.RunSnapshot.objects.create(
        run_id=input.run,
        t=input.t
    )
    return snapshot


def delete_snapshot(info: Info, input: inputs.DeleteSnapshotInput) -> strawberry.ID:
    snapshot = models.RunSnapshot.objects.get(id=input.snapshot)
    snapshot.delete()
    return input.snapshot


def track(info: Info, input: inputs.TrackInput) -> types.RunEvent:
    event = models.RunEvent.objects.create(
        run_id=input.run,
        t=input.t,
        type=input.type,
        value=input.value,
        caused_by=input.caused_by,
        edge_id=input.edge
    )
    return event