from kante.types import Info

from reaktion import models, types
import strawberry

def reactive_template(info: Info, id: strawberry.ID) -> types.ReactiveTemplate:
    return models.ReactiveTemplate.objects.get(id=id)
