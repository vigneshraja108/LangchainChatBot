from fastapi import FastAPI, Request
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import CSVLoader

# Create app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ['http://localhost:3000'] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and prepare RAG components once on startup
# loader = TextLoader("continent.csv")
loader = CSVLoader(file_path="continent.csv")
docs = loader.load()
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embedding = OllamaEmbeddings(model="nomic-embed-text")
db = FAISS.from_documents(chunks, embedding)

llm = Ollama(model="deepseek-r1:1.5b")
output_parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an assistant helping with information about continents and their countries or cultures. "
     "Answer the user's question using ONLY the following context. "
     "If the answer cannot be found in the context\nContext:\n{context}"),
    ("user", "{query}")
])


chain = prompt | llm | output_parser

# Define input schema
class QueryRequest(BaseModel):
    query: str

# Define a working route
@app.post("/ask")
async def ask_question(request: QueryRequest):
    docs = db.similarity_search(request.query, k=3)
    context = "\n".join([doc.page_content for doc in docs]).strip()

    if not context:
        return {"answer": "That information is not available."}

    result = chain.invoke({"query": request.query, "context": context}).strip()
    return {"answer": result}
