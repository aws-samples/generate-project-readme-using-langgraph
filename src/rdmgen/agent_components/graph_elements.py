from typing import Literal

from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.prebuilt import ToolNode

from ..utils.bedrock_utils import llm
from .state import AgentState
from .tools import tools

tool_node = ToolNode(tools)


############ CONDITIONAL EDGES ############


def router(state: AgentState):
    result = state["messages"][-1]
    print("state:", state)
    if len(result.tool_calls) > 0:
        return "tools"
    elif not state["readme_generated_flag"]:
        return "continue"
    else:
        return "finish"


def tool_return(state: AgentState) -> Literal["generate", "correct"]:
    readme_generated = state["readme_generated_flag"]

    if readme_generated:
        return "correct"
    else:
        return "generate"


#################### NODES #################


def call_model(state: AgentState):
    messages = state["messages"]
    response = llm.invoke(messages)
    print(f"response:- {response}")
    # We return a list, because this will get added to the existing list
    return {"messages": [response], "node": "call_model_"}


def correct_readme(state: AgentState):
    messages = state["messages"]
    response = llm.invoke(messages)
    print(f"response:- {response}")
    # We return a list, because this will get added to the existing list
    return {"messages": [response], "node": "correct_readme_"}


def readme_generated(state: AgentState):
    message = HumanMessage(
        content="read the readme in {state.dir} and assess it's quality from 1 to 10 based on best practices in readme writing, then apply corrections and rewrite the README.md file in that same path"
    )
    return {"messages": message, "readme_generated_flag": True}


def get_dir_path(state: AgentState):
    user_ques = state["messages"][-1].content

    class Formatted(BaseModel):
        dir: str = Field(
            description="A properly formatted directory path which must always end with a forward slash ('/')"
        )

    structured_llm = llm.with_structured_output(Formatted)
    model_response = structured_llm.invoke(user_ques)
    print("model_response: ", model_response)
    print("type of model_response: ", type(model_response))
    dir_path = model_response.dir
    return {"directory": dir_path, "readme_generated_flag": False}
