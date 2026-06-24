import strawberry
from strawberry_django.optimizer import DjangoOptimizerExtension
from reaktion import types, models
from reaktion.graphql import mutations
from reaktion.graphql import subscriptions
from reaktion.graphql import queries
import strawberry_django
from koherent.strawberry.extension import KoherentExtension
from authentikate.strawberry.extension import AuthentikateExtension
from strawberry.schema.config import StrawberryConfig
from kante.types import Info
from typing import List
from rekuest_core.constants import interface_types
from rekuest_core.scalars import scalar_map as rekuest_scalar_map
from reaktion.scoping import get_for_org


@strawberry.type
class Query:
    """The root query type"""

    flows: list[types.Flow] = strawberry_django.field()
    runs: list[types.Run] = strawberry_django.field()
    snapshots: list[types.Snapshot] = strawberry_django.field()
    workspaces: list[types.Workspace] = strawberry_django.field()
    workspace = strawberry_django.field(resolver=queries.workspace)
    reactive_templates: list[types.ReactiveTemplate] = strawberry_django.field()
    reactive_template = strawberry_django.field(resolver=queries.reactive_template)
    events_between = strawberry_django.field(resolver=queries.events_between)

    # Stats
    workspace_stats: types.WorkspaceStats = strawberry.field(resolver=types.WorkspaceStatsResolver)

    @strawberry_django.field
    def run(self, info: Info, id: strawberry.ID) -> types.Run:
        return models.Run.objects.get(id=id, flow__organization=info.context.request.organization)

    @strawberry_django.field
    def run_for_assignation(self, info: Info, id: strawberry.ID) -> types.Run:
        return models.Run.objects.get(assignation=id, flow__organization=info.context.request.organization)

    @strawberry_django.field
    def flow(self, info: Info, id: strawberry.ID) -> types.Flow:
        return get_for_org(models.Flow, info, id=id)

    @strawberry_django.field
    def snapshot(self, info: Info, id: strawberry.ID) -> types.Snapshot:
        return models.Snapshot.objects.get(id=id, run__flow__organization=info.context.request.organization)


@strawberry.type
class Mutation:
    """The root mutation type"""

    update_workspace = strawberry_django.mutation(resolver=mutations.update_workspace)
    create_workspace = strawberry_django.mutation(
        resolver=mutations.create_workspace,
    )
    create_run = strawberry_django.mutation(resolver=mutations.create_run)
    close_run = strawberry_django.mutation(resolver=mutations.close_run)
    delete_run = strawberry_django.mutation(resolver=mutations.delete_run)
    snapshot = strawberry_django.mutation(resolver=mutations.snapshot)
    delete_snapshot = strawberry_django.mutation(resolver=mutations.delete_snapshot)
    track = strawberry_django.mutation(resolver=mutations.track)


@strawberry.type
class Subscription:
    """The root subscription type"""

    events = strawberry.subscription(resolver=subscriptions.events)


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[DjangoOptimizerExtension, KoherentExtension, AuthentikateExtension],
    config=StrawberryConfig(scalar_map=rekuest_scalar_map),
    types=[
        types.RekuestFilterActionNode,
        types.RekuestMapActionNode,
        types.RetriableNode,
        types.ArgNode,
        types.ReturnNode,
        types.VanillaEdge,
        types.LoggingEdge,
        types.ReactiveNode,
        types.AgentSubFlowNode,
    ]
    + interface_types,
)
