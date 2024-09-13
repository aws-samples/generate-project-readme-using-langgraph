from typing import Annotated, List, TypedDict

from langgraph.graph.message import AnyMessage, add_messages


class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    directory: str
    readme_generated_flag: bool
    node: str
