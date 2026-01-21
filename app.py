import streamlit as st
from datetime import date
import io, re, os, time, requests
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config("GenAI SOW Architect", layout="wide", page_icon="📄")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "diagrams")

AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

# ---------------- COST & DIAGRAM MAPS ----------------
SOW_COST_TABLE_MAP = {
    "L1 Support Bot POC SOW": {"POC Cost": "3,536.40 USD"},
    "Beauty Advisor POC SOW": {
        "POC Cost": "4,725.66 USD",
        "Production Cost": "5,701.48 USD"
    },
    "Ready Search POC Scope of Work Document": {"POC Cost": "2,641.40 USD"},
    "AI based Image Enhancement POC SOW": {"POC Cost": "2,814.34 USD"},
    "AI based Image Inspection POC SOW": {"POC Cost": "3,536.40 USD"},
    "Gen AI for SOP POC SOW": {"POC Cost": "2,110.30 USD"},
    "Project Scope Document": {"Production Cost": "2,993.60 USD"},
    "Gen AI Speech To Speech": {"Production Cost": "2,124.23 USD"},
    "PoC Scope Document": {"Total": "3,150 USD"}
}

CALCULATOR_LINKS = {
    k: "https://calculator.aws/"
    for k in SOW_COST_TABLE_MAP.keys()
}

SOW_DIAGRAM_MAP = {
    k: os.path.join(ASSETS_DIR, f"{k}.png")
    for k in SOW_COST_TABLE_MAP.keys()
}

# ---------------- STYLES ----------------
st.markdown("""
<style>
.sow-preview {
    background:white;
    padding:40px;
    border-radius:12px;
    border:1px solid #e2e8f0;
    font-family: "Times New Roman";
    line-height:1.7;
}
.sow-preview a { color:black; text-decoration:underline; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------
def init_state():
    if "generated_sow" not in st.session_state:
        st.session_state.generated_sow = ""
    if "stakeholders" not in st.session_state:
        st.session_state.stakeholders = {
            "Partner": pd.DataFrame([{"Name": "", "Title": "", "Email": ""}]),
            "Customer": pd.DataFrame([{"Name": "", "Title": "", "Email": ""}]),
            "AWS": pd.DataFrame([{"Name": "", "Title": "", "Email": ""}]),
            "Escalation": pd.DataFrame([{"Name": "", "Title": "", "Email": ""}])
        }
    if "timeline" not in st.session_state:
        st.session_state.timeline = pd.DataFrame(
            [{"Phase": "Infra Setup", "Week": "Week 1"}]
        )

init_state()

# ---------------- GEMINI CALL ----------------
def call_gemini(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{
                "text": "Enterprise AWS Solutions Architect. Strict section order 1-10. Capital titles. No fluff."
            }]
        }
    }
    r = requests.post(url, json=payload, timeout=90)
    if r.status_code != 200:
        raise Exception(r.text)
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("Architect Pro")
    api_key = st.text_input("Gemini API Key", type="password")

    sow_key = st.selectbox(
        "Solution Type",
        list(SOW_COST_TABLE_MAP.keys())
    )

# ---------------- MAIN INPUTS ----------------
st.title("🚀 GenAI Scope of Work Architect")

doc_date = st.date_input("Document Date", date.today())
biz_objective = st.text_area("Business Objective", height=120)

st.header("Stakeholders")
for k in st.session_state.stakeholders:
    st.subheader(k)
    st.session_state.stakeholders[k] = st.data_editor(
        st.session_state.stakeholders[k],
        num_rows="dynamic",
        use_container_width=True
    )

st.header("Timeline")
st.session_state.timeline = st.data_editor(
    st.session_state.timeline,
    num_rows="dynamic",
    use_container_width=True
)

# ---------------- GENERATE ----------------
if st.button("✨ Generate Full SOW", type="primary", use_container_width=True):
    if not api_key:
        st.error("API Key required")
    else:
        with st.spinner("Generating SOW..."):
            def md(df): return df.to_markdown(index=False)

            cost_md = "| Item | Cost | AWS |\n|---|---|---|\n"
            for k, v in SOW_COST_TABLE_MAP[sow_key].items():
                cost_md += f"| {k} | {v} | Estimate |\n"

            prompt = f"""
1 TABLE OF CONTENTS

2 PROJECT OVERVIEW
Objective: {biz_objective}

Stakeholders:
Partner
{md(st.session_state.stakeholders["Partner"])}

Customer
{md(st.session_state.stakeholders["Customer"])}

AWS
{md(st.session_state.stakeholders["AWS"])}

Escalation
{md(st.session_state.stakeholders["Escalation"])}

3 ASSUMPTIONS & DEPENDENCIES

4 POC SUCCESS CRITERIA

5 SCOPE OF WORK – FUNCTIONAL CAPABILITIES

6 SOLUTION ARCHITECTURE

7 ARCHITECTURE & AWS SERVICES

8 NON-FUNCTIONAL REQUIREMENTS

9 TIMELINE & PHASING
{md(st.session_state.timeline)}

10 FINAL OUTPUTS

Pricing:
{cost_md}
"""
            st.session_state.generated_sow = call_gemini(api_key, prompt)
            st.rerun()

# ---------------- REVIEW & EXPORT ----------------
if st.session_state.generated_sow:
    t1, t2 = st.tabs(["✍️ Editor", "📄 Visual Preview"])

    with t1:
        st.session_state.generated_sow = st.text_area(
            "Modify Content",
            st.session_state.generated_sow,
            height=600
        )

    with t2:
        html = st.session_state.generated_sow.replace(
            "Estimate",
            f'<a href="{CALCULATOR_LINKS[sow_key]}" target="_blank">Estimate</a>'
        )
        st.markdown(f"<div class='sow-preview'>{html}</div>", unsafe_allow_html=True)

        diag = SOW_DIAGRAM_MAP.get(sow_key)
        if diag and os.path.exists(diag):
            st.image(diag, caption=f"{sow_key} Architecture Diagram")

    if st.button("💾 Prepare Microsoft Word"):
        from docx import Document
        from docx.shared import Inches

        doc = Document()
        doc.add_heading(sow_key, 0)

        for line in st.session_state.generated_sow.split("\n"):
            doc.add_paragraph(line)

        if diag and os.path.exists(diag):
            doc.add_picture(diag, width=Inches(6))

        buf = io.BytesIO()
        doc.save(buf)

        st.download_button(
            "📥 Download SOW (.docx)",
            buf.getvalue(),
            f"SOW_{sow_key.replace(' ', '_')}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
