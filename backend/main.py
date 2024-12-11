from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from swarmauri.agents.concrete.RagAgent import RagAgent
from swarmauri.documents.concrete.Document import Document
from swarmauri.llms.concrete.GroqModel import GroqModel as LLM
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from swarmauri.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore
from helper_functions import extract_text_from_pdf, chunk_text, get_allowed_models
from swarmauri.conversations.concrete.MaxSystemContextConversation import MaxSystemContextConversation

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure upload folder
UPLOAD_FOLDER = 'temp_folder'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("API key is not set. Please set the GROQ_API_KEY environment variable.")
    exit(1)

# Initialize the GroqModel
llm = LLM(api_key=API_KEY)
allowed_models = get_allowed_models(llm)
llm.name = allowed_models[2]

# Initialize vector store
vector_store = TfidfVectorStore()

# Initialize the RAG Agent
rag_system_context = "You are an assistant that provides answers to the user. You utilize the details below:"
rag_conversation = MaxSystemContextConversation(
    system_context=SystemMessage(content=rag_system_context), 
    max_size=50
)

rag_agent = RagAgent(
    llm=llm,
    conversation=rag_conversation,
    system_context=rag_system_context,
    vector_store=vector_store,
)

class Query(BaseModel):
    query: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
    
    try:
        # Save the file
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        contents = await file.read()
        with open(filepath, 'wb') as f:
            f.write(contents)
        
        # Process the PDF
        formatted_text = extract_text_from_pdf(filepath)
        chunks = chunk_text(formatted_text, chunk_size=300, overlap=150)
        documents = [Document(content=chunk) for chunk in chunks]
        
        # Create new vector store instance and RAG agent
        global vector_store, rag_agent
        vector_store = TfidfVectorStore()
        vector_store.add_documents(documents)
        
        # Reinitialize the RAG agent with the new vector store
        rag_agent = RagAgent(
            llm=llm,
            conversation=rag_conversation,
            system_context=rag_system_context,
            vector_store=vector_store,
        )
        
        # Clean up the temporary file
        os.remove(filepath)
        
        return JSONResponse(content={"message": "File processed successfully"}, status_code=200)
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")  # For debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def process_query(query: Query):
    try:
        response = rag_agent.exec(query.query)
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For development purposes, you can include this
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)