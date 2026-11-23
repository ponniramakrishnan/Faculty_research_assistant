
import ollama
import json

from research_tools import search_openalex

from research_analyzer import (
    collect_paper_details,
    analyze_papers
)


MODEL = "llama3.2"


def ask_planner(task, state):

    prompt = f"""
You are the decision-making planner of a
Faculty Research Assistant Agent.

USER TASK:
{task}

CURRENT STATE:
{state}

Choose exactly ONE next action:

SEARCH
ANALYZE
FINISH

Rules:

1. If no papers have been searched, choose SEARCH.
2. If papers are available but not analyzed,
   choose ANALYZE.
3. If analysis is completed, choose FINISH.
4. Never choose ANALYZE without papers.
5. Never choose FINISH before analysis.
6. Do not repeat completed actions.

Return ONLY valid JSON.

Example:
{{"action": "SEARCH", "reason": "Need research papers"}}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an AI agent planner."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    decision = json.loads(
        response.message.content
    )

    return decision


def run_agent():

    task = input(
        "\nWhat research task should I perform? "
    )

    state = {
        "papers_searched": False,
        "paper_count": 0,
        "analysis_completed": False
    }

    papers = []
    report = ""

    max_steps = 5

    for step in range(max_steps):

        print(f"\n--- Agent Step {step + 1} ---")

        decision = ask_planner(task, state)

        action = decision.get("action", "").upper()

        reason = decision.get("reason", "")

        print("Planner Decision:", action)
        print("Reason:", reason)

        # ACTION 1: SEARCH
        if action == "SEARCH":

            print("\nAgent is searching papers...")

            papers = search_openalex(
                task,
                limit=5
            )

            state["papers_searched"] = True
            state["paper_count"] = len(papers)

            print(
                f"Agent retrieved {len(papers)} papers."
            )

        # ACTION 2: ANALYZE
        elif action == "ANALYZE":

            if not papers:

                print("No papers available.")
                break

            print("\nAgent is analyzing papers...")

            research_data = collect_paper_details(
                papers
            )

            report = analyze_papers(
                task,
                research_data
            )

            state["analysis_completed"] = True

            print("Analysis completed.")

        # ACTION 3: FINISH
        elif action == "FINISH":

            print("\nAgent decided to finish.")

            break

        else:

            print("Invalid action from planner.")

            break

    # FINAL OUTPUT
    if report:

        print("\n" + "=" * 60)
        print("FACULTY RESEARCH ASSISTANT FINAL REPORT")
        print("=" * 60)

        print(report)

    else:

        print(
            "\nAgent stopped without producing "
            "a research report."
        )


if __name__ == "__main__":

    run_agent()
