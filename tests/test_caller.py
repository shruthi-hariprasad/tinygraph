from review_graph import context_node

def test_review_caller():
    sample_diff = """ def divide(a, b):
    return a / b
"""
    state = {"diff": sample_diff, "changed_symbol": "divide"}
    context = context_node(state)["context"]
    assert "CHANGED FUNCTION: divide" in context
    assert "CALLER FUNCTION: average" in context