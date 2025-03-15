from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st
import pdfplumber
import tiktoken
from docx import Document

# Set up the Streamlit app title
st.title("ChatGPT-like clone")

# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
secret_key = os.getenv("GITHUB_TOKEN")

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=secret_key
)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history in a bordered container
with st.container():
    st.subheader("Chat History")
    if not st.session_state.messages:
        st.info("No messages yet. Start the conversation!")
    else:
        for message in st.session_state.messages:
            with st.expander(f"{message['role'].capitalize()} says:"):
                st.markdown(message["content"])
#token counter
                
# Define the file upload callback function
def on_file_upload():
    if st.session_state.uploaded_file is not None:
        # Get the file extension (case-insensitive)
        file_type = st.session_state.uploaded_file.name.split('.')[-1].lower()
        supported_types = ['txt', 'pdf', 'docx']
        
        # Check if the file type is supported
        if file_type not in supported_types:
            st.error(f"Unsupported file type: {file_type}. Please upload a TXT, PDF, or DOCX file.")
            return
        
        # Extract text based on file type
        try:
            if file_type == 'txt':
                file_content = st.session_state.uploaded_file.read().decode("utf-8")
            elif file_type == 'pdf':
                with pdfplumber.open(st.session_state.uploaded_file) as pdf:
                    file_content = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            elif file_type == 'docx':
                doc = Document(st.session_state.uploaded_file)
                file_content = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Failed to extract text from {file_type.upper()} file: {e}")
            return
        
        # Add the file content to the chat history
        st.session_state.messages.append({"role": "user", "content": f"Uploaded file content ({file_type}):\n{file_content}"})
        st.success("File uploaded and added to chat history!")

# Add file uploader widget

st.file_uploader("Upload a file (optional)", type=["txt", "pdf", "docx"], key="uploaded_file", on_change=on_file_upload)

# Chat input for user messages
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                # System message to ensure responses in Lithuanian
                {"role": "system", "content": "Jūs esate naudingas asistentas, kuris visada atsako lietuvių kalba."}
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})