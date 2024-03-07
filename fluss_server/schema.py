import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension
from kante.directives import upper, replace, relation
from reaktion import types
from reaktion.graphql import mutations
from reaktion.graphql import subscriptions
from reaktion.graphql import queries
import strawberry_django
from koherent.strawberry.extension import KoherentExtension
from typing import List
from rekuest_core.constants import interface_types
from authentikate.strawberry.permissions import IsAuthenticated

@strawberry.type
class Query:
    """The root query type"""

    
    flow = strawberry_django.field(resolver=queries.flow)
    flows: list[types.Flow] = strawberry_django.field()
    workspaces: list[types.Workspace] = strawberry_django.field()
    workspace = strawberry_django.field(resolver=queries.workspace)
    reactive_templates: list[
        types.ReactiveTemplate
    ] = strawberry_django.field()
    reactive_template = strawberry_django.field(
        resolver=queries.reactive_template
    )


@strawberry.type
class Mutation:
    """The root mutation type"""

    
    update_workspace = strawberry_django.mutation(
        resolver=mutations.update_workspace
    )
    create_workspace = strawberry_django.mutation(
        permission_classes=[IsAuthenticated],
        resolver=mutations.create_workspace,
    )



@strawberry.type
class Subscription:
    """The root subscription type"""
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    directives=[upper, replace, relation],
    extensions=[DjangoOptimizerExtension, KoherentExtension],
    types=[
        types.ArkitektGraphNode,
        types.ArkitektFilterGraphNode,
        types.RetriableNode,
        types.ArgNode,
        types.ReturnNode,
        types.VanillaEdge,
        types.LoggingEdge,
        types.ReactiveNode,] + interface_types,
)
