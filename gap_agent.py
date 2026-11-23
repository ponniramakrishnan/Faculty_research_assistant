
import json
import ollama
from pathlib import Path

MODEL = "llama3.2"

REPORT_FOLDER = Path("reports")
INPUT_FILE = REPORT_FOLDER / "research_papers.json"
OUTPUT_FILE = REPORT_FOLDER / "Research_Gap_Analysis.md"


# -----------------------------------------
# STEP 1: LOAD RESEARCH PAPER DATA
# -----------------------------------------

def load_papers():

    if not INPUT_FILE.exists():

        print("Comparison JSON file not found.")
        print("Run comparison_generator.py first.")
        return []

    try:

        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            papers = json.load(file)

        if not isinstance(papers, list):

            print("Invalid JSON format.")
            return []

        print(f"Loaded {len(papers)} papers from JSON.")

        return papers

    except Exception as error:

        print("Error loading papers:", error)
        return []


# -----------------------------------------
# STEP 2: ANALYZE RESEARCH GAPS
# -----------------------------------------

def analyze_research_gaps(papers):

    research_data = json.dumps(
        papers,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an academic research gap analysis assistant.

Analyze the following research papers on phishing detection.

PAPER DATA:
{research_data}

Prepare a cross-paper research gap analysis under these headings:

1. Overview of Existing Research
2. Commonly Used Algorithms
3. Dataset Limitations
4. Feature Selection Research Gaps
5. Evaluation and Performance Gaps
6. Common Limitations Across Papers
7. Identified Research Gaps
8. Potential Research Opportunities
9. Proposed Future Research Directions
10. Recommended Research Problem

Rules:
- Analyze the papers collectively.
- Identify patterns, similarities, and differences.
- Do not invent paper findings or datasets.
- Distinguish evidence from your own inference.
- Do not claim a research gap is universally unexplored
  based only on these papers.
- Mention paper titles or filenames wherever possible.
- Focus on machine learning-based phishing URL detection.
- Consider feature selection, optimization, computational
  cost, generalization, and explainability.
- Use academic language.
- Format the output using Markdown.
"""

    print("\nAnalyzing research gaps using Llama 3.2...")

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research analyst specializing "
                        "in machine learning and cybersecurity. "
                        "Ground your analysis in the supplied paper data."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content

    except Exception as error:

        print("Gap analysis failed:", error)
        return None


# -----------------------------------------
# STEP 3: SAVE GAP ANALYSIS REPORT
# -----------------------------------------

def save_gap_report(report):

    REPORT_FOLDER.mkdir(exist_ok=True)

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write("# Cross-Paper Research Gap Analysis\n\n")
            file.write(report)

        print("\nResearch gap report created successfully!")
        print("Saved at:", OUTPUT_FILE.resolve())

    except Exception as error:

        print("Error saving gap report:", error)


# -----------------------------------------
# STEP 4: RUN GAP ANALYSIS AGENT
# -----------------------------------------

def run_gap_agent():

    print("=" * 60)
    print("CROSS-PAPER RESEARCH GAP ANALYSIS AGENT")
    print("=" * 60)

    papers = load_papers()

    if not papers:

        print("\nNo research papers available.")
        return

    report = analyze_research_gaps(papers)

    if not report:

        print("\nNo analysis returned by Llama.")
        return

    save_gap_report(report)

    print("\nGap Analysis Agent completed successfully!")


# -----------------------------------------
# MAIN PROGRAM
# -----------------------------------------

if __name__ == "__main__":

    run_gap_agent()
