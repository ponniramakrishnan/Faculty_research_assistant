
import streamlit as st
import subprocess
from pathlib import Path
import json

# -----------------------------------------
# PROJECT CONFIGURATION
# -----------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent
REPORT_FOLDER = PROJECT_FOLDER / "reports"
PAPERS_FOLDER = PROJECT_FOLDER / "papers"

PYTHON_EXE = PROJECT_FOLDER / ".venv" / "Scripts" / "python.exe"

st.set_page_config(
    page_title="Faculty Research Assistant",
    page_icon="🎓",
    layout="wide"
)


# -----------------------------------------
# DASHBOARD HEADER
# -----------------------------------------

st.title("🎓 Faculty Research Assistant")
st.caption("AI-powered academic research automation system")

st.markdown("---")

st.info(
    "Upload research papers, analyze literature, "
    "discover research gaps, and generate research ideas."
)


# -----------------------------------------
# SAVE UPLOADED PAPERS
# -----------------------------------------

def save_uploaded_papers(uploaded_files):

    PAPERS_FOLDER.mkdir(exist_ok=True)

    saved_files = []
    skipped_files = []

    for uploaded_file in uploaded_files:

        # Protect against path-containing filenames
        safe_filename = Path(uploaded_file.name).name

        file_path = PAPERS_FOLDER / safe_filename

        # Skip existing files to avoid overwriting
        if file_path.exists():

            skipped_files.append(safe_filename)
            continue

        try:

            with open(file_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            saved_files.append(safe_filename)

        except Exception as error:

            st.error(f"Could not save {safe_filename}: {error}")

    if saved_files:

        st.success(
            f"Successfully saved {len(saved_files)} PDF(s)."
        )

    if skipped_files:

        st.warning(
            "Skipped existing files: "
            + ", ".join(skipped_files)
        )

    return saved_files


# -----------------------------------------
# AGENT EXECUTION FUNCTION
# -----------------------------------------

def run_agent(script_name):

    script_path = PROJECT_FOLDER / script_name

    if not PYTHON_EXE.exists():
        return "ERROR: Virtual environment Python not found."

    if not script_path.exists():
        return f"ERROR: {script_name} not found."

    try:

        result = subprocess.run(
            [
                str(PYTHON_EXE),
                str(script_path)
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_FOLDER,
            encoding="utf-8",
            errors="replace",
            timeout=1800
        )

        output = result.stdout

        if result.stderr:

            output += "\n\nERROR / WARNINGS:\n" + result.stderr

        if result.returncode == 0:

            output += "\n\nAgent finished successfully."

        else:

            output += (
                f"\n\nAgent failed. Exit code: "
                f"{result.returncode}"
            )

        return output

    except subprocess.TimeoutExpired:

        return "Agent timed out after 30 minutes."

    except Exception as error:

        return f"Execution error: {error}"


# -----------------------------------------
# FILE STATUS FUNCTION
# -----------------------------------------

def file_status(file_path):

    if file_path.exists():

        size_kb = file_path.stat().st_size / 1024

        return f"✅ Available ({size_kb:.1f} KB)"

    return "❌ Not generated yet"


# -----------------------------------------
# LIST AVAILABLE PDF PAPERS
# -----------------------------------------

def list_papers():

    PAPERS_FOLDER.mkdir(exist_ok=True)

    pdf_files = list(PAPERS_FOLDER.glob("*.pdf"))

    if not pdf_files:

        st.info("No research PDFs uploaded yet.")

    else:

        st.write(f"**PDFs available for analysis: {len(pdf_files)}**")

        for pdf in pdf_files:

            st.write(f"📄 {pdf.name}")


# -----------------------------------------
# TABS
# -----------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Paper Comparison",
        "🔍 Research Gap Analysis",
        "💡 Research Ideas",
        "📁 Project Status"
    ]
)


# =========================================
# TAB 1: PAPER COMPARISON + UPLOAD
# =========================================

with tab1:

    st.header("Paper Comparison Agent")

    st.write(
        "Upload research PDFs at runtime. "
        "The agent extracts research information and "
        "generates a comparative analysis."
    )

    # Runtime PDF uploader
    uploaded_files = st.file_uploader(
        "📤 Upload Research Papers (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        key="research_pdf_upload"
    )

    if uploaded_files:

        st.write(
            f"**Selected files: {len(uploaded_files)}**"
        )

        for uploaded_file in uploaded_files:

            st.write(f"📄 {uploaded_file.name}")

    st.markdown("---")

    st.subheader("Papers in Research Folder")

    list_papers()

    st.markdown("---")

    st.write(
        "**Output:** Word comparison report and JSON data"
    )

    # Run Comparison Agent
    if st.button(
        "▶ Save Uploaded PDFs & Run Comparison Agent",
        key="comparison_button"
    ):

        # Save newly uploaded files first
        if uploaded_files:

            save_uploaded_papers(uploaded_files)

        # Then run the comparison agent
        with st.spinner(
            "Analyzing research papers using Llama 3.2..."
        ):

            output = run_agent("comparison_generator.py")

        st.session_state["comparison_output"] = output

        # Refresh to show newly saved PDFs and reports
        st.rerun()

    # Display execution output
    if "comparison_output" in st.session_state:

        st.subheader("Execution Output")

        st.code(
            st.session_state["comparison_output"],
            language="text"
        )

    st.markdown("---")

    comparison_doc = (
        REPORT_FOLDER / "Research_Comparison_Table.docx"
    )

    json_file = REPORT_FOLDER / "research_papers.json"

    col1, col2 = st.columns(2)

    # Word Report
    with col1:

        st.subheader("Word Comparison Report")

        st.write(file_status(comparison_doc))

        if comparison_doc.exists():

            with open(comparison_doc, "rb") as file:

                st.download_button(
                    label="⬇ Download Word Report",
                    data=file.read(),
                    file_name=comparison_doc.name,
                    mime=(
                        "application/vnd.openxmlformats-officedocument"
                        ".wordprocessingml.document"
                    ),
                    key="download_comparison"
                )

    # JSON Data
    with col2:

        st.subheader("Structured JSON Data")

        st.write(file_status(json_file))

        if json_file.exists():

            try:

                with open(
                    json_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    papers = json.load(file)

                st.metric(
                    "Successfully analyzed papers",
                    len(papers)
                )

                with st.expander("View extracted paper data"):

                    st.json(papers)

            except Exception as error:

                st.error(f"Could not read JSON file: {error}")


# =========================================
# TAB 2: RESEARCH GAP ANALYSIS
# =========================================

with tab2:

    st.header("Research Gap Analysis Agent")

    st.write(
        "Analyzes the comparison JSON and identifies "
        "common limitations and research opportunities."
    )

    st.markdown(
        "**Input:** `research_papers.json`"
    )

    st.markdown(
        "**Output:** `Research_Gap_Analysis.md`"
    )

    if st.button(
        "▶ Run Gap Analysis Agent",
        key="gap_button"
    ):

        with st.spinner(
            "Analyzing cross-paper research gaps..."
        ):

            output = run_agent("gap_agent.py")

        st.session_state["gap_output"] = output

    if "gap_output" in st.session_state:

        st.subheader("Execution Output")

        st.code(
            st.session_state["gap_output"],
            language="text"
        )

    st.markdown("---")

    gap_file = (
        REPORT_FOLDER / "Research_Gap_Analysis.md"
    )

    st.subheader("Gap Analysis Report")

    st.write(file_status(gap_file))

    if gap_file.exists():

        gap_content = gap_file.read_text(
            encoding="utf-8"
        )

        st.download_button(
            label="⬇ Download Gap Report",
            data=gap_content,
            file_name=gap_file.name,
            mime="text/markdown",
            key="download_gap"
        )

        with st.expander(
            "📖 View Research Gap Analysis",
            expanded=True
        ):

            st.markdown(gap_content)


# =========================================
# TAB 3: RESEARCH IDEA GENERATOR
# =========================================

with tab3:

    st.header("Research Idea Generator Agent")

    st.write(
        "Generates potential research directions "
        "using the research gap analysis."
    )

    st.markdown(
        "**Input:** `Research_Gap_Analysis.md`"
    )

    st.markdown(
        "**Output:** `Research_Ideas.md`"
    )

    if st.button(
        "▶ Generate Research Ideas",
        key="idea_button"
    ):

        with st.spinner(
            "Generating research ideas..."
        ):

            output = run_agent(
                "research_idea_agent.py"
            )

        st.session_state["idea_output"] = output

    if "idea_output" in st.session_state:

        st.subheader("Execution Output")

        st.code(
            st.session_state["idea_output"],
            language="text"
        )

    st.markdown("---")

    idea_file = (
        REPORT_FOLDER / "Research_Ideas.md"
    )

    st.subheader("Generated Research Ideas")

    st.write(file_status(idea_file))

    if idea_file.exists():

        idea_content = idea_file.read_text(
            encoding="utf-8"
        )

        st.download_button(
            label="⬇ Download Research Ideas",
            data=idea_content,
            file_name=idea_file.name,
            mime="text/markdown",
            key="download_ideas"
        )

        with st.expander(
            "📖 View Generated Research Ideas",
            expanded=True
        ):

            st.markdown(idea_content)


# =========================================
# TAB 4: PROJECT STATUS
# =========================================

with tab4:

    st.header("Project Status")

    st.write(
        "Monitor the generated files and uploaded "
        "papers in your Faculty Research Assistant."
    )

    st.markdown("---")

    files_to_check = {

        "Comparison Word Report":
            REPORT_FOLDER / "Research_Comparison_Table.docx",

        "Research Papers JSON":
            REPORT_FOLDER / "research_papers.json",

        "Research Gap Report":
            REPORT_FOLDER / "Research_Gap_Analysis.md",

        "Research Ideas Report":
            REPORT_FOLDER / "Research_Ideas.md"
    }

    for name, path in files_to_check.items():

        col1, col2 = st.columns([2, 3])

        with col1:

            st.write(f"**{name}**")

        with col2:

            st.write(file_status(path))

    st.markdown("---")

    st.subheader("Uploaded Research Papers")

    list_papers()

    st.markdown("---")

    if st.button("🔄 Refresh Project Status"):

        st.rerun()

    st.subheader("Project Folders")

    st.code(
        f"Project: {PROJECT_FOLDER}\n"
        f"Papers: {PAPERS_FOLDER}\n"
        f"Reports: {REPORT_FOLDER}",
        language="text"
    )


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.markdown("---")

st.caption(
    "Faculty Research Assistant | "
    "Local LLM powered by Ollama | Llama 3.2"
)
