
import strawberry
from kante.types import Info
from reaktion import models, types


def workspace(info: Info, id: strawberry.ID) -> types.Workspace:
    return models.Workspace.objects.get(id=id)
