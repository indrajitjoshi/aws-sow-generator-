import streamlit as st
from datetime import date
import io, os, requests

# ================= SAFE DIAGRAM IMPORT =================
DIAGRAMS_AVAILABLE = True
try:
    from diagrams import Diagram, Cluster
    from diagrams.aws.general import User
    from diagrams.aws.compute import Lambda, EC2
    from diagrams.aws.ml import Bedrock, Textract, Rekognition
    from diagrams.aws.storage import S3
    from diagrams.aws.analytics import OpenSearchService, KinesisDataStreams
    from diagrams.aws.database import RDS
    from diagrams.aws.iot import IotCore
except Exception:
    DIAGRAMS_AVAILABLE = False
# ======================================================

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="GenAI SOW Architect",
    layout="wide",
    page_icon="📄"
)

# ================= ARCHITECTURE MAP =================
ARCH_PATTERN_MAP = {
    "Multi Agent Store Advisor": "AGENTIC_RAG",
    "Agentic AI L1 Support": "AGENTIC_RAG",
    "Sales Co-Pilot": "AGENTIC_RAG",
    "Research Co-Pilot": "AGENTIC_RAG",
    "SOP Creation": "AGENTIC_RAG",

    "Intelligent Search": "RAG_TEXT",
    "Document / Report Audit": "RAG_TEXT",
    "Customer Review Analysis": "RAG_TEXT",

    "Virtual Data Analyst (Text to SQL)": "TEXT_TO_SQL",

    "Recommendation": "RECOMMENDER",
    "AI Agents Demand Forecasting": "RECOMMENDER",

    "Banner Audit using LLM": "VISION_LLM",
    "Image Enhancement": "VISION_LLM",
    "Virtual Try-On": "VISION_LLM",

    "Multilingual Voice Bot": "VOICE_AI",

    "AIoT based CCTV Surveillance": "IOT_STREAM"
}

# ================= ARCH SPEC =================
def generate_architecture_spec(solution):
    pattern = ARCH_PATTERN_MAP.get(solution, "RAG_TEXT")

    return {
        "title": f"{solution} – AWS Architecture",
        "pattern": pattern,
        "vector": pattern in ["RAG_TEXT", "AGENTIC_RAG"],
        "vision": pattern == "VISION_LLM",
        "voice": pattern == "VOICE_AI",
        "iot": pattern == "IOT_STREAM"
    }

# ================= DIAGRAM RENDER =================
def render_architecture_diagram(spec):
    if not DIAGRAMS_AVAILABLE:
        return None

    filename = f"architecture_{spec['title'].replace(' ', '_')}"

    with Diagram(spec["title"], filename=filename, show=False, direction="LR"):
        user = User("User")

        with Cluster("AWS Cloud"):
            ui = EC2("Web / App UI")
            orchestrator = Lambda("Orchestration")
            llm = Bedrock("Amazon Bedrock")

            user >> ui >> orchestrator >> llm

            if spec["vector"]:
                vector = OpenSearchService("Vector DB")
                orchestrator >> vector >> orchestrator

            if spec["vision"]:
                vision = Rekognition("Vision AI")
                orchestrator >> vision >> orchestrator

            if spec["voice"]:
                stream = KinesisDataStreams("Voice Stream")
                orchestrator >> stream >> orchestrator

            if spec["iot"]:
                iot = IotCore("IoT Core")
                orchestrator >> iot >> orchestrator

            store = S3("Data Lake")
            db = RDS("Metadata DB")

            orchestrator >> store
            orchestrator >> db
            orchestrator >> ui

    return f"{filename}.png"

# ================= DOCX =================
def create_docx(text, diagram_path, solution):
    from docx import Document
    from docx.shared import Inches

    doc = Document()
    doc.add_heading(solution, 0)
    doc.add_paragraph("Scope of Work")
    doc.add_paragraph(date.today().strftime("%d %B %Y"))
    doc.add_page_break()

    for line in text.split("\n"):
        doc.add_paragraph(line)

    doc.add_page_break()
    doc.add_heading("4 SOLUTION ARCHITECTURE", 1)

    if diagram_path and os.path.exists(diagram_path):
        doc.add_picture(diagram_path, width=Inches(6.5))

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ================= SESSION =================
if "sow" not in st.session_state:
    st.session_state.sow = ""

# ================= SIDEBAR =================
with st.sidebar:
    st.title("GenAI SOW Architect")

    api_key = st.text_input("Gemini API Key", type="password")

    solution = st.selectbox("Solution Type", list(ARCH_PATTERN_MAP.keys()))
    industry = st.selectbox("Industry", ["Retail", "BFSI", "Healthcare", "Manufacturing"])
    engagement = st.selectbox("Engagement Type", ["PoC", "Pilot", "MVP", "Production"])

# ================= MAIN =================
st.title("🚀 GenAI Scope of Work Architect")

objective = st.text_area("2.1 Define the core business objective:", height=120)

if st.button("✨ Generate SOW + Architecture", use_container_width=True):
    if not api_key or not objective:
        st.error("API Key and Objective required.")
    else:
        with st.spinner("Generating..."):

            prompt = f"""
Generate a professional enterprise Scope of Work.

Structure:
1 TABLE OF CONTENTS
2 PROJECT OVERVIEW
2.1 OBJECTIVE
2.2 STAKEHOLDERS
2.3 ASSUMPTIONS & DEPENDENCIES
3 SCOPE OF WORK
4 SOLUTION ARCHITECTURE
5 COST ESTIMATES

Solution: {solution}
Industry: {industry}
Engagement: {engagement}
Objective: {objective}

Rules:
- Plain text
- Strict numbering
"""

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload).json()

            st.session_state.sow = res["candidates"][0]["content"]["parts"][0]["text"]

            spec = generate_architecture_spec(solution)
            st.session_state.diagram = render_architecture_diagram(spec)

# ================= OUTPUT =================
if st.session_state.sow:
    st.divider()
    st.text_area("Generated SOW", st.session_state.sow, height=500)

if "diagram" in st.session_state and st.session_state.diagram:
    st.image(st.session_state.diagram, use_column_width=True)

    docx = create_docx(
        st.session_state.sow,
        st.session_state.diagram,
        solution
    )

    st.download_button(
        "📥 Download SOW (.docx)",
        data=docx,
        file_name=f"SOW_{solution.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
