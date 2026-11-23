
import ollama
from pathlib import Path

from pdf_reader import read_pdf

MODEL = "llama3.2"

PAPER_FOLDER = Path("papers")


def load_all_papers():

    pdf_files = list(PAPER_FOLDER.glob("*.pdf"))

    all_papers = []

    if not pdf_files:
        print("No PDF files found inside the papers folder.")
        return all_papers

    for pdf_file in pdf_files:

        print(f"\nReading: {pdf_file.name}")

        text = read_pdf(str(pdf_file))

        if text.strip():

            paper_data = {
                "filename": pdf_file.name,
                "text": text[:6000]
            }

            all_papers.append(paper_data)

            print("Text extracted successfully.")

        else:
            print("No text found in this PDF.")

    return all_papers


def compare_papers(all_papers):

    if not all_papers:
        return "No research papers available for analysis."

    paper_content = ""

    for index, paper in enumerate(all_papers, start=1):

        paper_content += f"""

        PAPER {index}
        Filename: {paper['filename']}

        Content:
        {paper['text']}

        --------------------------------
        """

    prompt = f"""
You are an academic research assistant specializing
in Machine Learning and Cybersecurity.

Analyze and compare the following research papers.

{paper_content}

Prepare a structured report using the following sections:

1. Overall Research Background
2. Individual Paper Summaries
3. Algorithms Used in Each Paper
4. Dataset Comparison
5. Performance Metrics Comparison
6. Methodology Comparison
7. Strengths of Each Paper
8. Limitations of Each Paper
9. Common Research Challenges
10. Preliminary Research Gaps
11. Future Research Directions

Rules:

- Analyze only the supplied paper content.
- Do not invent algorithm names, datasets, or results.
- If a detail is missing, state "Not available in extracted content".
- Do not assume a paper is better based on accuracy alone.
- Compare performance only when datasets and evaluation conditions
  are comparable.
- Clearly distinguish authors' stated limitations from your own
  suggested research opportunities.
- Research gaps are preliminary and must be validated through
  a broader literature review.
- Mention the filename when discussing each paper.
- Use academic language.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a careful scientific literature review assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content


def run_multi_pdf_agent():

    print("=" * 60)
    print("MULTI-PDF FACULTY RESEARCH ASSISTANT")
    print("=" * 60)

    print("\nStep 1: Loading research papers...")

    papers = load_all_papers()

    print(f"\nTotal papers loaded: {len(papers)}")

    if not papers:
        return

    print("\nStep 2: Comparing research papers using Llama...")

    report = compare_papers(papers)

    print("\n" + "=" * 60)
    print("MULTI-PAPER RESEARCH ANALYSIS")
    print("=" * 60)

    print(report)


if __name__ == "__main__":
    run_multi_pdf_agent()
