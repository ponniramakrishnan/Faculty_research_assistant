# Faculty Research Assistant Agent

## Overview

The Faculty Research Assistant Agent is a tool-using AI research assistant designed to help faculty members explore research topics, retrieve information from local research papers, analyze findings, and generate research directions.

The agent follows a ReAct-style workflow (Reason, Act, Observe) and uses tools to search research content, analyze retrieved information, and maintain research memory.

## Objectives

- Explore a research topic using natural language queries.
- Search local research papers and abstracts.
- Summarize retrieved research information.
- Identify common research findings and possible research gaps.
- Maintain short-term conversation context.
- Store user research interests in persistent JSON memory.
- Generate structured responses in JSON format.

## Architecture

User Query  
↓  
Agent Planner  
↓  
Reasoning and Planning  
↓  
Tool Selection  
↓  
┌──────────────────────┐  
│ Search Research Notes│  
│ Summarize Findings  │  
│ Save User Memory    │  
│ Retrieve Memory     │  
└──────────────────────┘  
↓  
Observation  
↓  
Agent Loop (until completion or maximum steps)  
↓  
Output Validation  
↓  
Structured JSON Response

## Technologies Used

- **Python** – Agent implementation
- **Ollama** – Local LLM inference
- **Llama 3.2** – Language model
- **JSON** – Persistent memory and structured output
- **Streamlit** – Interactive user interface
- **Local text files / research abstracts** – Knowledge source

## Project Structure

```text
Faculty_research_assistant/
│
├── agent.py
├── research_tools.py
├── research_analyzer.py
├── research_rag.py
├── research_idea_agent.py
├── gap_agent.py
├── comparison_generator.py
├── app.py
├── dashboard.py
├── memory.json
├── notes/
│   ├── machine_learning.txt
│   ├── phishing_detection.txt
│   └── research_abstracts.txt
├── papers/
├── reports/
├── research_db/
└── README.md
```

## Installation

### 1. Install Python

Install Python 3.10 or later.

### 2. Install Ollama

Download and install Ollama:

https://ollama.com/

### 3. Download the language model

```bash
ollama pull llama3.2
```

### 4. Clone the repository

```bash
git clone https://github.com/ponniramakrishnan/Faculty_research_assistant.git
cd Faculty_research_assistant
```

### 5. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

### 6. Install dependencies

Install the required Python packages using:

```powershell
.\.venv\Scripts\python.exe -m pip install ollama streamlit pypdf python-docx pandas numpy
```

## Running the Agent

Ensure Ollama is running locally and the Llama 3.2 model is available.

Run the research agent:

```powershell
.\.venv\Scripts\python.exe agent.py
```

Run the interactive research assistant:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Run the research dashboard:

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard.py
```

## Agent Workflow

The agent follows a bounded ReAct-style process:

1. **Plan** – Determine what information is needed to answer the user's query.
2. **Act** – Select and invoke a research tool.
3. **Observe** – Examine the tool output.
4. **Reflect** – Decide whether more information is needed.
5. **Repeat** – Continue until the task is completed or the maximum step limit is reached.
6. **Finish** – Generate and validate the final JSON response.

## Tools

### Search Research Notes
Searches local text files and research abstracts for information relevant to the user's query.

### Summarize
Summarizes retrieved research information using the local LLM.

### Save Memory
Stores relevant research topics and user preferences in a persistent JSON file.

### Retrieve Memory
Reads previously stored research topics and preferences to personalize subsequent queries.

## Memory

The agent uses two types of memory:

- **Short-term memory:** Context maintained during the current conversation.
- **Long-term memory:** User interests and preferences saved to a JSON file and reused across runs.

## Output Format

The final response is generated in structured JSON format.

```json
{
  "topic": "Machine Learning for Phishing Detection",
  "key_findings": [
    "Machine learning models are used to identify phishing URLs.",
    "Feature selection can reduce model complexity.",
    "Optimization methods can improve feature selection."
  ],
  "sources": [
    "phishing_detection.txt",
    "research_abstracts.txt"
  ],
  "next_steps": [
    "Compare existing feature selection methods.",
    "Investigate optimization-based feature selection.",
    "Evaluate models using precision, recall and F1-score."
  ]
}
```

## Error Handling and Guardrails

The system incorporates safeguards for:

- Empty user queries.
- Empty search results.
- Research tool failures.
- Language model connection failures.
- Invalid JSON output.
- Missing required output fields.
- Maximum agent iteration limits.

When the agent cannot retrieve sufficient research evidence, it should report the limitation instead of inventing findings.

## Sample Run

**User Query:**

```text
Explore research opportunities in machine learning-based phishing URL detection.
```

**Sample Output:**

```json
{
  "topic": "Machine Learning-Based Phishing URL Detection",
  "key_findings": [
    "URL-based features can support phishing classification.",
    "Feature selection may reduce unnecessary input features.",
    "Optimization algorithms can be explored for feature selection."
  ],
  "sources": [
    "phishing_detection.txt",
    "research_abstracts.txt"
  ],
  "next_steps": [
    "Compare feature selection algorithms.",
    "Investigate lightweight detection methods.",
    "Evaluate model performance and computational cost."
  ]
}
```

*Note: Sample output is illustrative. Actual results depend on the research documents available to the agent.*

## Future Enhancements

- Semantic retrieval using vector embeddings.
- Automated research gap identification.
- Research idea generation.
- Multi-paper comparison.
- Citation-aware research summaries.
- Export research reports to Word.
- Interactive dashboard for research workflows.

## Author

Developed as a Faculty Research Assistant Agent project using local LLMs and Python-based tools.
