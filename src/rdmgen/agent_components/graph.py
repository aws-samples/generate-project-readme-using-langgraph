from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from ..constants import ENABLE_LANGGRAPH_DEBUG_MODE
from .graph_elements import (
    call_model,
    correct_readme,
    get_dir_path,
    readme_generated,
    router,
    tool_node,
    tool_return,
)
from .state import AgentState

workflow = StateGraph(AgentState)

# Define Nodes
workflow.add_node("call_model", call_model)
workflow.add_node("get_dir_path", get_dir_path)
workflow.add_node("tools", tool_node)
workflow.add_node("readme_generated", readme_generated)
workflow.add_node("correct_readme", correct_readme)

# Entrypoint
workflow.add_edge(START, "get_dir_path")

# Edges
workflow.add_edge("get_dir_path", "call_model")
workflow.add_edge("readme_generated", "correct_readme")


# Conditional edges
workflow.add_conditional_edges(
    "call_model", router, {"tools": "tools", "continue": "readme_generated"}
)

workflow.add_conditional_edges(
    "tools", tool_return, {"generate": "call_model", "correct": "correct_readme"}
)

workflow.add_conditional_edges(
    "correct_readme", router, {"tools": "tools", "finish": END}
)

checkpointer = MemorySaver()

# Create runnable
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=None,
    debug=ENABLE_LANGGRAPH_DEBUG_MODE,
)
