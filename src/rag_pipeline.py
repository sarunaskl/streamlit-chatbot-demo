from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.chains import RetrievalQA
from langchain import hub
import os
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

    # Use the key from client for embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=all_splits)

    # Use raw OpenAI client instead of ChatOpenAI for consistency
    from langchain.llms import OpenAI as LangChainOpenAI
    llm = LangChainOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    prompt = hub.pull("rlm/rag-prompt")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain