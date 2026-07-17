from graph import app

def test_graph():
    input_data = {"input": "Hello"}
    final_state = app.invoke(input_data)

    assert "response" in final_state
    assert final_state["response"] == "Further Processed: Hello"