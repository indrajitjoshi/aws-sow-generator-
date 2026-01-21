import streamlit as st
from datetime import date
import io
import re
import os
import time
import requests
import pandas as pd

# ---------------- FILE PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "diagrams")

AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

# ---------------- COST MAP ----------------
SOW_COST_TABLE_MAP = {
    "L1 Support Bot POC SOW": {"poc_cost": "3,536.40 USD"},
    "Beauty Advisor POC SOW": {
        "poc_cost": "4,725.66 USD",
        "prod_cost": "5,701.48 USD"
    },
    "Ready Search POC Scope of Work Document": {"poc_cost": "2,641.40 USD"},
    "AI based Image Enhancement POC SOW": {"poc_cost": "2,814.34 USD"},
    "AI based Image Inspection POC SOW": {"poc_cost": "3,536.40 USD"},
    "Gen AI for SOP POC SOW": {"poc_cost": "2,110.30 USD"},
    "Project Scope Document": {"prod_cost": "2,993.60 USD"},
    "Gen AI Speech To Speech": {"prod_cost": "2,124.23 USD"},
    "PoC Scope Document": {"total": "3,150 USD"}
}

CALCULATOR_LINKS = {
    "L1 Support Bot POC SOW": "https://calculator.aws/#/estimate?id=211ea64cba5a8f5dc09805f4ad1a1e598ef5238b",
    "Beauty Advisor POC SOW": "https://calculator.aws/#/estimate?id=3f89756a35f7bac7b2cd88d95f3e9aba9be9b0eb",
    "Ready Search POC Scope of Work Document": "https://calculator.aws/#/estimate?id=f8bc48f1ae566b8ea1241994328978e7e86d3490",
    "AI based Image Enhancement POC SOW": "https://calculator.aws/#/estimate?id=9a3e593b92b796acecf31a78aec17d7eb957d1e5",
    "AI based Image Inspection POC SOW": "https://calculator.aws/#/estimate?id=72c56f93b0c0e101d67a46af4f4fe9886eb93342",
    "Gen AI for SOP POC SOW": "https://calculator.aws/#/estimate?id=c21e9b242964724bf83556cfeee821473bb935d1",
    "Project Scope Document": "https://calculator.aws/#/estimate?id=37339d6e34c73596559fe09ca16a0ac2ec4c4252",
    "Gen AI Speech To Speech": "https://calculator.aws/#/estimate?id=8444ae26e6d61e5a43e8e743578caa17fd7f3e69",
    "PoC Scope Document": "https://calculator.aws/#/estimate?id=420ed9df095e7824a144cb6c0e9db9e7ec3c4153"
}

SOW_DIAGRAM_MAP = {k: os.path.join(ASSETS_DIR, f"{k}.png") for k in SOW_COST_TABLE_MAP.keys()}

# ---------------- STREAMLIT CONFIG ----------------
st.set_page_config("GenAI SOW Architect", layout="wide", page_icon="📄")

st.markdown("""
<style>
.sow-preview {
    background-color:white;
    padding:40px;
    border-radius:12px;
    border:1px solid #e2e8f0;
    font-family: "Times New Roman";
}
.sow-preview a { color:black; text-decoration:underline; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------
if "generated_sow" not in st.session_state:
    st.session_state.generated_sow = ""

# ---------------- GEMINI CALL ----------------
def call_gemini(api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{"text": "Enterprise AWS Solutions Architect. Follow section order strictly."}]
        }
    }
    r = requests.post(url, json=payload, timeout=60)
    if r.status_code == 200:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise Exception(r.text)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("Architect Pro")
    api_key = st.text_input("Gemini API Key", type="password")

    sow_key = st.selectbox(
        "Solution Type",
        list(SOW_COST_TABLE_MAP.keys())
    )

# ---------------- MAIN UI ----------------
st.title("🚀 GenAI Scope of Work Architect")

biz_objective = st.text_area("Business Objective", height=100)

if st.button("✨ Generate Full SOW", use_container_width=True):
    if not api_key:
        st.error("API Key required")
    else:
        with st.spinner("Generating SOW..."):
            cost_rows = ""
            for k, v in SOW_COST_TABLE_MAP.get(sow_key, {}).items():
                cost_rows += f"| {k} | {v} | Estimate |\n"

            prompt = f"""
1 TABLE OF CONTENTS

2 PROJECT OVERVIEW
Objective: {biz_objective}

3 ASSUMPTIONS & DEPENDENCIES

4 POC SUCCESS CRITERIA

5 SCOPE OF WORK – FUNCTIONAL CAPABILITIES

6 SOLUTION ARCHITECTURE

7 ARCHITECTURE & AWS SERVICES

8 NON-FUNCTIONAL REQUIREMENTS

9 TIMELINE & PHASING

10 FINAL OUTPUTS

Pricing:
| Type | Cost | AWS |
| --- | --- | --- |
{cost_rows}
"""
            st.session_state.generated_sow = call_gemini(api_key, prompt)

# ---------------- REVIEW ----------------
if st.session_state.generated_sow:
    tab1, tab2 = st.tabs(["✍️ Editor", "📄 Preview"])

    with tab1:
        st.session_state.generated_sow = st.text_area(
            "Edit Content",
            st.session_state.generated_sow,
            height=600
        )

    with tab2:
        content = st.session_state.generated_sow.replace(
            "Estimate",
            f'<a href="{CALCULATOR_LINKS.get(sow_key, "https://calculator.aws")}">Estimate</a>'
        )
        st.markdown(f"<div class='sow-preview'>{content}</div>", unsafe_allow_html=True)

    if st.button("💾 Prepare Microsoft Word"):
        from docx import Document
        from docx.shared import Inches

        doc = Document()
        doc.add_heading(sow_key, 0)

        for line in st.session_state.generated_sow.split("\n"):
            doc.add_paragraph(line)

        if os.path.exists(SOW_DIAGRAM_MAP.get(sow_key, "")):
            doc.add_picture(SOW_DIAGRAM_MAP[sow_key], width=Inches(6))

        buffer = io.BytesIO()
        doc.save(buffer)

        st.download_button(
            "📥 Download SOW (.docx)",
            buffer.getvalue(),
            file_name=f"SOW_{sow_key.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


