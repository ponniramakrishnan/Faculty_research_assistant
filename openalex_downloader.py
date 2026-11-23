import requests
import os
import re
from research_rag import index_papers

PAPERS_FOLDER = "papers"

os.makedirs(PAPERS_FOLDER, exist_ok=True)


def clean_filename(title):
    title = re.sub(r'[<>:"/\\|?*]', "", title)
    title = title.strip()
    return title[:150]


def search_openalex(topic, limit=5):

    url = "https://api.openalex.org/works"

    params = {
        "search": topic,
        "per-page": limit
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json().get("results", [])


def get_pdf_url(paper):

    # Check the best open access location first
    best_location = paper.get("best_oa_location") or {}

    pdf_url = best_location.get("pdf_url")

    if pdf_url:
        return pdf_url

    # If unavailable, check other open access locations
    for location in paper.get("locations", []):

        pdf_url = location.get("pdf_url")

        if pdf_url:
            return pdf_url

    return None


def download_pdf(paper):

    title = paper.get("title", "Research_Paper")

    pdf_url = get_pdf_url(paper)

    if not pdf_url:
        print("No open-access PDF available.")
        return False

    filename = clean_filename(title) + ".pdf"

    filepath = os.path.join(PAPERS_FOLDER, filename)

    # Avoid downloading the same paper again
    if os.path.exists(filepath):
        print("Already downloaded:", filename)
        return True

    try:

        print("\nDownloading:", title)

        response = requests.get(
            pdf_url,
            timeout=60,
            headers={"User-Agent": "FacultyResearchAssistant/1.0"},
            stream=True
        )

        response.raise_for_status()

        # Check if the file is actually a PDF
        content_type = response.headers.get("Content-Type", "").lower()

        first_chunk = next(
            response.iter_content(chunk_size=1024),
            b""
        )

        if not first_chunk.startswith(b"%PDF-"):
            print("The downloaded file is not a valid PDF.")
            return False

        with open(filepath, "wb") as file:

            file.write(first_chunk)

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:
                    file.write(chunk)

        print("Saved successfully:", filepath)

        return True

    except Exception as e:

        print("Download failed:", e)

        if os.path.exists(filepath):
            os.remove(filepath)

        return False


def download_research_papers(topic, limit=5):

    print("\nResearch topic:", topic)
    print("=" * 60)

    papers = search_openalex(topic, limit)

    print("Papers found:", len(papers))

    downloaded = 0

    for i, paper in enumerate(papers, start=1):

        print(f"\nPaper {i}")
        print("-" * 40)

        print("Title:", paper.get("title"))
        print("Year:", paper.get("publication_year"))

        if download_pdf(paper):
            downloaded += 1

    print("\nDownload Summary")
    print("=" * 60)
    print("Papers searched:", len(papers))
    print("Papers downloaded/already present:", downloaded)
    print("Folder:", os.path.abspath(PAPERS_FOLDER))
    if downloaded > 0:

        print("\nStarting automatic RAG indexing...")

        index_papers()

        print("\nYour research papers are now indexed!")


if __name__ == "__main__":

    topic = input("Enter research topic: ")

    download_research_papers(topic, limit=5)