import io
import fitz
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text.strip()


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename_lower.endswith(".doc"):
        raise ValueError("El formato .doc no está soportado. Por favor usa .docx o .pdf")
    else:
        raise ValueError("Formato de archivo no soportado. Usa PDF o DOCX")