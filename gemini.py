import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from sentence_transformers import SentenceTransformer

import google.generativeai as genai
import config

genai.configure(api_key=config.GOOGLE_API_KEY)

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

FAISS_INDEX_PATH = "faiss_index.bin"
model_name='sentence-transformers/all-MiniLM-L6-v2'
vector_model = SentenceTransformer(model_name)

# Step 1: Extract content from PDF using PDFLoader
def extract_text_from_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return "\n".join([doc.page_content for doc in documents])

# Step 2: Extract content from Website using WebLoader
def extract_text_from_website(url):
    loader = WebBaseLoader(url)
    documents = loader.load()
    return documents

# Step 3: Chunk the extracted content
def chunk_text(text, chunk_size=512, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(text)

# Function to create FAISS index
def create_faiss_index(chunks):
    embeddings = vector_model.encode(chunks, convert_to_numpy=True)
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(embeddings)
    # Save the index to file
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)
    return faiss_index

# Function to load FAISS index
def load_faiss_index():
    return faiss.read_index(FAISS_INDEX_PATH)

# Step 5: Perform a semantic search using the FAISS index
def semantic_search(faiss_index, query, top_k=5):
    query_embedding = vector_model.encode([query], convert_to_numpy=True)
    D, I = faiss_index.search(query_embedding, top_k)
    return sorted(list(set(I[0])))


# # Step 4: Generate embeddings for the chunks and store in FAISS
# def create_faiss_index(chunks, model_name='sentence-transformers/all-MiniLM-L6-v2'):
#     model = SentenceTransformer(model_name)
#     embeddings = model.encode(chunks, convert_to_numpy=True)
#     faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
#     faiss_index.add(embeddings)
#     return faiss_index, model

# # Step 5: Perform a semantic search using the FAISS index
# def semantic_search(faiss_index, query, model, top_k=1):
#     query_embedding = model.encode([query], convert_to_numpy=True)
#     D, I = faiss_index.search(query_embedding, top_k)
#     return I[0]

# Step 6: Use the retrieved chunks to generate an answer with the Gemini model
def generate_answer(retrieved_chunks, query):
    context = "\n".join(retrieved_chunks)
    
    # Set up safety settings
    # safety_settings = {
    #     HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
    #     HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    #     HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    #     HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    #     HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    # }

    # llm = VertexAI(model_name="gemini-1.0-pro-001", safety_settings=safety_settings)
    # prompt = f"Provide answer based on the provided context\nNever say 'belong to the context', 'based on the context', 'provided info'\nThis is a chatbot, should answer to the user relevant, if information does not exist, try to answer basically\nProvide answer more friendly, short and crisp\nContext: {context}\n\nQuestion: {query}\n\nAnswer:"
    prompt_parts = [
        f"input: {query}\ncontext: {context}",
        "output: ",
    ]

    response = model.generate_content(prompt_parts)
    return response.text