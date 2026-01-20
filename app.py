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

# Static assets (ensure these files exist in the /diagrams folder)
AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

# Mapped Infra Costs
SOW_COST_TABLE_MAP = { 
    "L1 Support Bot POC SOW": { "poc_cost": "3,536.40 USD" }, 
    "Beauty Advisor POC SOW": { 
        "poc_cost": "4,525.66 USD + 200 USD (Amazon Bedrock Cost) = 4,725.66", 
        "prod_cost": "4,525.66 USD + 1,175.82 USD (Amazon Bedrock Cost) = 5,701.48" 
    }, 
    "Ready Search POC Scope of Work Document":{ "poc_cost": "2,641.40 USD" }, 
    "AI based Image Enhancement POC SOW": { "poc_cost": "2,814.34 USD" }, 
    "AI based Image Inspection POC SOW": { "poc_cost": "3,536.40 USD" }, 
    "Gen AI for SOP POC SOW": { "poc_cost": "2,110.30 USD" }, 
    "Project Scope Document": { "prod_cost": "2,993.60 USD" }, 
    "Gen AI Speech To Speech": { "prod_cost": "2,124.23 USD" }, 
    "PoC Scope Document": { "amazon_bedrock": "1,000 USD", "total": "$ 3,150" }
}

# Mapped Calculator Links
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
    "Ready Search POC Scope of Work Document": os.path.join(ASSETS_DIR, "Ready Search POC Scope of Work Document.png"),
    "AI based Image Enhancement POC SOW": os.path.join(ASSETS_DIR, "AI based Image Enhancement POC SOW.png"),
    "Beauty Advisor POC SOW": os.path.join(ASSETS_DIR, "Beauty Advisor POC SOW.png"),
    "AI based Image Inspection POC SOW": os.path.join(ASSETS_DIR, "AI based Image Inspection POC SOW.png"),
    "Gen AI for SOP POC SOW": os.path.join(ASSETS_DIR, "Gen AI for SOP POC SOW.png"),
    "Project Scope Document": os.path.join(ASSETS_DIR, "Project Scope Document.png"),
    "Gen AI Speech To Speech": os.path.join(ASSETS_DIR, "Gen AI Speech To Speech.png"),
    "PoC Scope Document": os.path.join(ASSETS_DIR, "PoC Scope Document.png")
}

# --- CONFIGURATION ---
st.set_page_config(
    page_title="GenAI SOW Architect", 
    layout="wide", 
    page_icon="📄",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI
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
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    h1, h2, h3 { color: #0f172a; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
    [data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 10px; background: white; margin-bottom: 1rem; }
    .stakeholder-header { 
        background-color: #f1f5f9; 
        padding: 8px 12px; 
        border-radius: 6px; 
        margin-bottom: 10px; 
        font-weight: bold;
        color: #334155;
        border-left: 4px solid #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper for docx hyperlinks
def add_hyperlink(paragraph, text, url):
    import docx.oxml.shared
    import docx.opc.constants
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')
    c = docx.oxml.shared.OxmlElement('w:color')
    c.set(docx.oxml.shared.qn('w:val'), '0000FF')
    u = docx.oxml.shared.OxmlElement('w:u')
    u.set(docx.oxml.shared.qn('w:val'), 'single')
    rPr.append(c)
    rPr.append(u)
    new_run.append(rPr)
    t = docx.oxml.shared.OxmlElement('w:t')
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink

def add_poc_calculation_table(doc):
    doc.add_paragraph("The above numbers are calculated basis the following:")
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Particulars"
    hdr[1].text = "Value (in Dollar)"
    hdr[2].text = "Remarks"
    data = [
        ("Number of documents", "200", "Assuming 5 interactions for finalising each product copy"),
        ("Input Tokens per document", "10,00,000", ""),
        ("Input Token Cost per 1,00,000 Tokens", "0", "Anthropic Claude 3 Sonnet Model"),
        ("Total Input Cost in USD", "600", ""),
        ("Output Tokens per document", "50,000", ""),
        ("Output Token Cost per 1,00,000 Tokens", "0", "Anthropic Claude 3 Sonnet Model"),
        ("Total Output Cost in USD", "150", ""),
        ("Total Cost in USD", "750", ""),
        ("", "", ""),
        ("Tokens for Embedding Model", "2,50,00,00,000", ""),
        ("Input Cost per 1,00,000 Tokens", "0", "Cohere English Model"),
        ("Total Embedding Model Cost in USD", "250", ""),
        ("", "", ""),
        ("Total Cost in USD per month", "1,000", "")
    ]
    for row in data:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = val

def add_infra_cost_table(doc, sow_type_name, text_content):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    cost_data = SOW_COST_TABLE_MAP.get(sow_type_name)
    if not cost_data: return
    calc_url = CALCULATOR_LINKS.get(sow_type_name, "https://calculator.aws/#/")
    if sow_type_name == "Beauty Advisor POC SOW" and "Production Development" in text_content:
        calc_url = CALCULATOR_LINKS["Beauty Advisor Production"]
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "System"
    hdr[1].text = "Infra Cost / month"
    hdr[2].text = "AWS Calculator Cost"
    rows_to_add = []
    if "poc_cost" in cost_data: rows_to_add.append(("POC", cost_data["poc_cost"]))
    if "prod_cost" in cost_data: rows_to_add.append(("Production", cost_data["prod_cost"]))
    if "amazon_bedrock" in cost_data: rows_to_add.append(("Amazon Bedrock", cost_data["amazon_bedrock"]))
    if "total" in cost_data: rows_to_add.append(("Total", cost_data["total"]))
    for label, cost in rows_to_add:
        r = table.add_row().cells
        r[0].text = label
        r[1].text = cost
        p = r[2].paragraphs[0]
        add_hyperlink(p, "Estimate", calc_url)
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if sow_type_name == "PoC Scope Document":
        doc.add_paragraph("")
        add_poc_calculation_table(doc)

def create_docx_logic(text_content, branding_info, sow_type_name):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    doc = Document()
    
    # Render sections tracking (1-11)
    rendered_sections = {str(i): False for i in range(1, 12)}
    
    # --- PAGE 1: COVER PAGE ---
    p_top = doc.add_paragraph()
    if os.path.exists(AWS_PN_LOGO): doc.add_picture(AWS_PN_LOGO, width=Inches(1.6))
    doc.add_paragraph("\n" * 3)
    
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(branding_info['sow_name'])
    run.font.size, run.bold = Pt(26), True
    
    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_p.add_run("Scope of Work Document").font.size = Pt(14)
    
    doc.add_paragraph("\n" * 4)
    
    logo_table = doc.add_table(rows=1, cols=3)
    logo_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Logos
    cell = logo_table.rows[0].cells[0]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if branding_info.get("customer_logo_bytes"): 
        cell.paragraphs[0].add_run().add_picture(io.BytesIO(branding_info["customer_logo_bytes"]), width=Inches(1.8))
    else: 
        cell.paragraphs[0].add_run("Customer Logo").bold = True
    
    cell = logo_table.rows[0].cells[1]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(ONETURE_LOGO): cell.paragraphs[0].add_run().add_picture(ONETURE_LOGO, width=Inches(2.2))
    
    cell = logo_table.rows[0].cells[2]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(AWS_ADV_LOGO): cell.paragraphs[0].add_run().add_picture(AWS_ADV_LOGO, width=Inches(1.8))
    
    doc.add_paragraph("\n" * 3)
    date_p = doc.add_paragraph()
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_p.add_run(branding_info["doc_date_str"]).bold = True
    
    doc.add_page_break()
    
    # --- CONTENT PROCESSING ---
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Arial', Pt(11)
    
    lines = text_content.split('\n')
    i, in_toc_section, content_started = 0, False, False
    
    header_patterns = {
        "1": "1 TABLE OF CONTENTS", 
        "2": "2 PROJECT OVERVIEW", 
        "3": "3 ASSUMPTIONS & DEPENDENCIES", 
        "4": "4 POC SUCCESS CRITERIA",
        "5": "5 SCOPE OF WORK – FUNCTIONAL CAPABILITIES",
        "6": "6 SOLUTION ARCHITECTURE", 
        "7": "7 ARCHITECTURE & AWS SERVICES",
        "8": "8 NON-FUNCTIONAL REQUIREMENTS",
        "9": "9 TIMELINE & PHASING",
        "10": "10 COST ESTIMATION TABLE", 
        "11": "11 RESOURCES & COST ESTIMATES"
    }
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if i > 0 and lines[i-1].strip() and content_started: doc.add_paragraph("")
            i += 1; continue
            
        line_clean = re.sub(r'\*+', '', line).strip()
        clean_text = re.sub(r'^#+\s*', '', line_clean).strip()
        upper_text = clean_text.upper()
        
        # Robust Header Detection
        current_header_id = None
        for h_id, pattern in header_patterns.items():
            core_title = pattern.split(' ', 1)[1]
            if upper_text.startswith(f"{h_id} {core_title}") or upper_text.startswith(f"{h_id}. {core_title}"):
                current_header_id = h_id
                break
        
        # Skip repetitive placeholders generated by AI
        if any(kw in upper_text for kw in ["PLACEHOLDER FOR COST TABLE", "SPECIFICS TO BE DISCUSSED BASIS POC"]):
            i += 1; continue
            
        if not content_started:
            if current_header_id == "1": content_started = True
            else: i += 1; continue
        
        if current_header_id:
            if in_toc_section and current_header_id == "2":
                in_toc_section = False; doc.add_page_break()
            
            if not rendered_sections[current_header_id]:
                doc.add_heading(clean_text, level=1)
                rendered_sections[current_header_id] = True
                if current_header_id == "1": in_toc_section = True
                
                # Injection logic
                if current_header_id == "6":
                    diag = SOW_DIAGRAM_MAP.get(sow_type_name)
                    if diag and os.path.exists(diag):
                        doc.add_paragraph(""); doc.add_picture(diag, width=Inches(6.0))
                        cap = doc.add_paragraph(f"{sow_type_name} – Architecture Diagram")
                        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                if current_header_id == "10": 
                    add_infra_cost_table(doc, sow_type_name, text_content)
            i += 1; continue
            
        # Table Processing (Primarily for Resources section 11 or stakeholder tables in section 2)
        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|'):
            # Resources logic
            if rendered_sections["10"] and not rendered_sections["11"]:
                i += 1; continue # Don't render AI tables if they are redundant cost tables
                
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i]); i += 1
            if len(table_lines) >= 3:
                headers = [c.strip() for c in table_lines[0].split('|') if c.strip()]
                table = doc.add_table(rows=1, cols=len(headers)); table.style = "Table Grid"
                for idx, h in enumerate(headers): table.rows[0].cells[idx].text = h
                for row_line in table_lines[2:]:
                    row_cells = table.add_row().cells
                    cells = [c.strip() for c in row_line.split('|') if c.strip()]
                    for idx, c in enumerate(cells):
                        if idx < len(row_cells): row_cells[idx].text = c
            continue
            
        # Formatting Headings and Bullets
        if line.startswith('## '):
            h = doc.add_heading(clean_text, level=2)
            if in_toc_section: h.paragraph_format.left_indent = Inches(0.4)
        elif line.startswith('### '):
            h = doc.add_heading(clean_text, level=3)
            if in_toc_section: h.paragraph_format.left_indent = Inches(0.8)
        elif line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(clean_text[2:] if (clean_text.startswith('- ') or clean_text.startswith('* ')) else clean_text, style="List Bullet")
            if in_toc_section: p.paragraph_format.left_indent = Inches(0.4)
        else:
            # Skip repetitive architecture descriptions that repeat diagram info
            if "ARCHITECTURE DIAGRAM" in upper_text and rendered_sections["6"] and not rendered_sections["10"]: i += 1; continue
            p = doc.add_paragraph(clean_text)
            bold_kw = ["PARTNER EXECUTIVE SPONSOR", "CUSTOMER EXECUTIVE SPONSOR", "AWS EXECUTIVE SPONSOR", "PROJECT ESCALATION CONTACTS", "ASSUMPTIONS:", "DEPENDENCIES:", "ASSUMPTIONS (", "DEPENDENCIES ("]
            if any(k in upper_text for k in bold_kw) and p.runs: p.runs[0].bold = True
        i += 1
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

def call_gemini_with_retry(api_key, payload):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
    for attempt in range(5):
        try:
            res = requests.post(url, json=payload)
            if res.status_code == 200: return res, None
            if res.status_code in [503, 429]: time.sleep(2**attempt); continue
            return None, f"API Error {res.status_code}: {res.text}"
        except Exception: time.sleep(2**attempt)
    return None, "Model overloaded. Please retry."

# --- INITIALIZATION ---
if 'generated_sow' not in st.session_state: st.session_state.generated_sow = ""
if 'stakeholders' not in st.session_state:
    st.session_state.stakeholders = {
        "Partner": pd.DataFrame([{"Name": "Gaurav Kankaria", "Title": "Head of Analytics & ML", "Email": "gaurav.kankaria@oneture.com"}]),
        "Customer": pd.DataFrame([{"Name": "Cheten Dev", "Title": "Head of Product Design", "Email": "cheten.dev@nykaa.com"}]),
        "AWS": pd.DataFrame([{"Name": "Anubhav Sood", "Title": "AWS Account Executive", "Email": "anbhsood@amazon.com"}]),
        "Escalation": pd.DataFrame([{"Name": "Omkar Dhavalikar", "Title": "AI/ML Lead", "Email": "omkar.dhavalikar@oneture.com"}, {"Name": "Gaurav Kankaria", "Title": "Head of Analytics and AIML", "Email": "gaurav.kankaria@oneture.com"}])
    }
if 'timeline_phases' not in st.session_state:
    st.session_state.timeline_phases = pd.DataFrame([
        {"Phase": "Infra setup", "Week Range": "Week 1"},
        {"Phase": "Core workflows", "Week Range": "Week 2 - 3"},
        {"Phase": "Testing & validation", "Week Range": "Week 3 - 4"},
        {"Phase": "Demo & feedback", "Week Range": "Week 4"}
    ])

def clear_sow(): st.session_state.generated_sow = ""

# --- SIDEBAR: PROJECT INTAKE ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("SOW Architect")
    st.caption("Enterprise POC/MVP Engine")
    with st.expander("🔑 API Key", expanded=False): api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    st.header("📋 1. Project Intake")
    selected_sow_name = st.selectbox("1.1 Scope of Work Type", list(SOW_COST_TABLE_MAP.keys()))
    engagement_type = st.selectbox("1.2 Engagement Type (Closed-ended)", ["Proof of Concept (PoC)", "Pilot", "MVP", "Production Rollout", "Assessment / Discovery", "Support"])
    st.divider()
    industry_options = ["Retail / E-commerce", "BFSI", "Manufacturing", "Telecom", "Healthcare", "Energy / Utilities", "Logistics", "Media", "Government", "Other (specify)"]
    industry_type = st.selectbox("1.3 Industry / Domain", industry_options)
    final_industry = st.text_input("Specify Industry", placeholder="Enter industry...") if industry_type == "Other (specify)" else industry_type
    if st.button("🗑️ Reset All Fields", on_click=clear_sow, use_container_width=True): st.rerun()

# --- MAIN UI ---
st.title("🚀 GenAI Scope of Work Architect")
st.header("📸 Cover Page Branding")
col_cov1, col_cov2 = st.columns(2)
with col_cov1: customer_logo = st.file_uploader("Upload Customer Logo (Optional)", type=["png", "jpg", "jpeg"])
with col_cov2: doc_date = st.date_input("Document Date", date.today())
st.divider()

st.header("2. Objectives & Stakeholders")
st.subheader("🎯 2.1 Objective")
objective = st.text_area("Define the core business objective:", placeholder="e.g., Development of a Gen AI based WIMO Bot...", height=100)
outcomes = st.multiselect("Select success metrics:", ["Reduced Response Time", "Automated SOP Mapping", "Cost Savings", "Higher Accuracy", "Metadata Richness", "Revenue Growth", "Security Compliance", "Scalability", "Integration Feasibility"], default=["Higher Accuracy", "Cost Savings"])
st.divider()

st.subheader("👥 2.2 Project Sponsor(s) / Stakeholder(s) / Project Team")
col_team1, col_team2 = st.columns(2)
with col_team1:
    st.markdown('<div class="stakeholder-header">Partner Executive Sponsor</div>', unsafe_allow_html=True)
    st.session_state.stakeholders["Partner"] = st.data_editor(st.session_state.stakeholders["Partner"], num_rows="dynamic", use_container_width=True, key="ed_partner")
    st.markdown('<div class="stakeholder-header">AWS Executive Sponsor</div>', unsafe_allow_html=True)
    st.session_state.stakeholders["AWS"] = st.data_editor(st.session_state.stakeholders["AWS"], num_rows="dynamic", use_container_width=True, key="ed_aws")
with col_team2:
    st.markdown('<div class="stakeholder-header">Customer Executive Sponsor</div>', unsafe_allow_html=True)
    st.session_state.stakeholders["Customer"] = st.data_editor(st.session_state.stakeholders["Customer"], num_rows="dynamic", use_container_width=True, key="ed_customer")
    st.markdown('<div class="stakeholder-header">Project Escalation Contacts</div>', unsafe_allow_html=True)
    st.session_state.stakeholders["Escalation"] = st.data_editor(st.session_state.stakeholders["Escalation"], num_rows="dynamic", use_container_width=True, key="ed_escalation")

st.divider()
st.header("📋 3. Assumptions & Dependencies (Semi-Structured)")
st.subheader("🔗 3.1 Customer Dependencies")
st.write("Select all that apply:")
dep_options = ["Sample data availability", "Historical data availability", "Design / business guidelines finalized", "API access provided", "User access to AWS account", "SME availability for validation", "Network / VPC access", "Security approvals"]
selected_deps = []
cols_dep = st.columns(2)
for idx, opt in enumerate(dep_options):
    if cols_dep[idx % 2].checkbox(opt, key=f"dep_{idx}"): selected_deps.append(opt)

st.subheader("📊 3.2 Data Characteristics")
data_types = st.multiselect("What type of data is involved?", ["Images", "Text", "PDFs / Documents", "Audio", "Video", "Structured tables", "APIs / Streams"])
data_details = {}
if data_types:
    for dtype in data_types:
        with st.expander(f"⚙️ Details for {dtype}", expanded=True):
            col1, col2, col3 = st.columns(3)
            if dtype == "Images":
                sz = col1.text_input("Avg size (MB)", "2 MB", key="img_sz")
                fmt = col2.text_input("Formats (JPEG/PNG/etc.)", "JPEG, PNG", key="img_fmt")
                vol = col3.text_input("Approx volume (per day / total)", "1000 total", key="img_vol")
                data_details[dtype] = {"Avg Size": sz, "Formats": fmt, "Volume": vol}
            elif dtype == "PDFs / Documents":
                sz = col1.text_input("Avg size (MB)", "5 MB", key="pdf_sz")
                fmt = col2.text_input("Formats", "PDF, DOCX", key="pdf_fmt")
                vol = col3.text_input("Approx volume (per day / total)", "500 total", key="pdf_vol")
                data_details[dtype] = {"Avg Size": sz, "Formats": fmt, "Volume": vol}
            elif dtype == "Text":
                sz = col1.text_input("Avg size (KB/MB)", "100 KB", key="txt_sz")
                fmt = col2.text_input("Formats", "TXT, JSON, CSV", key="txt_fmt")
                vol = col3.text_input("Approx volume (per day / total)", "10,00,0 records", key="txt_vol")
                data_details[dtype] = {"Avg Size": sz, "Formats": fmt, "Volume": vol}
            else:
                sz = col1.text_input("Avg size", "TBD", key=f"gen_sz_{dtype}")
                fmt = col2.text_input("Formats / Specs", "TBD", key=f"gen_fmt_{dtype}")
                vol = col3.text_input("Approx volume", "TBD", key=f"gen_vol_{dtype}")
                data_details[dtype] = {"Avg Size": sz, "Formats": fmt, "Volume": vol}

st.subheader("💡 3.3 Key Assumptions")
assump_options = ["PoC only, not production-grade", "Limited data volume", "Rule-based logic acceptable initially", "Manual review for edge cases", "No real-time SLA commitments"]
selected_assumps = []
cols_as = st.columns(2)
for idx, opt in enumerate(assump_options):
    if cols_as[idx % 2].checkbox(opt, key=f"as_{idx}"): selected_assumps.append(opt)
other_assump = st.text_input("Other (Free text)", placeholder="Enter any other project assumptions...")
if other_assump: selected_assumps.append(other_assump)

st.divider()
st.header("🎯 4. PoC Success Criteria")
st.subheader("📊 4.1 Success Dimensions")
success_dim_options = ["Accuracy", "Latency", "Usability", "Explainability", "Coverage", "Cost efficiency", "Integration readiness"]
selected_dims = st.multiselect("Dimensions:", success_dim_options, default=["Accuracy", "Cost efficiency"])
st.subheader("✅ 4.2 User Validation Requirement")
val_req = st.radio("Customer validation requirement:", ["Yes – customer validation required", "No – internal validation sufficient"])

st.divider()
st.header("🛠️ 5. Scope of Work – Functional Capabilities")
st.subheader("⚙️ 5.1 Core Capabilities")
cap_options = ["Upload / Ingestion", "Processing / Inference", "Metadata extraction", "Scoring / Recommendation", "Feedback loop", "UI display"]
selected_caps = []
cols_cap = st.columns(2)
for idx, opt in enumerate(cap_options):
    if cols_cap[idx % 2].checkbox(opt, value=True, key=f"cap_{idx}"): selected_caps.append(opt)
custom_step = st.text_input("Add custom step (Optional):", placeholder="e.g., Automated reporting module...")
if custom_step: selected_caps.append(custom_step)
st.subheader("🔗 5.2 Integrations Required")
selected_ints = st.multiselect("Select systems to integrate:", ["Internal databases", "External APIs", "CRM", "ERP", "Search engine", "Data warehouse", "None"], default=["None"])

st.divider()
st.header("🏢 6. Architecture & AWS Services")
st.subheader("🖥️ 6.1 Compute & Orchestration")
compute_option = st.multiselect("Select compute & orchestration services:", ["AWS Lambda", "Step Functions", "Amazon ECS / EKS", "Hybrid"], default=["AWS Lambda", "Step Functions"])
st.subheader("🤖 6.2 GenAI / ML Services")
ml_services = st.multiselect("Select AI services:", ["Amazon Bedrock", "Amazon SageMaker", "Amazon Rekognition", "Amazon Textract", "Amazon Comprehend", "Amazon Transcribe", "Amazon Translate"], default=["Amazon Bedrock"])
st.subheader("💾 6.3 Storage & Search")
storage_services = st.multiselect("Select Storage & Search:", ["Amazon S3", "Amazon DynamoDB", "Amazon OpenSearch", "Amazon RDS", "Vector DB (OpenSearch)", "Vector DB (Aurora PG)"], default=["Amazon S3"])

st.divider()
st.header("⚙️ 7. Non-Functional Requirements")
st.subheader("⚡ 7.1 Performance Expectations")
perf_expectation = st.selectbox("Select expected performance profile:", ["Batch", "Near real-time", "Real-time"], index=1)
st.subheader("🛡️ 7.2 Security & Compliance")
sec_compliance = st.multiselect("Select security controls:", ["IAM-based access", "Encryption at rest", "Encryption in transit", "VPC deployment", "Audit logging", "Compliance alignment (RBI, SOC2, etc.)"], default=["IAM-based access", "Encryption at rest", "VPC deployment"])

st.divider()
# --- 8. Timeline & Phasing (Entirely Editable Form) ---
st.header("📅 8. Timeline & Phasing")
col8_1, col8_2 = st.columns([1, 2])
with col8_1:
    st.subheader("⌛ 8.1 PoC Duration")
    poc_duration = st.selectbox("Select PoC duration:", ["2 weeks", "4 weeks", "6 weeks", "Custom"], index=1)
    final_duration = st.text_input("Specify Custom Duration:", "8 weeks") if poc_duration == "Custom" else poc_duration
with col8_2:
    st.subheader("📈 8.2 Phase Breakdown")
    st.write("Editable Phase Breakdown:")
    st.session_state.timeline_phases = st.data_editor(st.session_state.timeline_phases, num_rows="dynamic", use_container_width=True, key="ed_timeline")

# --- GENERATION ---
if st.button("✨ Generate SOW Document", type="primary", use_container_width=True):
    if not api_key: st.warning("⚠️ Enter Gemini API Key.")
    elif not objective: st.error("⚠️ Business Objective required.")
    else:
        with st.spinner(f"Architecting {selected_sow_name}..."):
            def get_md(df): return df.to_markdown(index=False)
            cost_info = SOW_COST_TABLE_MAP.get(selected_sow_name, {})
            dynamic_table_prompt = "| System | Infra Cost / month | AWS Calculator Cost |\n| --- | --- | --- |\n"
            for k, v in cost_info.items():
                label = "POC" if k=="poc_cost" else "Production" if k=="prod_cost" else "Bedrock" if k=="amazon_bedrock" else "Total"
                dynamic_table_prompt += f"| {label} | {v} | Estimate |\n"
            dep_context = "\n".join([f"- {d}" for d in selected_deps])
            as_context = "\n".join([f"- {a}" for a in selected_assumps])
            data_context = "".join([f"- **{dt}**: {', '.join([f'{k}: {v}' for k, v in val.items()])}\n" for dt, val in data_details.items()])
            
            prompt_text = f"""
            Generate a COMPLETE, high-quality formal enterprise SOW for {selected_sow_name} in the {final_industry} industry.
            
            STRICT SECTION FLOW (USE THESE EXACT HEADERS AND NUMBERS):
            1 TABLE OF CONTENTS
            2 PROJECT OVERVIEW (Objective: {objective}. Use these stakeholder tables provided.)
              ### Partner Executive Sponsor
              {get_md(st.session_state.stakeholders["Partner"])}
              ### Customer Executive Sponsor
              {get_md(st.session_state.stakeholders["Customer"])}
              ### Project Escalation Contacts
              {get_md(st.session_state.stakeholders["Escalation"])}
            3 ASSUMPTIONS & DEPENDENCIES
              3.1 Customer Dependencies: {dep_context}
              3.2 Data Characteristics: {data_context}
              3.3 Key Assumptions: {as_context}
            4 POC SUCCESS CRITERIA (Dimensions: {', '.join(selected_dims)}. Requirement: {val_req}.)
            5 SCOPE OF WORK – FUNCTIONAL CAPABILITIES (Flows: {', '.join(selected_caps)}. Integrations: {', '.join(selected_ints)}.)
            6 SOLUTION ARCHITECTURE (ONLY: "Specifics to be discussed basis POC".)
            7 ARCHITECTURE & AWS SERVICES (Compute: {', '.join(compute_option)}. AI: {', '.join(ml_services)}. Storage: {', '.join(storage_services)}.)
            8 NON-FUNCTIONAL REQUIREMENTS (Performance: {perf_expectation}. Security: {', '.join(sec_compliance)}.)
            9 TIMELINE & PHASING (Overall duration: {final_duration}. Phases: {get_md(st.session_state.timeline_phases)}.)
            10 COST ESTIMATION TABLE (Provide strictly this table only: {dynamic_table_prompt})
            11 RESOURCES & COST ESTIMATES

            INSTRUCTIONS:
            - Engagement type '{engagement_type}' drives depth. Use professional Solutions Architect tone.
            - Follow numbering 1 to 11 exactly. No markdown bolding (**). No repetition of headers.
            """
            res, err = call_gemini_with_retry(api_key, {"contents": [{"parts": [{"text": prompt_text}]}], "systemInstruction": {"parts": [{"text": f"AWS Architect. Follow numbering 1 to 11 exactly. Start with '1 TABLE OF CONTENTS'. No repetition."}]}})
            if res:
                st.session_state.generated_sow = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.balloons(); st.rerun()
            else: st.error(err)

# --- STEP 3: REVIEW & EXPORT ---
if st.session_state.generated_sow:
    st.divider(); st.header("3. Review & Export")
    tab_edit, tab_preview = st.tabs(["✍️ Document Editor", "📄 Visual Preview"])
    with tab_edit: 
        st.session_state.generated_sow = st.text_area("Modify:", value=st.session_state.generated_sow, height=600, key="sow_editor")
    with tab_preview:
        st.markdown('<div class="sow-preview">', unsafe_allow_html=True)
        calc_url_p = CALCULATOR_LINKS.get(selected_sow_name, "https://calculator.aws")
        preview_content = st.session_state.generated_sow.replace("Estimate", f'<a href="{calc_url_p}" target="_blank" style="color:#3b82f6; text-decoration: underline;">Estimate</a>')
        
        match = re.search(r'(?i)(^#*\s*6\s+SOLUTION ARCHITECTURE.*)', preview_content, re.MULTILINE)
        if match:
            start, end = match.span(); st.markdown(preview_content[:end], unsafe_allow_html=True)
            diag_out = SOW_DIAGRAM_MAP.get(selected_sow_name)
            if diag_out and os.path.exists(diag_out): st.image(diag_out, caption=f"{selected_sow_name} Architecture", use_container_width=True)
            st.markdown(preview_content[end:], unsafe_allow_html=True)
        else: st.markdown(preview_content, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    if st.button("💾 Prepare Microsoft Word Document"):
        info = {"sow_name": selected_sow_name, "customer_logo_bytes": customer_logo.getvalue() if customer_logo else None, "doc_date_str": doc_date.strftime("%d %B %Y")}
        docx_data = create_docx_logic(st.session_state.generated_sow, info, selected_sow_name)
        st.download_button("📥 Download Now (.docx)", docx_data, f"SOW_{selected_sow_name.replace(' ', '_')}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
