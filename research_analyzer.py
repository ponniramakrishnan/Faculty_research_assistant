
import ollama

from research_tools import search_openalex


def convert_abstract(abstract_index):

    if not abstract_index:
        return "Abstract not available."

    words = {}

    for word, positions in abstract_index.items():

        for position in positions:

            words[position] = word

    abstract = " ".join(
        words[position]
        for position in sorted(words)
    )

    return abstract


def collect_paper_details(papers):

    research_data = []

    for paper in papers:

        title = paper.get("title", "Unknown title")

        year = paper.get("publication_year", "Unknown")

        doi = paper.get("doi", "Not available")

        citations = paper.get("cited_by_count", 0)

        abstract = convert_abstract(
            paper.get("abstract_inverted_index")
        )

        paper_details = f"""
        Title: {title}
        Publication Year: {year}
        DOI: {doi}
        Citation Count: {citations}
        Abstract: {abstract}
        """

        research_data.append(paper_details)

    return research_data


def analyze_papers(topic, research_data):

    paper_text = "\n\n".join(research_data)

    prompt = f"""
    Research Topic: {topic}

    Research papers retrieved from OpenAlex:

    {paper_text}

    Analyze ONLY the research information supplied above.

    Prepare the report using these sections:

    1. Research Background
    2. Paper-wise Summary
    3. Machine Learning Algorithms Used
    4. Comparison of Research Approaches
    5. Challenges and Limitations
    6. Potential Research Gaps
    7. Future Research Directions

    Rules:

    - Use academic language.
    - Do not invent paper findings.
    - Do not invent author names or citations.
    - If an abstract is missing, mention that.
    - Distinguish evidence from your own suggestions.
    - Research gaps must be treated as preliminary.
    - Mention the paper title when discussing a paper.
    """

    response = ollama.chat(

        model="llama3.2",

        messages=[
            {
                "role": "system",

                "content": (
                    "You are a careful academic "
                    "research analysis assistant."
                )
            },

            {
                "role": "user",

                "content": prompt
            }
        ]
    )

    return response.message.content


def run_research_analysis():

    topic = input(
        "\nEnter research topic: "
    )

    print("\nStep 1: Searching research papers...")

    papers = search_openalex(topic, limit=5)

    print("\nStep 2: Collecting paper information...")

    research_data = collect_paper_details(papers)

    print("\nStep 3: Sending papers to Llama...")

    report = analyze_papers(
        topic,
        research_data
    )

    print("\n" + "=" * 60)

    print("FACULTY RESEARCH ANALYSIS REPORT")

    print("=" * 60)

    print(report)


if __name__ == "__main__":

    run_research_analysis()
