
import ollama

from pdf_reader import read_pdf

MODEL = "llama3.2"


def analyze_pdf(text, filename):

    # Limit text for our first experiment
    paper_text = text[:12000]

    prompt = f"""
You are an academic research assistant.

Analyze the following research paper extracted from a PDF.

PDF Filename: {filename}

PAPER CONTENT:
{paper_text}

Prepare a structured research analysis with the following sections:

1. Research Problem
2. Research Objective
3. Methodology
4. Algorithms Used
5. Dataset Used
6. Experimental Results
7. Key Findings
8. Limitations
9. Future Research Directions

Instructions:
- Analyze only the content provided.
- Do not invent results, datasets, algorithms, or references.
- If information is missing, write "Not mentioned in the extracted text".
- Clearly distinguish the authors' findings from your suggestions.
- Use academic language.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a careful academic research paper analyzer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.message.content


def run_pdf_analyzer():

    filename = input("Enter PDF filename: ")

    print("\nStep 1: Reading PDF...")

    text = read_pdf(filename)

    if not text.strip():
        print("No text extracted from PDF.")
        return

    print("PDF text extracted successfully.")
    print("Extracted characters:", len(text))

    print("\nStep 2: Sending paper to Llama 3.2...")

    report = analyze_pdf(text, filename)

    print("\n" + "=" * 60)
    print("RESEARCH PAPER ANALYSIS")
    print("=" * 60)

    print(report)


if __name__ == "__main__":
    run_pdf_analyzer()
