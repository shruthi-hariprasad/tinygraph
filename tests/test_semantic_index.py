from semantic_index import repo_chunks, build_semantic_index, top_k_similar_functions

def test_semantic_retrieval():
    # Build the semantic index for the sample repository
    chunks = repo_chunks("sample_repo")
    collection = build_semantic_index(chunks)

    # Test retrieval of similar functions for a known function
    changed_function = "divide"
    results = top_k_similar_functions(changed_function, collection, k=3)

    # Check that the results contain the expected keys
    assert 'ids' in results
    assert 'documents' in results
    assert 'metadatas' in results

    # Check that the changed function is not included in the results
    assert changed_function not in results['ids'][0]

    # Check that we have at most k results
    assert len(results['ids'][0]) <= 3