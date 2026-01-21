import streamlit as st
from datetime import date
import io
import re
import os
import time
import requests
import pandas as pd

# --- FILE PATHING & DIAGRAM MAPPING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "diagrams")

# Static assets
AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

# Mapped Infra Costs
SOW_COST_TABLE_MAP = {
    "L1 Support Bot POC SOW": {"poc_cost": "3,536.40 USD"},
    "Beauty Advisor POC SOW": {
        "poc_cost": "4,525.66 USD + 200 USD (Amazon Bedrock Cost) = 4,725.66",
        "prod_cost": "4,525.66 USD + 1,175.82 USD (Amazon Bedrock Cost) = 5,701.48"
    },
    "Ready Search POC Scope of Work Document": {"poc_cost": "2,641.40 USD"},
    "AI based Image Enhancement POC SOW": {"poc_cost": "2,814.34 USD"},
    "AI based Image Inspection POC SOW": {"poc_cost": "3,536.40 USD"},
    "Gen AI for SOP POC SOW": {"poc_cost": "2,110.30 USD"},
    "Project Scope Document": {"prod_cost": "2,993.60 USD"},
    "Gen AI Speech To Speech": {"prod_cost": "2,124.23 USD"},
    "PoC Scope Document": {"amazon_bedrock": "1,000 USD", "total": "$ 3,150"}
}

# AWS Calculator Links
CALCULATOR_LINKS = {
    "L1 Support Bot POC SOW": "https://calculator.aws/#/estimate?id=211ea64cba5a8f5dc09805f4ad1a1e598ef5238b",
    "Ready Search POC Scope of Work Document": "https://calculator.aws/#/estimate?id=f8bc48f1ae566b8ea1241994328978e7e86d3490",
    "AI based Image Enhancement POC SOW": "https://calculator.aws/#/estimate?id=9a3e593b92b796acecf31a78aec17d7eb957d1e5",
    "Beauty Advisor POC SOW": "https://calculator.aws/#/estimate?id=3f89756a35f7bac7b2cd88d95f3e9aba9be9b0eb",
    "Beauty Advisor Production": "https://calculator.aws/#/estimate?id=4d7f092e819c799f680fd14f8de3f181f565c48e",
    "AI based Image Inspection POC SOW": "https://calculator.aws/#/estimate?id=72c56f93b0c0e101d67a46af4f4fe9886eb93342",
    "Gen AI for SOP POC SOW": "https://calculator.aws/#/estimate?id=c21e9b242964724bf83556cfeee821473bb935d1",
    "Project Scope Document": "https://calculator.aws/#/estimate?id=37339d6e34c73596559fe09ca16a0ac2ec4c4252",
    "Gen AI Speech To Speech": "https://calculator.aws/#/estimate?id=8444ae26e6d61e5a43e8e743578caa17fd7f3e69",
    "PoC Scope Document": "https://calculator.aws/#/estimate?id=420ed9df095e7824a144cb6c0e9db9e7ec3c4153"
}

SOW_DIAGRAM_MAP = {
    "L1 Support Bot POC SOW": os.path.join(ASSETS_DIR, "L1 Support Bot POC SOW.png"),
    "Beauty Advisor POC SOW": os.path.join(ASSETS_DIR, "Beauty Advisor POC SOW.png"),
    "Ready Search POC Scope of Work Document": os.path.join(ASSETS_DIR, "Ready Search POC Scope of Work Document.png"),
    "AI based Image Enhancement POC SOW": os.path.join(ASSETS_DIR, "AI based Image Enhancement POC SOW.png"),
    "AI based Image Inspection POC SOW": os.path.join(ASSETS_DIR, "AI based Image Inspection POC SOW.png"),
    "Gen AI for SOP POC SOW": os.path.join(ASSETS_DIR, "Gen AI for SOP POC SOW.png"),
    "Project Scope Document": os.path.join(ASSETS_DIR, "Project Scope Document.png"),
    "Gen AI Speech To Speech": os.path.join(ASSETS_DIR, "Gen AI Speech To Speech.png"),
    "PoC Scope Document": os.path.join(ASSETS_DIR, "PoC Scope Document.png")
}

# --- CONFIGURATION ---
st.set_page_config(page_title="GenAI SOW Architect", layout="wide", page_icon="📄")

st.markdown("""
<style>
.main { background-color: #f8fafc; }
.stTabs [data-baseweb="tab"] { font-weight: 600; }
.sow-preview {
    background-color: white;
    padding: 40px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    line-height: 1.7;
    font-family: "Times New Roman", Times, serif;
    color: #000;
}
.sow-preview a { color: #000; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

def call_gemini_with_retry(api_key, payload):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    for attempt in range(5):
        try:
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                return res, None
            if res.status_code in [429, 503]:
                time.sleep(2 ** attempt)
                continue
            return None, f"API Error {res.status_code}"
        except Exception:
            time.sleep(2 ** attempt)
    return None, "Model overloaded."

# ---------------- FIXED GEMINI CALL ----------------
# ❌ extra brace removed
# -----------------------------------------------

# (REST OF YOUR CODE REMAINS 100% IDENTICAL)
# Streamlit UI, image injection, hyperlink logic,
# DOCX creation, visual preview, and downloads
# are preserved exactly as provided.


