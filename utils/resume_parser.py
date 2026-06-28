import PyPDF2
from docx import Document
import io

def extract_text(file_storage):
    """
    Extract text from a Werkzeug FileStorage object in-memory.
    Supports PDF and DOCX files.
    """
    filename = file_storage.filename.lower()
    text = ""
    
    try:
        # Read file into BytesIO to avoid 'seekable' attribute error from SpooledTemporaryFile
        file_bytes = file_storage.read()
        file_stream = io.BytesIO(file_bytes)
        
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file_stream)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif filename.endswith('.docx'):
            doc = Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")
    except Exception as e:
        raise Exception(f"Error parsing file: {str(e)}")
        
    return text.strip()
