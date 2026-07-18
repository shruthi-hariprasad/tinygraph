from typing_extensions import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

class AgentState(TypedDict):
    diff: str
    context: NotRequired[str]
    review_comment: NotRequired[str]

def context_node(state: AgentState):
    with open("sample_repo/calc.py", 'r') as f:
        content = f.read()
    return {"context": content}

def agent_node(state: AgentState):
    prompt = f"""
    You are a code review assistant. 
    Here is the diff of a code change:
    {state['diff']}
    
    Here is the context of the file:
    {state.get('context', '')}
    
    Please provide a review comment for this code change.
    """
    response = llm.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}])
    return {"review_comment": response.choices[0].message.content}

workflow = StateGraph(AgentState)

workflow.add_node("ContextNode", context_node)
workflow.add_node("AgentNode", agent_node)

workflow.add_edge(START, "ContextNode")
workflow.add_edge("ContextNode", "AgentNode")
workflow.add_edge("AgentNode", END)

app = workflow.compile()

if __name__ == "__main__":
    sample_diff = """ def divide(a, b):
    return a / b
"""
    final_state = app.invoke({"diff": sample_diff})
    print("Review Comment:", final_state.get("review_comment", "No comment generated."))