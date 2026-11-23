
import ollama
from pathlib import Path

MODEL = "llama3.2"

REPORT_FOLDER = Path("reports")
GAP_FILE = REPORT_FOLDER / "Research_Gap_Analysis.md"
OUTPUT_FILE = REPORT_FOLDER / "Research_Ideas.md"


# -----------------------------------------
# STEP 1: LOAD RESEARCH GAP REPORT
# -----------------------------------------

def load_research_gaps():

    if not GAP_FILE.exists():

        print("Research gap report not found.")
        print("Run gap_agent.py first.")
        return None

    try:

        with open(GAP_FILE, "r", encoding="utf-8") as file:
            gap_content = file.read()

        if not gap_content.strip():

            print("Research gap report is empty.")
            return None

        return gap_content

    except Exception as error:

        print("Error reading research gap report:", error)
        return None


# -----------------------------------------
# STEP 2: GENERATE RESEARCH IDEAS
# -----------------------------------------

def generate_research_ideas(gap_content):

    prompt = f"""
You are an expert academic research idea generator
specializing in Machine Learning and Cybersecurity.

Analyze the following research gap report:

{gap_content}

Generate 5 innovative research ideas focused on
Machine Learning-based Phishing URL Detection.

For EACH research idea, provide:

1. Research Title
2. Problem Statement
3. Identified Research Gap
4. Proposed Methodology
5. Proposed Algorithms
6. Feature Selection Strategy
7. Dataset Suggestions
8. Evaluation Metrics
9. Expected Contribution
10. Novelty

Requirements:

- Ideas must be based on the research gaps provided.
- Avoid repeating the same idea with different titles.
- Prefer technically feasible research ideas.
- Consider optimization algorithms, hybrid ML,
  explainable AI, lightweight detection, and generalization.
- Suggest possible methods, but do not claim they are proven.
- Clearly distinguish proposed work from existing research.
- Use academic language.
- Format the output using Markdown.
"""

    print("\nGenerating research ideas using Llama 3.2...")

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an academic research ideation assistant. "
                        "Generate technically feasible and novel research "
                        "directions grounded in the supplied research gaps."
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

        print("Research idea generation failed:", error)
        return None


# -----------------------------------------
# STEP 3: SAVE RESEARCH IDEAS
# -----------------------------------------

def save_research_ideas(ideas):

    REPORT_FOLDER.mkdir(exist_ok=True)

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write("# Phishing URL Detection - Research Ideas\n\n")
            file.write(ideas)

        print("\nResearch ideas saved successfully!")
        print("Output:", OUTPUT_FILE.resolve())

    except Exception as error:

        print("Error saving research ideas:", error)


# -----------------------------------------
# STEP 4: RUN RESEARCH IDEA AGENT
# -----------------------------------------

def run_research_idea_agent():

    print("=" * 60)
    print("RESEARCH IDEA GENERATOR AGENT")
    print("=" * 60)

    gap_content = load_research_gaps()

    if not gap_content:

        print("\nNo research gap content available.")
        return

    print("Research gap report loaded successfully.")

    ideas = generate_research_ideas(gap_content)

    if not ideas:

        print("\nNo research ideas generated.")
        return

    save_research_ideas(ideas)

    print("\nResearch Idea Agent completed successfully!")


# -----------------------------------------
# MAIN PROGRAM
# -----------------------------------------

if __name__ == "__main__":

    run_research_idea_agent()
