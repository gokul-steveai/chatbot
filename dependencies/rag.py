from fastapi import Request, HTTPException, status
from rag import RAGPipeline

def get_rag_pipeline(request: Request) -> RAGPipeline:
    try:
        return request.app.state.rag_pipeline
    except Exception as e:
        print(f"Error accessing RAG pipeline: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RAG pipeline not available")