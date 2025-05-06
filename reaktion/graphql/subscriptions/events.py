from kante.types import Info
import strawberry_django
import strawberry
from reaktion import types, models, scalars, channel_signals, channels
from typing import AsyncGenerator


async def events(
    self,
    info: Info,
    run: strawberry.ID,
) -> AsyncGenerator[types.RunEvent, None]:
    """Join and subscribe to message sent to the given rooms."""


    run = await models.Run.objects.aget(id=run)


    async for message in channels.run_event_channel.listen(info.context, [f"run_{run.id}"]):
        print("message", message)
        yield await models.RunEvent.objects.aget(id=message.event)
