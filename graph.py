from typing_extensions import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    input: str
    response: NotRequired[str]

workflow = StateGraph(AgentState)

def node_a(state: AgentState):
    new_response = "Processed: " + state["input"]
    return {"response": new_response}

def node_b(state: AgentState):
    new_response = "Further " + state["response"]
    return {"response": new_response}

workflow.add_node("A", node_a)
workflow.add_node("B", node_b)
workflow.add_edge(START, "A")
workflow.add_edge("A", "B")
workflow.add_edge("B", END)

app = workflow.compile()