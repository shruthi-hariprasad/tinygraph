import ast
from pathlib import Path

def build_call_graph(file_path):
    call_names = {}
    defined_in = {}
    with open(file_path, 'r') as file:
        source = file.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                defined_in[node.name] = str(file_path)
                call_names[node.name] = []
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Name):
                        call_names[node.name].append(subnode.func.id)
    return call_names, defined_in

def build_repo_graph(repository_path):
    call_graph = {}
    defined_in = {}
    for file_path in Path(repository_path).rglob('*.py'):
        file_call_graph, file_defined_in = build_call_graph(file_path)
        call_graph.update(file_call_graph)
        defined_in.update(file_defined_in)
    return call_graph, defined_in

def find_callers(function_name, call_graph):
    callers = []
    for func, calls in call_graph.items():
        if function_name in calls:
            callers.append(func)
    return callers

def get_function_source(function_name, defined_in):
    if function_name not in defined_in:
        return None
    file_path = defined_in[function_name]
    with open(file_path, 'r') as file:
        source = file.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return ast.get_source_segment(source, node)
    return None

def find_enclosing_function(file_path, line_number):
    with open(file_path, 'r') as file:
        source = file.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.lineno <= line_number <= node.end_lineno:
                    return node.name
    return None

if __name__ == "__main__":
    repo_path = "sample_repo"
    graph, defined_in = build_repo_graph(repo_path)
    divide_callers = find_callers("divide", graph)
    subtract_callers = find_callers("subtract", graph)
    source = get_function_source("divide", defined_in)
    print("Source of 'divide':", source)
    print("Functions that call 'divide':", divide_callers)
    print("Functions that call 'subtract':", subtract_callers)
    print("Call Graph:", graph)
    print("Defined In:", defined_in)