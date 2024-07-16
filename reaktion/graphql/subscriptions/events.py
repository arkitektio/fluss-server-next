from kante.types import Info
import strawberry_django
import strawberry
from reaktion import types, models, scalars
from typing import AsyncGenerator
from reaktion.channels import runevent_created_listen


async def events(
    self,
    info: Info,
    run: strawberry.ID,
) -> AsyncGenerator[types.RunEvent, None]:
    """Join and subscribe to message sent to the given rooms."""

    print(info)

    run = await models.Run.objects.aget(id=run)

    print("listening to", [f"run_{run.id}"])

    async for message in runevent_created_listen(info, [f"run_{run.id}"]):
        print("message", message)
        yield await models.RunEvent.objects.aget(id=message)
