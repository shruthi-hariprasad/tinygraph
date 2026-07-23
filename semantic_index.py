from code_graph import build_repo_graph, find_callers, get_function_source
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def repo_chunks(repo_path):
    call_graph, defined_in = build_repo_graph(repo_path)
    functions = list(call_graph.keys())
    chunks = []
    for function in functions:
        chunk = {}

        function_source = get_function_source(function, defined_in)
        chunk['source'] = function_source if function_source else "Source not found."
        chunk['function_name'] = function
        chunk['filepath'] = defined_in.get(function, 'unknown file')
    
        chunks.append(chunk)
    return chunks

def build_semantic_index(chunks):
    client = chromadb.Client()
    collection = client.get_or_create_collection("function_index")

    for chunk in chunks:
        embedding = model.encode(chunk['source']).tolist()
        collection.add(
            documents=[chunk['source']],
            metadatas=[{"function_name": chunk['function_name'], "filepath": chunk['filepath']}],
            ids=[chunk['function_name']],
            embeddings=[embedding]
        )
    return collection

def top_k_similar_functions(changed_function, collection, k=3):
    query_text = collection.get(ids=[changed_function])
    if not query_text['documents']:
        return {"ids": [[]], "documents": [[]], "metadatas": [[]]}  # Return empty results if the function is not found
    embedding = model.encode(query_text['documents'][0]).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=k, where={"function_name": {"$ne": changed_function}}  # Exclude the changed function itself
    )
    return results

if __name__ == "__main__":
    repo_path = "sample_repo"
    chunks = repo_chunks(repo_path)
    collection = build_semantic_index(chunks)
    results = top_k_similar_functions("divide", collection, k=3)
    print(results)