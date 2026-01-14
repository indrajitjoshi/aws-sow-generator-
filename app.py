import streamlit as st
from datetime import date
import io
import re
import os
import requests

# ============================================================
# AWS DIAGRAMS (SAFE, OPTIONAL, NON-BREAKING ADD-ON)
# ============================================================
AWS_DIAGRAMS_AVAILABLE = True
try:
    from diagrams import Diagram, Cluster
    from diagrams.aws.general import User
    from diagrams.aws.compute import Lambda, EC2
    from diagrams.aws.ml import Bedrock, Textract, Rekognition
    from diagrams.aws.storage import S3
    from diagrams.aws.analytics import OpenSearchService
    from diagrams.aws.database import RDS
except Exception:
    AWS_DIAGRAMS_AVAILABLE = False
# ============================================================


# --- CONFIGURATION ---
st.set_page_config(
    page_title="GenAI SOW Architect",
    layout="wide",
    page_icon="📄",
    initial_sidebar_state="expanded"
)

# Custom CSS for an Enterprise UI
st.markdown("""
<style>
.main { background-color: #f8fafc; }
.stButton>button { border-radius: 8px; font-weight: 600; }
.stTextArea textarea { border-radius: 10px; }
.stTextInput input { border-radius: 8px; }
.block-container { padding-top: 1.5rem; }
.sow-preview {
    background-color: white;
    padding: 40px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.7;
    color: #1e293b;
}
</style>
""", unsafe_allow_html=True)

# --- DOCX GENERATION (UNCHANGED) ---
def create_docx_logic(text_content, branding_info):
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(branding_info["solution_name"])
    run.bold = True
    run.font.size = Pt(26)

    doc.add_paragraph("\nScope of Work\n").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(branding_info["doc_date_str"]).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    for line in text_content.split("\n"):
        doc.add_paragraph(line)

    if branding_info.get("architecture_diagram") and os.path.exists(branding_info["architecture_diagram"]):
        doc.add_page_break()
        doc.add_heading("Solution Architecture", level=1)
        doc.add_picture(branding_info["architecture_diagram"], width=Inches(6.5))

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


# ============================================================
# AWS ARCHITECTURE GENERATOR (ADD-ON ONLY)
# ============================================================
def generate_aws_architecture_diagram(solution_name):
    if not AWS_DIAGRAMS_AVAILABLE:
        return None

    file_name = f"aws_arch_{solution_name.replace(' ', '_')}"

    with Diagram(
        name=f"{solution_name} – AWS Architecture",
        filename=file_name,
        show=False,
        direction="LR"
    ):
        user = User("End User")

        with Cluster("AWS Cloud (Customer VPC)"):
            ui = EC2("Web / App UI")
            orchestrator = Lambda("GenAI Orchestrator")
            llm = Bedrock("Amazon Bedrock (LLM)")
            vector = OpenSearchService("Vector Store")
            docs = S3("Documents")
            db = RDS("Metadata DB")

            user >> ui >> orchestrator >> llm
            orchestrator >> vector >> orchestrator
            orchestrator >> docs
            orchestrator >> db
            orchestrator >> ui

    return f"{file_name}.png"
# ============================================================


# --- INITIALIZATION ---
if "generated_sow" not in st.session_state:
    st.session_state.generated_sow = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("SOW Architect")
    api_key = st.text_input("Gemini API Key", type="password")

    solution_options = [
        "Multi Agent Store Advisor", "Intelligent Search", "Recommendation",
        "AI Agents Demand Forecasting", "Banner Audit using LLM", "Image Enhancement",
        "Virtual Try-On", "Agentic AI L1 Support", "Product Listing Standardization",
        "AI Agents Based Pricing Module", "Cost, Margin Visibility & Insights using LLM",
        "AI Trend Simulator", "Virtual Data Analyst (Text to SQL)",
        "Multilingual Call Analysis", "Customer Review Analysis",
        "Sales Co-Pilot", "Research Co-Pilot", "Product Copy Generator",
        "Multi-agent e-KYC & Onboarding", "Document / Report Audit",
        "RBI Circular Scraping & Insights Bot", "Visual Inspection",
        "AIoT based CCTV Surveillance", "Multilingual Voice Bot",
        "SOP Creation", "Other"
    ]

    final_solution = st.selectbox("Solution Type", solution_options)
    engagement_type = st.selectbox("Engagement Type", ["PoC", "Pilot", "MVP", "Production"])
    industry = st.selectbox("Industry", ["Retail", "BFSI", "Healthcare", "Manufacturing"])

# --- MAIN ---
st.title("🚀 GenAI Scope of Work Architect")

objective = st.text_area(
    "Define the core business objective:",
    height=120,
    placeholder="e.g. Build an AI-powered WIMO bot..."
)

# --- GENERATE ---
if st.button("✨ Generate SOW Document", type="primary", use_container_width=True):
    if not api_key or not objective:
        st.error("API Key and Objective required.")
    else:
        with st.spinner("Generating SOW..."):
            prompt = f"""
Generate a professional enterprise Scope of Work.

Mandatory structure:
1 TABLE OF CONTENTS
2 PROJECT OVERVIEW
2.1 OBJECTIVE
2.2 STAKEHOLDERS
2.3 ASSUMPTIONS & DEPENDENCIES
3 SCOPE OF WORK
4 SOLUTION ARCHITECTURE
5 COST ESTIMATES

Solution: {final_solution}
Industry: {industry}
Engagement: {engagement_type}
Objective: {objective}

Rules:
- Plain text
- Strict numbering
"""

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload)

            if res.status_code == 200:
                st.session_state.generated_sow = res.json()["candidates"][0]["content"]["parts"][0]["text"]

                # 🔹 AWS DIAGRAM HOOK (ADD-ON ONLY)
                st.session_state.aws_diagram = generate_aws_architecture_diagram(final_solution)
            else:
                st.error("LLM generation failed")

# --- REVIEW ---
if st.session_state.generated_sow:
    st.divider()
    st.subheader("Generated SOW")
    st.text_area("", st.session_state.generated_sow, height=600)

    # 🔹 AWS DIAGRAM DISPLAY (ADD-ON ONLY)
    if "aws_diagram" in st.session_state and st.session_state.aws_diagram:
        st.divider()
        st.subheader("🧱 Auto-Generated AWS Architecture")
        st.image(st.session_state.aws_diagram, use_column_width=True)

    if st.button("📥 Download Word Document"):
        branding_info = {
            "solution_name": final_solution,
            "doc_date_str": date.today().strftime("%d %B %Y"),
            "architecture_diagram": st.session_state.get("aws_diagram")
        }

        docx_data = create_docx_logic(st.session_state.generated_sow, branding_info)

        st.download_button(
            "Download .docx",
            docx_data,
            file_name=f"SOW_{final_solution.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
