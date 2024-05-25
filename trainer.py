import os
from pinecone import Pinecone
from llama_index.llms.gemini import Gemini
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core import StorageContext, VectorStoreIndex, download_loader
from llama_index.core import Settings
from llama_index.readers.web import BeautifulSoupWebReader
from config import *

from collections import deque

DATA_URL = "https://tbcland.com/"

llm = Gemini(model_name="models/gemini-1.0-pro")

pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

pinecone_index = pinecone_client.Index("kom-index")

# loader = BeautifulSoupWebReader()
# documents = loader.load_data(urls=[DATA_URL])

embed_model = GeminiEmbedding(model_name="models/embedding-001")

Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = 512

# Create a PineconeVectorStore using the specified pinecone_index
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

# storage_context = StorageContext.from_defaults(
#     vector_store=vector_store
# )

# index = VectorStoreIndex.from_documents(
#     documents, 
#     storage_context=storage_context
# )

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

query_engine = index.as_query_engine()

chat_memory = dict()

def chat_with_memory(user_id, message, limit=4):
    if user_id not in chat_memory:
        chat_memory[user_id] = deque(maxlen=limit)

    template = """
    System: You are helpful and friendly text based AI assistant, follow up the conversation and respond to the user based on the provided context.
    If you don't know the answer, answer with your own knowledge as possible
    Try to do:
    Ask question based on the details you have and previous conversation
    Make the response short and crisp
    Be friendly assistant
    try to share details about the context provided with you below
    Entertain the user with your AI power

    Never do:
    1) Don't say "in this context" , "based on the context provided" or something that says about context
    2) Don't respond with too much length context, make it simple and conversational
    3) Don't ask like "anything else I can help you with today?" instead try to share details based on the conversation until the user says enough

    Your Name: Goat AI
    Your details: You are capable of answering <below provided context details comes here>
    You are working on the telegram group and to help user based on the provided context, do admin opretaions such as kick, ban, mute automatically

    conversation:
    """

    for user, system in chat_memory[user_id]:
        template += f"User: {user}\nAI: {system}\n"
    
    template += f"User: {message}"

    gemini_response = query_engine.query(template)
    print(template)
    print()
    print(gemini_response)

    chat_memory[user_id].append((message, gemini_response))

    if len(chat_memory[user_id]) > limit:
        chat_memory[user_id].popleft()

while True:
    user_id = int(input("ID: "))
    text = input("Ask me: ")
    chat_with_memory(user_id, text)

