import ollama
import json
import math
from pathlib import Path
from pdf_reader import read_pdf_pages


# Models
LLM_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"

# Folders and database
PAPER_FOLDER = Path("papers")
DB_FOLDER = Path("research_db")
DB_FILE = DB_FOLDER / "research_embeddings.json"


# 1. Split text into chunks
def split_text(text, chunk_size=1200, overlap=200):
    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]

        if chunk.strip():
            chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks


# 2. Generate embedding using Ollama
def create_embedding(text):
    response = ollama.embed(
        model=EMBED_MODEL,
        input=text
    )

    return response["embeddings"][0]


# 3. Index research papers
def index_papers():

    DB_FOLDER.mkdir(exist_ok=True)

    records = []
    record_id = 0

    pdf_files = list(PAPER_FOLDER.glob("*.pdf"))

    print(f"Found {len(pdf_files)} research papers.")

    for pdf_file in pdf_files:

        print(f"\nProcessing: {pdf_file.name}")

        # Extract each page separately
        pages = read_pdf_pages(pdf_file)

        for page in pages:

            page_number = page["page_number"]
            page_text = page["text"]

            # Skip empty pages
            if not page_text.strip():
                continue

            # Split only this page's text
            chunks = split_text(page_text)

            for chunk_index, chunk in enumerate(chunks):

                record_id += 1

                print(
                    f"Embedding paper {pdf_file.name} | "
                    f"Page {page_number} | "
                    f"Chunk {chunk_index + 1}/{len(chunks)}"
                )

                embedding = create_embedding(chunk)

                records.append({
                    "id": record_id,
                    "source": pdf_file.name,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk,
                    "embedding": embedding
                })

    # Save all records to JSON
    with open(DB_FILE, "w", encoding="utf-8") as file:

        json.dump(records, file, ensure_ascii=False)

    print("\nPaper indexing completed!")
    print(f"Total chunks stored: {len(records)}")
    print(f"Database location: {DB_FILE.resolve()}")

# 4. Calculate cosine similarity (pure Python)
def cosine_similarity(vector_a, vector_b):

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot_product / (norm_a * norm_b)


# 5. Retrieve the most relevant chunks
def retrieve_chunks(question, top_k=3):

    if not DB_FILE.exists():
        print("Research database not found. Index papers first.")
        return []

    with open(DB_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not records:
        return []

    question_embedding = create_embedding(question)

    scored_records = []

    for record in records:

        score = cosine_similarity(
            question_embedding,
            record["embedding"]
        )

        scored_records.append((score, record))

    # Sort by similarity score (highest first)
    scored_records.sort(
        key=lambda item: item[0],
        reverse=True
    )

    results = scored_records[:top_k]

    retrieved_chunks = []

    for score, record in results:

        retrieved_chunks.append({
            "source": record["source"],
            "chunk_index": record["chunk_index"],
            "text": record["text"],
            "score": score
        })

    return retrieved_chunks


# 6. Ask a research question using retrieved content
def ask_research_question(question):

    # Step 1: Retrieve relevant chunks
    results = retrieve_chunks(question, top_k=3)

    if not results:
        print("No relevant research evidence found.")
        return

    # Step 2: Prepare context for the LLM
    context = ""

    for i, item in enumerate(results, start=1):
        context += f"\nEvidence {i}\n"
        context += f"Source: {item['source']}\n"
        context += f"Chunk: {item['chunk_index']}\n"
        context += f"Text: {item['text']}\n"

    # Step 3: Create grounded prompt
    prompt = f"""
You are a research assistant.

Answer the question using ONLY the evidence provided below.

If the evidence is insufficient, clearly state that.

Question:
{question}

Retrieved Evidence:
{context}

Instructions:
1. Answer clearly and academically.
2. Do not invent information.
3. Mention the research paper source when possible.
4. Use the retrieved evidence only.
"""

    # Step 4: Generate answer
    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Step 5: Display answer
    print("\n" + "=" * 60)
    print("RESEARCH ANSWER")
    print("=" * 60)

    print(response["message"]["content"])

    # Step 6: Display evidence and citations
    print("\n" + "=" * 60)
    print("SOURCE EVIDENCE")
    print("=" * 60)

    for i, item in enumerate(results, start=1):

        print(f"\nEvidence {i}")
        print(f"Source Paper : {item['source']}")
        print(f"Page Number : {item['page_number']}")
        print(f"Chunk Number: {item['chunk_index']}")
        print(f"Similarity  : {item['score']:.4f}")

        print("\nRetrieved Text:")
        print(item["text"])

        print("-" * 60)
# 7. Main program
def run_rag():

    print("\nFaculty Research Assistant - RAG")
    print("=" * 40)

    # Index PDFs when the program starts
    index_papers()

    if not DB_FILE.exists():
        return

    with open(DB_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not records:
        print("No chunks available in database.")
        return

    print("\nResearch papers indexed successfully!")
    print("Ask questions about your papers.")
    print("Type 'exit' to stop.")

    while True:

        question = input("\nYour question: ")

        if question.lower().strip() == "exit":
            print("Research assistant stopped.")
            break

        if not question.strip():
            continue

        ask_research_question(question)


if __name__ == "__main__":
    run_rag()