import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from core.config import settings


class RAGPipeline:
    def __init__(self, data_dir: str = "data", persist_dir: str = None, model_name: str = None):
        self.data_dir = data_dir
        self.persist_dir = persist_dir or settings.chroma_dir
        self.model_name = model_name or settings.gemini_model
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key = settings.gemini_api_key)
        self.vector_store = None
        self.chain = None
        self.llm = None
        
    def load_documents(self) -> list[Document]:
        loader = DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader)
        docs = loader.load()
        print(f"Loaded {len(docs)} document(s)")
        return docs
    
    def split_documents(self, documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        print(f"Split into {len(chunks)} chunks")
        return chunks
    
    async def initialize_vector_store(self):
        if os.path.exists(self.persist_dir):
            print("Loading existing vector store...")
            self.vector_store = Chroma(persist_directory=self.persist_dir, embedding_function=self.embeddings)
        else:
            print("Creating new vector store...")
            docs = self.load_documents()
            chunks = self.split_documents(docs)
            self.vector_store = await Chroma.afrom_documents(documents=chunks, embedding=self.embeddings, persist_directory=self.persist_dir)
            print(f"Indexing complete. Data stored at {self.persist_dir}")
        
    def build_chain(self):
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0, max_output_tokens=1024, api_key=settings.gemini_api_key)
        retriever = self.vector_store.as_retriever(search_type='similarity', search_kwargs={'k': 4,})
        
        template = """Answer the question based ONLY on the following context:
        {context}
        
        {question}
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        self.chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | self.llm | StrOutputParser()
        print("RAG chain created.")
    
    async def initialize(self):
        await self.initialize_vector_store()
        self.build_chain()
        return self
    
    async def query(self, question: str) -> str:
        return await self.chain.ainvoke(question)
