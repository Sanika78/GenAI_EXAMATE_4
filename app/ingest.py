from pypdf import PdfReader

PDF_PATH = "data/raw/constitution.pdf"


def extract_pdf_text():
    try:
        reader = PdfReader(PDF_PATH)

        print("Total pages:", len(reader.pages))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if text:
                print(f"\n--- Page {page_number} ---")
                print(text[:1000])

    except FileNotFoundError:
        print("PDF file not found!")

    except Exception as e:
        print("Error while reading PDF:", e)


if __name__ == "__main__":
    extract_pdf_text()