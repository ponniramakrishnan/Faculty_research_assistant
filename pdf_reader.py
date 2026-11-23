from pypdf import PdfReader

def read_pdf(pdf_path):

    reader = PdfReader(pdf_path)
    full_text = ""

    for page_number, page in enumerate(reader.pages, start=1):

        page_text = page.extract_text() or ""

        full_text += f"\n\n--- Page {page_number} ---\n"
        full_text += page_text

    print(f"Extracted {len(full_text)} characters.")

    return full_text


def read_pdf_pages(pdf_path):

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        page_text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": page_text
        })

    return pages