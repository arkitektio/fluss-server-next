
from strawberry.experimental import pydantic
from pydantic import BaseModel, Field
from rekuest_core.inputs import models as rimodels
from rekuest_core.inputs import types as ritypes
from rekuest_core import enums as renums
from reaktion import scalars, enums
from typing import Any, Dict, Optional
from strawberry import LazyType
import strawberry

class PositionInputModel(BaseModel):
    x: float
    y: float


@pydantic.input(PositionInputModel)
class PositionInput:
    x: float
    y: float


class GraphNodeInputModel(BaseModel):
    id: str
    kind: enums.GraphNodeKind
    position: PositionInput
    parent_node: str | None = None
    ins: list[list[rimodels.PortInputModel]]  # A set of streams
    outs: list[list[rimodels.PortInputModel]]
    constants: list[rimodels.PortInputModel]
    voids: list[rimodels.PortInputModel]
    constants_map: Dict[str, Any]
    globals_map: Dict[str, Any]
    description: str | None = None
    title: str | None = None
    retries: int | None = None
    retry_delay: int | None = None
    node_kind: renums.NodeKind | None = None
    next_timeout: int | None = None
    hash: str | None = None
    map_strategy: enums.MapStrategy | None = None
    allow_local_execution: bool | None = None
    binds: rimodels.BindsInputModel | None = None
    implementation: enums.ReactiveImplementation | None = None


@pydantic.input(GraphNodeInputModel)
class GraphNodeInput:
    id: str
    kind: enums.GraphNodeKind
    position: PositionInput
    parent_node: str | None = None
    ins: list[list[ritypes.PortInput]]  # A set of streams
    outs: list[list[ritypes.PortInput]]
    constants: list[ritypes.PortInput]
    voids: list[ritypes.PortInput]
    constants_map: scalars.ValueMap
    globals_map: scalars.ValueMap
    description: str | None = None
    title: str | None = None
    retries: int | None = None
    retry_delay: int | None = None
    node_kind: renums.NodeKind | None = None
    next_timeout: int | None = None
    hash: str | None = None
    map_strategy: enums.MapStrategy | None = None
    allow_local_execution: bool | None = None
    binds: ritypes.BindsInput | None = None
    parent_node: str | None = None
    implementation: enums.ReactiveImplementation | None = None
    # Placeholder for the node kind
    hello: str | None = None
    path: str | None = None


class StreamItemInputModel(BaseModel):
    kind: str
    label: str | None = None


@pydantic.input(StreamItemInputModel)
class StreamItemInput:
    kind: renums.PortKind
    label: str


class GraphEdgeInputModel(BaseModel):
    kind: str
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str
    stream: list[StreamItemInputModel]


@pydantic.input(GraphEdgeInputModel)
class GraphEdgeInput:
    kind: enums.GraphEdgeKind
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str
    stream: list[StreamItemInput]
    label: str | None = None
    level: str | None = None


class GlobalArgInputModel(BaseModel):
    key: str
    port: rimodels.PortInputModel


@pydantic.input(GlobalArgInputModel)
class GlobalArgInput:
    key: str
    port: ritypes.PortInput


class GraphInputModel(BaseModel):
    nodes: list[GraphNodeInputModel]
    edges: list[GraphEdgeInputModel]
    globals: list[GlobalArgInputModel]


@pydantic.input(GraphInputModel)
class GraphInput:
    nodes: list[GraphNodeInput]
    edges: list[GraphEdgeInput]
    globals: list[GlobalArgInput]


class ReactiveTemplateInputModel(BaseModel):
    title: str
    description: str
    ins: list[list[rimodels.PortInputModel]]  # A set of streams
    outs: list[list[rimodels.PortInputModel]]
    constants: list[rimodels.PortInputModel]
    implementation: enums.ReactiveImplementation

    class Config:
        use_enum_values = True


@pydantic.input(ReactiveTemplateInputModel, all_fields=True)
class ReactiveTemplateInput:
    pass


@strawberry.input
class PortMatchInput:
    at: int | None = None
    key: str | None  = None
    kind: renums.PortKind | None  = None
    identifier: str | None  = None
    nullable: bool | None  = None
    variants: Optional[list[LazyType["PortDemandInput", __name__]]]  = None
    child: Optional[LazyType["PortDemandInput", __name__]]  = None
 


@strawberry.input
class PortDemandInput:
    kind: enums.DemandKind
    matches: list[PortMatchInput] | None = None
    force_length: int | None = None
    force_non_nullable_length: int | None = None




class CreateRunInputModel(BaseModel):
    flow: str
    snapshot_interval: int
    assignation: str 


@pydantic.input(CreateRunInputModel)
class CreateRunInput:
    assignation: strawberry.ID
    flow: strawberry.ID
    snapshot_interval: int


class DeteteRunInputModel(BaseModel):
    run: str

@pydantic.input(DeteteRunInputModel)
class DeleteRunInput:
    run: strawberry.ID


class SnapshotRunInputModel(BaseModel):
    run: str
    events: list[str]
    t : int


@pydantic.input(SnapshotRunInputModel)
class SnapshotRunInput:
    run: strawberry.ID
    events: list[strawberry.ID]
    t : int


class DeleteSnapshotInputModel(BaseModel):
    snapshot: str

@pydantic.input(DeleteSnapshotInputModel)
class DeleteSnapshotInput:
    snapshot: strawberry.ID


class TrackInputModel(BaseModel):
    edge: str
    t: int 
    kind: str
    value: Any | None = None
    run: str
    caused_by: list[str] = Field(default_factory=list)


@pydantic.input(TrackInputModel)
class TrackInput:
    edge: strawberry.ID
    t: int 
    kind: enums.RunEventKind
    value: scalars.EventValue | None = None
    run: strawberry.ID
    caused_by: list[strawberry.ID] 
