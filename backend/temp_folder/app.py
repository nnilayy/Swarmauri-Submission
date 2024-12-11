import os
from dotenv import load_dotenv
from swarmauri.agents.concrete.RagAgent import RagAgent
from swarmauri.documents.concrete.Document import Document
from swarmauri.llms.concrete.GroqModel import GroqModel as LLM
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from swarmauri.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore
from backend.helper_functions import extract_text_from_pdf, chunk_text, get_allowed_models
from swarmauri.conversations.concrete.MaxSystemContextConversation import MaxSystemContextConversation

# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("API key is not set. Please set the GROQ_API_KEY environment variable.")

# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
# Initializing the vector store and adding documents
vector_store = TfidfVectorStore()
pdf_path = "Resume_CV-Nilay Kumar.pdf"
formatted_text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(formatted_text, chunk_size=300, overlap=150)
documents = [Document(content=chunk) for chunk in chunks]
vector_store.add_documents(documents)

# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
# Initialize the GroqModel
llm = LLM(api_key=API_KEY)
allowed_models = get_allowed_models(llm)
llm.name = allowed_models[2]

# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
# Initialize the RAG Agent
rag_system_context = "You are an assistant that provides answers to the user. You utilize the details below:"
rag_conversation = MaxSystemContextConversation(
    system_context=SystemMessage(content=rag_system_context), max_size=50
)

rag_agent = RagAgent(
    llm=llm,
    conversation=rag_conversation,
    system_context=rag_system_context,
    vector_store=vector_store,
)
# ----------------------------------------------------------------------------------------------------------------------------- 
# -----------------------------------------------------------------------------------------------------------------------------

# Start the conversation
while True:
    query =input("Enter your Question: ")
    if query =="q" or query =="Q":
        break
    response = rag_agent.exec(query)
    print(response)