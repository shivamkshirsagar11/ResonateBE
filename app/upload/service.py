import pdfplumber


async def extract_pdf_structure(file_path: str):
    pages_data = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            tables = page.extract_tables()

            pages_data.append({
                "page": page_number,
                "text": text,
                "tables": tables
            })

    return pages_data