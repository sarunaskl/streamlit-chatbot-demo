import pdfplumber
from docx import Document as DocxDocument

def extract_text_from_file(file):
    file_type = file.name.split('.')[-1].lower()
    if file_type == 'txt':
        return file.read().decode("utf-8")
    elif file_type == 'pdf':
        with pdfplumber.open(file) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif file_type == 'docx':
        doc = DocxDocument(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError(f"Nepalaikomas failo tipas: {file_type}")