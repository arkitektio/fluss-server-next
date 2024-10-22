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
    ins: list[list[rtypes.Port]]  # Itmes that are streamed in
    outs: list[list[rtypes.Port]]  # Items that are streamed out
    constants: list[rtypes.Port]  # Items that are constants
    voids: list[rtypes.Port]  # Items that are voids
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



class RekuestNodeModel(BaseModel):
    hash: str
    map_strategy: str
    allow_local_execution: bool
    binds: rmodels.BindsModel
    node_kind: str
    


@pydantic.interface(RekuestNodeModel)
class RekuestNode:
    hash: str
    map_strategy: str
    allow_local_execution: bool
    binds: rtypes.Binds
    node_kind: renums.NodeKind





class RekuestMapNodeModel(GraphNodeModel, RetriableNodeModel, AssignableNodeModel, RekuestNodeModel):
    kind: Literal["REKUEST_MAP"]
    hello: str | None = None # This is a fake attribute to test the model
    

class RekuestFilterNodeModel(GraphNodeModel, RetriableNodeModel, AssignableNodeModel, RekuestNodeModel):
    kind: Literal["REKUEST_FILTER"]
    path: str | None = None #This is a fake attribute to test the model



@pydantic.type(RekuestMapNodeModel)
class RekuestMapNode(GraphNode, RetriableNode, AssignableNode, RekuestNode):
    hello: str | None = None


@pydantic.type(RekuestFilterNodeModel)
class RekuestFilterNode(GraphNode, RetriableNode, AssignableNode, RekuestNode):
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


GraphNodeModelUnion = Union[
    RekuestMapNodeModel, ReactiveNodeModel, ArgNodeModel, ReturnNodeModel, RekuestFilterNodeModel
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
    port: rmodels.PortModel


@pydantic.type(GlobalArgModel)
class GlobalArg:
    key: str
    port: rtypes.Port


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
    models.Workspace, filters=filters.WorkspaceFilter, pagination=True, order=filters.WorkspaceOrder
)
class Workspace:
    id: strawberry.ID
    title: str
    description: str | None = None
    created_at: datetime.datetime

    @strawberry_django.field()
    def latest_flow(self, info) -> Optional[Flow]:
        return self.flows.order_by("-created_at").first()


@strawberry_django.type(
    models.ReactiveTemplate, filters=filters.ReactiveTemplateFilter, pagination=True
)
class ReactiveTemplate:
    id: strawberry.ID
    implementation: enums.ReactiveImplementation
    title: str
    description: str | None = None

    @strawberry_django.field()
    def ins(self, info) -> list[list[rtypes.Port]]:
        return [[rmodels.PortModel(**i) for i in stream] for stream in self.ins]

    @strawberry_django.field()
    def outs(self, info) -> list[list[rtypes.Port]]:
        return [[rmodels.PortModel(**i) for i in stream] for stream in self.outs]

    @strawberry_django.field()
    def constants(self, info) -> list[rtypes.Port]:
        return [rmodels.PortModel(**i) for i in self.constants]
    
    @strawberry_django.field()
    def voids(self, info) -> list[rtypes.Port]:
        return []


@strawberry_django.type(models.Run, filters=filters.RunFilter, pagination=True)
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
