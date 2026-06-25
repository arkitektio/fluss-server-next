from typing import NewType

import strawberry

FlowHash = NewType("FlowHash", str)
ValueMap = NewType("ValueMap", object)
EventValue = NewType("EventValue", object)


# Registered with the schema via StrawberryConfig.scalar_map (the non-deprecated
# way to map a NewType to a custom scalar).
scalar_map = {
    FlowHash: strawberry.scalar(
        name="FlowHash",
        description="A hash uniquely identifying the graph of a flow.",
        serialize=lambda v: v,
        parse_value=lambda v: v,
    ),
    ValueMap: strawberry.scalar(
        name="ValueMap",
        description="A JSON-serializable map of port keys to arbitrary values.",
        serialize=lambda v: v,
        parse_value=lambda v: v,
    ),
    EventValue: strawberry.scalar(
        name="EventValue",
        description="The JSON-serializable payload carried by a run event.",
        serialize=lambda v: v,
        parse_value=lambda v: v,
    ),
}
