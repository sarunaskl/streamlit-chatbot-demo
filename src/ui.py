import streamlit as st
import os
import glob
from src.file_processor import extract_text_from_file
from src.rag_pipeline import setup_rag
from src.chat_manager import get_response

def run_app():
    st.title("Streamlit chatbot with RAG")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None

    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    pdf_files = [f for f in glob.glob(f"{data_dir}/*.pdf")]
    if pdf_files and not st.session_state.qa_chain:
        try:
            st.session_state.qa_chain = setup_rag(pdf_files)
            if st.session_state.qa_chain:
                st.session_state.messages.append({"role": "system", "content": f"Įkelti failai iš 'data': {', '.join(os.path.basename(f) for f in pdf_files)}"})
                st.success(f"Įkelti PDF failai iš 'data' katalogo: {len(pdf_files)} failų!")
            else:
                st.warning("Rasta PDF failų, bet RAG sistema neinicijuota dėl dokumentų trūkumo.")
        except Exception as e:
            st.error(f"Klaida įkeliant failus iš 'data': {e}")

    with st.container():
        st.subheader("Chat History")
        if not st.session_state.messages:
            st.info("No messages yet. Start the conversation!")
        else:
            for message in st.session_state.messages:
                with st.expander(f"{message['role'].capitalize()} says:"):
                    st.markdown(message["content"])

    def on_file_upload():
        if st.session_state.uploaded_file:
            try:
                file_content = extract_text_from_file(st.session_state.uploaded_file)
                temp_path = os.path.join("data", st.session_state.uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(st.session_state.uploaded_file.getbuffer())
                pdf_files = [f for f in glob.glob("data/*.pdf")]
                st.session_state.qa_chain = setup_rag(pdf_files)
                if st.session_state.qa_chain:
                    st.success("Failas sėkmingai įkeltas ir RAG sistema atnaujinta!")
                else:
                    st.warning("Failas įkeltas, bet RAG sistema neinicijuota dėl dokumentų trūkumo.")
            except Exception as e:
                st.error(f"Klaida apdorojant failą: {e}")

    st.file_uploader("Upload a file (optional)", type=["txt", "pdf", "docx"], key="uploaded_file", on_change=on_file_upload)

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                response = get_response(st.session_state.messages, st.session_state.qa_chain)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error generating response: {e}")