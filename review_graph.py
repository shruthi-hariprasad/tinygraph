from typing_extensions import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END
from code_graph import build_repo_graph, find_callers, get_function_source
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

class AgentState(TypedDict):
    diff: str
    changed_symbol: str
    context: NotRequired[str]
    review_comment: NotRequired[str]

def context_node(state: AgentState):
    call_graph, defined_in = build_repo_graph("sample_repo")
    changed_symbol = state['changed_symbol']
    context = f"CHANGED FUNCTION: {changed_symbol} (defined in {defined_in.get(changed_symbol, 'unknown file')})\n{get_function_source(changed_symbol, defined_in) or 'Source not found.'}\nCALLERS OF {changed_symbol}:\n"
    callers = find_callers(changed_symbol, call_graph)
    if not callers:
        context += f"No callers found in this repository."
    else:
        context_sources = []
        for caller in callers:
            caller_source = get_function_source(caller, defined_in)
            if caller_source:
                context_sources.append(f"CALLER FUNCTION: {caller} (defined in {defined_in.get(caller, 'unknown file')})\n{caller_source}")
            else:
                context_sources.append(f"CALLER FUNCTION: {caller} (defined in {defined_in.get(caller, 'unknown file')})\nSource not found.")
        context += "\n\n".join(filter(None, context_sources))
    return {"context": context}

def agent_node(state: AgentState):
    prompt = f"""
    You are a code review assistant. 
    Here is the diff of a code change:
    {state['diff']}
    
    Here is the context which contains the changed function and the functions that call it, pulled from the repository.:
    {state.get('context', '')}

    Please provide a review comment for this code change while considering impact on the callers shown, and reference functions by name when relevant.
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
    final_state = app.invoke({"diff": sample_diff, "changed_symbol": "divide"})
    print("Review Comment:", final_state.get("review_comment", "No comment generated."))
    print("Context:", final_state.get("context", "No context generated."))