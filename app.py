import streamlit as st
import ollama
import json
from pathlib import Path
import research_rag as rag
from pdf_reader import read_pdf

from research_rag import retrieve_chunks, LLM_MODEL, DB_FILE


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Scholar AI | Research Assistant",
    page_icon="🎓",
    layout="wide"
)
st.markdown("""
<style>

/* Main application background */
.stApp {
    background-color: #0F172A;
    color: #F1F5F9;
}

/* Main text */
.stApp p,
.stApp span,
.stApp label,
.stApp li {
    color: #E2E8F0;
}

/* Headings */
h1, h2, h3, h4 {
    color: #F8FAFC !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 15px;
}

/* Chat input area */
[data-testid="stChatInput"] {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 12px;
}

/* Input text */
[data-testid="stChatInput"] textarea {
    color: #F8FAFC !important;
    background-color: #1E293B !important;
}

/* Text boxes and other inputs */
.stTextInput input,
.stTextArea textarea {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #1E293B;
    border-radius: 10px;
    padding: 8px;
}

/* Buttons */
.stButton button {
    background-color: #6D4AFF;
    color: #FFFFFF !important;
    border-radius: 10px;
    border: none;
}

/* Success message */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
}

/* Links */
.stApp a {
    color: #93C5FD !important;
}

/* Divider */
hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# CUSTOM CSS DESIGN
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0b1120 0%, #111827 55%, #17132b 100%);
    color: #f1f5f9;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #17152a);
    border-right: 1px solid rgba(139, 92, 246, 0.2);
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #cbd5e1 !important;
}

h1, h2, h3 {
    color: #f8fafc !important;
}

.hero {
    padding: 30px 32px;
    border-radius: 24px;
    background: linear-gradient(120deg, #171f38, #252044, #342256);
    border: 1px solid rgba(167, 139, 250, 0.25);
    margin-bottom: 24px;
}

.hero-label {
    color: #c4b5fd;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
}

.hero-title {
    font-size: 38px;
    font-weight: 800;
    margin-top: 10px;
    color: #ffffff;
}

.hero-text {
    color: #cbd5e1;
    font-size: 16px;
    margin-top: 8px;
}

.metric-card {
    background: #171f33;
    border: 1px solid #2d3750;
    padding: 18px;
    border-radius: 16px;
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
}

.metric-value {
    color: #e9d5ff;
    font-size: 22px;
    font-weight: 700;
    margin-top: 6px;
}

.prompt-card {
    background: linear-gradient(145deg, #19243a, #211d39);
    border: 1px solid #3a3b5d;
    border-radius: 16px;
    padding: 18px;
    height: 125px;
    margin-bottom: 8px;
}

.prompt-title {
    color: #e9d5ff;
    font-weight: 700;
    font-size: 15px;
}

.prompt-desc {
    color: #a5b4c8;
    font-size: 13px;
    margin-top: 8px;
}

div[data-testid="stChatMessage"] {
    background: rgba(25, 33, 52, 0.65);
    border: 1px solid rgba(100, 116, 139, 0.18);
    border-radius: 18px;
    padding: 16px;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid #6d5bbd;
    background: linear-gradient(135deg, #6d48c7, #493b8f);
    color: white;
    padding: 10px 15px;
    font-weight: 600;
    transition: 0.2s;
}

.stButton > button:hover {
    border-color: #c4b5fd;
    color: white;
    transform: translateY(-2px);
}

.stChatInput textarea {
    border-radius: 16px !important;
}

.source-box {
    background: #121b2e;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #334155;
    margin: 8px 0;
}

.footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 25px 0;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("## 🎓 Scholar AI")
    st.caption("YOUR PERSONAL RESEARCH WORKSPACE")

    st.markdown("---")

    st.markdown("### 📚 Research Library")

    if DB_FILE.exists():

        st.success("Vector database connected")

        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Knowledge Base</div>
            <div class="metric-value">Ready to explore</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("Research database not found")

    st.markdown("---")

    st.markdown("### ✨ Capabilities")

    st.markdown("""
    - 🔎 Semantic paper search
    - 🧠 AI research assistance
    - 📄 Evidence retrieval
    - 📌 Source tracking
    - 📊 Research comparison
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):

        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style="color:#64748b; font-size:12px; margin-top:30px;">
    Powered by Ollama · Llama 3.2<br>
    Local AI Research Assistant
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.header("Upload New Research Paper")

    uploaded_pdf = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_pdf is not None:

        if st.button("Upload and Index Paper"):

            with st.spinner("Processing research paper..."):

                # Create papers folder if it does not exist
                rag.PAPER_FOLDER.mkdir(exist_ok=True)

                # Save uploaded PDF
                pdf_path = rag.PAPER_FOLDER / uploaded_pdf.name

                with open(pdf_path, "wb") as file:
                    file.write(uploaded_pdf.getbuffer())

                # Extract text
                paper_text = read_pdf(pdf_path)

                # Split into chunks
                chunks = rag.split_text(paper_text)

                # Generate embeddings and create records
                new_records = []

                for chunk_index, chunk in enumerate(chunks):

                    embedding = rag.create_embedding(chunk)

                    new_records.append({
                        "source": uploaded_pdf.name,
                        "chunk_index": chunk_index,
                        "text": chunk,
                        "embedding": embedding
                    })

                # Load existing database
                rag.DB_FOLDER.mkdir(exist_ok=True)

                if rag.DB_FILE.exists():

                    with open(
                        rag.DB_FILE,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        records = json.load(file)

                else:
                    records = []

                # Avoid duplicate records for same uploaded paper
                records = [
                    record for record in records
                    if record.get("source") != uploaded_pdf.name
                ]

                # Add new paper chunks
                records.extend(new_records)

                # Save updated database
                with open(
                    rag.DB_FILE,
                    "w",
                    encoding="utf-8"
                ) as file:
                    json.dump(
                        records,
                        file,
                        ensure_ascii=False
                    )

            st.success("Paper uploaded and indexed successfully!")
            st.write("Paper:", uploaded_pdf.name)
            st.write("Chunks created:", len(chunks))
# ==================================================
# HERO HEADER
# ==================================================

st.markdown("""
<div class="hero">
    <div class="hero-label">AI · KNOWLEDGE · DISCOVERY</div>
    <div class="hero-title">Your Research. One Intelligent Workspace.</div>
    <div class="hero-text">
        Explore your research papers, discover insights, compare methods,
        and find evidence — powered by local AI.
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# METRICS
# ==================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">AI ENGINE</div>
        <div class="metric-value">Llama 3.2</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">RETRIEVAL</div>
        <div class="metric-value">Semantic Search</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">KNOWLEDGE SOURCE</div>
        <div class="metric-value">Your Research PDFs</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("## 💬 Research Conversation")

st.markdown(
    "Ask a question or select a research prompt to get started."
)


# ==================================================
# WELCOME PROMPT CARDS
# ==================================================

suggested_question = None

if len(st.session_state.messages) == 0:

    st.markdown("### ✨ Explore your research")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        <div class="prompt-card">
            <div class="prompt-title">🔬 Research Methodologies</div>
            <div class="prompt-desc">
            Explore algorithms, methods, and techniques used in your papers.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Explore algorithms", use_container_width=True):
            suggested_question = "What machine learning algorithms are used in these research papers?"

    with col2:

        st.markdown("""
        <div class="prompt-card">
            <div class="prompt-title">📊 Dataset Analysis</div>
            <div class="prompt-desc">
            Identify datasets and experimental setups used by researchers.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Explore datasets", use_container_width=True):
            suggested_question = "What datasets are used in these research papers?"

    col3, col4 = st.columns(2)

    with col3:

        st.markdown("""
        <div class="prompt-card">
            <div class="prompt-title">🎯 Research Challenges</div>
            <div class="prompt-desc">
            Discover limitations and unresolved challenges.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Find limitations", use_container_width=True):
            suggested_question = "What are the limitations of the methods discussed in these papers?"

    with col4:

        st.markdown("""
        <div class="prompt-card">
            <div class="prompt-title">💡 Research Opportunities</div>
            <div class="prompt-desc">
            Identify research gaps and possible future directions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Discover research gaps", use_container_width=True):
            suggested_question = "What research gaps and future directions can be identified from these papers?"


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):

            with st.expander("📚 View research evidence"):

                for i, item in enumerate(message["sources"], start=1):

                    st.markdown(f"**Evidence {i}**")

                    st.markdown(
                        f"**Paper:** {item['source']}"
                    )

                    if "page_number" in item:
                        st.markdown(
                            f"**Page:** {item['page_number']}"
                        )

                    st.markdown(
                        f"**Similarity:** {item['score']:.4f}"
                    )

                    st.write(item["text"])
                    st.markdown("---")


# ==================================================
# CHAT INPUT
# ==================================================

typed_question = st.chat_input(
    "Ask anything about your research papers..."
)

question = suggested_question or typed_question


# ==================================================
# PROCESS QUESTION
# ==================================================

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Retrieve evidence
    with st.spinner("🔎 Searching your research knowledge base..."):

        results = retrieve_chunks(question, top_k=3)

    # Generate answer
    if not results:

        answer = "I couldn't find relevant evidence in your indexed research papers."

    else:

        context = ""

        for i, item in enumerate(results, start=1):

            context += f"\nEvidence {i}\n"
            context += f"Source: {item['source']}\n"

            if "page_number" in item:
                context += f"Page: {item['page_number']}\n"

            context += f"Text: {item['text']}\n"

        prompt = f"""
You are Scholar AI, an academic research assistant.

Answer using ONLY the retrieved research evidence below.

Question:
{question}

Evidence:
{context}

Instructions:
- Provide a clear, structured academic answer.
- Use headings or bullet points when useful.
- Do not invent facts.
- If the evidence does not contain the answer, state this clearly.
- Cite the paper filename and page number when available.
"""

        with st.spinner("🧠 Analyzing research evidence..."):

            response = ollama.chat(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response["message"]["content"]

    # Display assistant response
    with st.chat_message("assistant"):

        st.markdown(answer)

        if results:

            with st.expander("📚 View research evidence"):

                if results:

                     st.markdown("### 📚 Research Evidence")
                     st.caption(f"{len(results)} relevant passages retrieved")

                     for i, item in enumerate(results, start=1):

                        with st.container(border=True):

                            st.markdown(f"#### 📄 Evidence {i}")

                #
                #  Paper information
                            st.markdown(f"**Source Paper:** `{item['source']}`")

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if "page_number" in item:
                                    st.metric("PDF Page", item["page_number"])
                                else:
                                    st.metric("PDF Page", "N/A")

                            with col2:
                                st.metric("Chunk", item["chunk_index"])

                            with col3:
                                st.metric("Similarity", f"{item['score']:.4f}")

                # Evidence passage
                            with st.expander("🔎 Read supporting passage"):
                                st.markdown(item["text"])

                            st.divider()

        else:
         st.info("No research evidence was retrieved.")
                
    # Store answer and sources
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": results
    })


# ==================================================
# FOOTER
# ==================================================

st.markdown("""
<div class="footer">
SCHOLAR AI · FACULTY RESEARCH ASSISTANT · PRIVATE LOCAL AI
</div>
""", unsafe_allow_html=True)