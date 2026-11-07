import requests
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DOWNLOAD_DIR = BASE_DIR / "data" / "raw"


DOCUMENTS = [
    {
        "name": "constitution_loksabha_2024.pdf",
        "url": "https://eparlib.sansad.in/bitstream/123456789/2982247/1/29-05-27_Constitution_English_Final.pdf"
    },
    {
        "name": "constitution_legislative_2025.pdf",
        "url": "https://www.legislative.gov.in/static/uploads/2025/08/cb1b190ea633a1746368ed1fac35fb30.pdf"
    },
    {
        "name": "constitution_legislative_2025_edition.pdf",
        "url": "https://www.legislative.gov.in/static/uploads/2025/07/359f70a69695affb9d72f8393102bd2e.pdf"
    },
    {
        "name": "legislative_department_page.html",
        "url": "https://lddashboard.legislative.gov.in/constitution-of-india"
    }
]


def download_document(url, filename):

    file_path = DOWNLOAD_DIR / filename

    try:

        print(f"\nDownloading: {filename}")

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        with requests.get(
            url,
            headers=headers,
            timeout=(10, 45),
            stream=True
        ) as response:

            response.raise_for_status()

            with open(file_path, "wb") as file:

                for chunk in response.iter_content(
                    chunk_size=8192
                ):

                    if chunk:
                        file.write(chunk)

        # Validate PDF files
        if filename.lower().endswith(".pdf"):

            with open(file_path, "rb") as file:
                signature = file.read(5)

            if signature != b"%PDF-":
                file_path.unlink(missing_ok=True)
                raise ValueError("Downloaded file is not a valid PDF")

        print("Download successful:", filename)

    except requests.exceptions.Timeout:
        print("Download timed out:", filename)

    except requests.exceptions.HTTPError as error:
        print("HTTP error:", error)

    except requests.exceptions.RequestException as error:
        print("Request failed:", error)

    except (OSError, ValueError) as error:
        print("File error:", error)


def fetch_documents():

    DOWNLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for document in DOCUMENTS:

        try:
            download_document(
                document["url"],
                document["name"]
            )

        except Exception as error:
            print("Unexpected download error:", error)


if __name__ == "__main__":
    fetch_documents()