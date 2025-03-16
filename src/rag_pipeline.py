from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.prompts import PromptTemplate
import os
from langchain_openai import ChatOpenAI
from src.client import client

def setup_rag(file_paths):
    print("Starting RAG setup with files:", file_paths)
    all_documents = []
    for file_path in file_paths:
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            valid_docs = [doc for doc in documents if doc.page_content.strip()]
            if valid_docs:
                print(f"Loaded {file_path} with {len(valid_docs)} valid pages.")
                all_documents.extend(valid_docs)
            else:
                print(f"No valid content in {file_path}.")
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")

    if not all_documents:
        print("No valid documents loaded; RAG setup aborted.")
        return None

    print(f"Total valid documents loaded: {len(all_documents)}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(all_documents)
    print(f"Split documents into {len(all_splits)} sub-documents.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=os.getenv("GITHUB_TOKEN"),
        openai_api_base="https://models.inference.ai.azure.com"
    )
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=all_splits)
    retriever = vector_store.as_retriever()

    llm = ChatOpenAI(
        openai_api_key=os.getenv("GITHUB_TOKEN"),
        openai_api_base="https://models.inference.ai.azure.com",
        model_name="gpt-4o"
    )

    # Stricter prompt to enforce concise answers
    rag_prompt = PromptTemplate(
        input_variables=["context", "query"],
        template="Jūs esate naudingas asistentas, kuris visada atsako lietuvių kalba.\n\nKontekstas: {context}\nKlausimas: {query}\nAtsakykite tik vienu ar dviem sakiniais lietuvių kalba, remdamiesi kontekstu. Jokiu būdu nekopijuokite viso konteksto ar dokumento."
    )

    # Use RunnableSequence instead of deprecated LLMChain
    rag_chain = rag_prompt | llm
    
    def rag_function(input_dict):
        docs = retriever.invoke(input_dict["query"])
        context = "\n".join([doc.page_content for doc in docs])[:4000]  # Limit to 4000 chars
        response = rag_chain.invoke({"context": context, "query": input_dict["query"]})
        return response.content  # Extract string from ChatOpenAI response

    return rag_function