from dataclasses import Field
import strawberry_django
from reaktion import models, scalars, enums, filters
import strawberry
from typing import Optional
from pydantic import BaseModel
from strawberry.experimental import pydantic
from typing import Any, Dict
from typing import Literal, Union
import datetime
from rekuest_core.objects import types as rtypes
from rekuest_core.objects import models as rmodels
from rekuest_core import enums as renums
from strawberry import LazyType
from .type_gen import create_stats_type


def build_prescoped_queryset(info, queryset, field="organization"):
    print(info)
    if info.variable_values.get("filters", {}).get("scope") is None:
        queryset = queryset.filter(**{field: info.context.request.organization})
        return queryset

    else:
        raise Exception("Custom scopes not implemented yet")


def build_prescoper(field="organization"):
    def prescoper(queryset, info):
        return build_prescoped_queryset(info, queryset, field=field)

    return prescoper


class PositionModel(BaseModel):
    x: float
    y: float


@pydantic.type(PositionModel)
class Position:
    x: float
    y: float


class GraphNodeModel(BaseModel):
    kind: enums.GraphNodeKind
    id: str
    position: PositionModel
    parent_node: str | None = None
    ins: list[list[rmodels.PortModel]]  # A set of streams
    outs: list[list[rmodels.PortModel]]
    constants: list[rmodels.PortModel]
    voids: list[rmodels.PortModel]
    constants_map: Dict[str, Any]
    globals_map: Dict[str, Any]
    description: str
    title: str


@pydantic.interface(GraphNodeModel)
class GraphNode:
    id: strawberry.ID
    kind: enums.GraphNodeKind
    position: Position
    parent_node: str | None = None
    ins: list[list[rtypes.ArgPort]]  # Itmes that are streamed in
    outs: list[list[rtypes.ReturnPort]]  # Items that are streamed out
    constants: list[rtypes.ArgPort]  # Items that are constants
    voids: list[rtypes.ArgPort]  # Items that are voids
    constants_map: scalars.ValueMap
    globals_map: scalars.ValueMap
    description: str = "No description"
    title: str


class RetriableNodeModel(BaseModel):
    retries: int
    retry_delay: int


@pydantic.interface(RetriableNodeModel)
class RetriableNode:
    retries: int | None
    retry_delay: int | None


class AssignableNodeModel(BaseModel):
    next_timeout: int | None


@pydantic.interface(AssignableNodeModel)
class AssignableNode:
    next_timeout: int | None


class RekuestActionNodeModel(BaseModel):
    hash: str
    map_strategy: str
    allow_local_execution: bool
    action_kind: str


@pydantic.interface(RekuestActionNodeModel)
class RekuestActionNode:
    hash: str
    map_strategy: str
    allow_local_execution: bool
    action_kind: renums.ActionKind


class RekuestMapActionNodeModel(GraphNodeModel, RetriableNodeModel, AssignableNodeModel, RekuestActionNodeModel):
    kind: Literal["REKUEST_MAP"]
    hello: str | None = None  # This is a fake attribute to test the model


class RekuestFilterActionNodeModel(GraphNodeModel, RetriableNodeModel, AssignableNodeModel, RekuestActionNodeModel):
    kind: Literal["REKUEST_FILTER"]
    path: str | None = None  # This is a fake attribute to test the model


@pydantic.type(RekuestMapActionNodeModel)
class RekuestMapActionNode(GraphNode, RetriableNode, AssignableNode, RekuestActionNode):
    hello: str | None = None


@pydantic.type(RekuestFilterActionNodeModel)
class RekuestFilterActionNode(GraphNode, RetriableNode, AssignableNode, RekuestActionNode):
    path: str | None = None


class ArgNodeModel(GraphNodeModel):
    kind: Literal["ARGS"]
    arg_stuff: str | None = None


@pydantic.type(ArgNodeModel)
class ArgNode(GraphNode):
    arg_stuff: str | None = None


class ReactiveNodeModel(GraphNodeModel):
    kind: Literal["REACTIVE"]
    implementation: enums.ReactiveImplementation


@pydantic.type(ReactiveNodeModel)
class ReactiveNode(GraphNode):
    arg_stuff: str | None = None
    implementation: enums.ReactiveImplementation


class ReturnNodeModel(GraphNodeModel):
    kind: Literal["RETURNS"]
    return_stuff: str | None = None


@pydantic.type(ReturnNodeModel)
class ReturnNode(GraphNode):
    return_stuff: str | None = None


class AgentSubFlowNodeModel(GraphNodeModel):
    kind: Literal["AGENT_SUBFLOW"]
    app_filter: str | None = None
    version_filter: str | None = None
    device_filter: str | None = None
    instance_filter: str | None = None
    user_filter: str | None = None
    auto_resolvable: bool = False


@pydantic.type(AgentSubFlowNodeModel)
class AgentSubFlowNode(GraphNode):
    app_filter: str | None = None
    version_filter: str | None = None
    device_filter: str | None = None
    instance_filter: str | None = None
    user_filter: str | None = None
    auto_resolvable: bool = strawberry.field(
        default=False,
        description="Whether this dependency is auto resolvable or not. If so we will try to automatically resolve it based on the demands specified in the dependency and the capabilities of the available agents in the system. This is used to identify the demand in the system. Attention if any of the dependencies of this agent dependency is not auto resolvable, this dependency will also not be auto resolvable",
    )


GraphNodeModelUnion = Union[
    RekuestMapActionNodeModel,
    ReactiveNodeModel,
    ArgNodeModel,
    ReturnNodeModel,
    RekuestFilterActionNodeModel,
    AgentSubFlowNodeModel,
]


class StreamItemModel(BaseModel):
    kind: str
    label: str | None = None


@pydantic.type(StreamItemModel)
class StreamItem:
    kind: renums.PortKind
    label: str


class GraphEdgeModel(BaseModel):
    kind: str
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str
    stream: list[StreamItemModel]


@pydantic.interface(GraphEdgeModel)
class GraphEdge:
    stream: list[StreamItem]
    id: strawberry.ID
    kind: enums.GraphEdgeKind
    source: str
    target: str
    source_handle: str
    target_handle: str


class VanillaEdgeModel(GraphEdgeModel):
    kind: Literal["VANILLA"]
    label: str | None = None


class LoggingEdgeModel(GraphEdgeModel):
    kind: Literal["LOGGING"]
    level: str


@pydantic.type(VanillaEdgeModel)
class VanillaEdge(GraphEdge):
    label: str | None = None


@pydantic.type(LoggingEdgeModel)
class LoggingEdge(GraphEdge):
    level: str


StreamEdgeModelUnion = Union[VanillaEdgeModel, LoggingEdgeModel]


class GlobalArgModel(BaseModel):
    key: str
    port: rmodels.ArgPortModel


@pydantic.type(GlobalArgModel)
class GlobalArg:
    key: str
    port: rtypes.ArgPort


class GraphModel(BaseModel):
    zoom: str | None = None
    nodes: list[GraphNodeModelUnion]
    edges: list[StreamEdgeModelUnion]
    globals: list[GlobalArgModel]


@pydantic.type(GraphModel)
class Graph:
    zoom: float
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    globals: list[GlobalArg]


@strawberry_django.type(models.Flow, filters=filters.FlowFilter, pagination=True)
class Flow:
    id: strawberry.ID
    title: str
    description: str | None = None
    created_at: datetime.datetime
    workspace: "Workspace"
    hash: str

    @strawberry_django.field()
    def graph(self, info) -> Graph:
        print(GraphModel(**self.graph))

        return GraphModel(**self.graph)


@strawberry_django.type(
    models.Workspace,
    filters=filters.WorkspaceFilter,
    pagination=True,
    order=filters.WorkspaceOrder,
)
class Workspace:
    id: strawberry.ID
    title: str
    description: str | None = None
    created_at: datetime.datetime
    flows: list["Flow"]

    @strawberry_django.field()
    def latest_flow(self, info) -> Optional[Flow]:
        return self.flows.order_by("-created_at").first()


WorkspaceStats, WorkspaceStatsResolver = create_stats_type(
    model=models.Workspace,
    filters=filters.WorkspaceFilter,
    allowed_fields={
        "created_at": "created_at",
    },
    allowed_datetime_fields={"created_at": "created_at"},
    prescope=build_prescoper(field="organization"),
)


@strawberry_django.type(models.ReactiveTemplate, filters=filters.ReactiveTemplateFilter, pagination=True)
class ReactiveTemplate:
    id: strawberry.ID
    implementation: enums.ReactiveImplementation
    title: str
    description: str | None = None

    @strawberry_django.field()
    def ins(self, info) -> list[list[rtypes.ArgPort]]:
        return [[rmodels.ArgPortModel(**i) for i in stream] for stream in self.ins]

    @strawberry_django.field()
    def outs(self, info) -> list[list[rtypes.ReturnPort]]:
        return [[rmodels.ReturnPortModel(**i) for i in stream] for stream in self.outs]

    @strawberry_django.field()
    def constants(self, info) -> list[rtypes.ArgPort]:
        return [rmodels.ArgPortModel(**i) for i in self.constants]

    @strawberry_django.field()
    def voids(self, info) -> list[rtypes.ArgPort]:
        return []


@strawberry_django.type(models.Run, filters=filters.RunFilter, order=filters.RunOrder, pagination=True)
class Run:
    id: strawberry.ID
    created_at: datetime.datetime
    events: list["RunEvent"]
    flow: "Flow"
    assignation: strawberry.ID
    snapshots: list["Snapshot"]
    status: enums.RunStatus

    @strawberry_django.field()
    def latest_snapshot(self, info) -> Optional["Snapshot"]:
        return self.snapshots.order_by("-created_at").first()


@strawberry_django.type(models.Snapshot, pagination=True)
class Snapshot:
    t: int
    run: "Run"
    events: list["RunEvent"]
    id: strawberry.ID
    status: str | None = None
    created_at: datetime.datetime


@strawberry_django.type(models.RunEvent, pagination=True)
class RunEvent:
    id: strawberry.ID
    t: int
    caused_by: list[strawberry.ID]
    value: scalars.EventValue | None = None
    exception: str | None = None
    kind: enums.RunEventKind
    handle: str
    source: str
    created_at: datetime.datetime


@strawberry_django.type(models.Trace, pagination=True)
class Trace:
    id: strawberry.ID


@strawberry_django.type(models.TraceSnapshot, pagination=True)
class TraceSnapshot:
    id: strawberry.ID


@strawberry_django.type(models.TraceEvent, pagination=True)
class TraceEvent:
    id: strawberry.ID
