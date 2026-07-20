from review_graph import app

def test_review_comment_generation():
    sample_diff = """ def divide(a, b):
    return a / b
"""
    final_state = app.invoke({"diff": sample_diff, "changed_symbol": "divide"})
    assert final_state.get("review_comment") is not None