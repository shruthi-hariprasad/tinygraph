from mcp.server.fastmcp import FastMCP
from code_graph import build_repo_graph, find_callers, get_function_source
from semantic_index import repo_chunks, build_semantic_index, top_k_similar_functions

call_graph, defined_in = build_repo_graph("sample_repo")
collection = build_semantic_index(repo_chunks("sample_repo"))

mcp = FastMCP(name="CodeReviewAgent")

@mcp.tool()
def get_callers(function_name: str) -> list[str]:
    """Return the names of functions that call a given function."""
    return find_callers(function_name, call_graph)

@mcp.tool()
def get_source(function_name: str) -> str:
    """Return the source code of a given function."""
    return get_function_source(function_name, defined_in) or "Source not found."

@mcp.tool()
def semantic_search(function_name: str, k: int = 3) -> list[dict]:
    """Return the top k similar functions to a given function based on semantic similarity."""
    functions = top_k_similar_functions(function_name, collection, k)
    function_names = functions['ids'][0]
    function_sources = functions['documents'][0]
    zip_functions = zip(function_names, function_sources)
    result = []
    for name, source in zip_functions:
        func = {"function_name": name, "source": source}
        result.append(func)
    return result

if __name__ == "__main__":
    mcp.run()