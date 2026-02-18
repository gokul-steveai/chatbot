from fastapi import Request, HTTPException, status
from rag import RAGPipeline
from core.logger import logger

def get_rag_pipeline(request: Request) -> RAGPipeline:
    try:
        return request.app.state.rag_pipeline
    except Exception as e:
        logger.error(f"Error accessing RAG pipeline: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RAG pipeline not available")