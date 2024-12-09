import strawberry
from kante.types import Info
from reaktion import models, types


def events_between(
    info: Info, run: strawberry.ID, min: int | None = None, max: int | None = None
) -> list[types.RunEvent]:
    if min is None:
        min = 0

    snapshot = (
        models.Snapshot.objects.filter(run_id=run, t__lte=min).order_by("-t").first()
    )

    if snapshot:
        min = snapshot.t
        start_events = list(snapshot.events.all())
    else:
        start_events = []

    events = models.RunEvent.objects.filter(run_id=run, t__gte=min)

    if max:
        events = events.filter(t__lte=max)

    events = events.order_by("t").all()

    return start_events + list(events)
