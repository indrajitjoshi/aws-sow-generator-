import streamlit as st
from datetime import date
import io
import re
import os

# --- FILE PATHING & DIAGRAM MAPPING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "diagrams")

# Static assets
AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

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
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    h1, h2, h3 { color: #0f172a; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
    [data-testid="stExpander"] { border: none; box-shadow: none; background: transparent; }
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

# WORD – COST TABLE
def add_infra_cost_table(doc, sow_type_name, text_content):
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    cost_data = SOW_COST_TABLE_MAP.get(sow_type_name)
    if not cost_data:
        return

    # Determine calculator link
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
    if "poc_cost" in cost_data:
        rows_to_add.append(("POC", cost_data["poc_cost"]))
    if "prod_cost" in cost_data:
        rows_to_add.append(("Production", cost_data["prod_cost"]))
    if "amazon_bedrock" in cost_data:
        rows_to_add.append(("Amazon Bedrock", cost_data["amazon_bedrock"]))
    if "total" in cost_data:
        rows_to_add.append(("Total", cost_data["total"]))

    for label, cost in rows_to_add:
        r = table.add_row().cells
        r[0].text = label
        r[1].text = cost
        # Add hyperlinked "Estimate" or "Link"
        p = r[2].paragraphs[0]
        add_hyperlink(p, "Estimate", calc_url)

    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# --- CACHED UTILITIES ---
def create_docx_logic(text_content, branding_info, sow_type_name):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    architecture_rendered = False
    cost_table_rendered = False

    # --- PAGE 1: COVER PAGE ---
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if os.path.exists(AWS_PN_LOGO):
        doc.add_picture(AWS_PN_LOGO, width=Inches(1.6))

    doc.add_paragraph("\n" * 3)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(branding_info['sow_name'])
    run.font.size = Pt(26)
    run.bold = True

    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_p.add_run("Scope of Work Document").font.size = Pt(14)

    doc.add_paragraph("\n" * 4)

    logo_table = doc.add_table(rows=1, cols=3)
    logo_table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Customer Logo
    cell = logo_table.rows[0].cells[0]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if branding_info.get("customer_logo_bytes"):
        cell.paragraphs[0].add_run().add_picture(io.BytesIO(branding_info["customer_logo_bytes"]), width=Inches(1.8))
    else:
        cell.paragraphs[0].add_run("Customer Logo").bold = True

    # Oneture Logo
    cell = logo_table.rows[0].cells[1]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(ONETURE_LOGO):
        cell.paragraphs[0].add_run().add_picture(ONETURE_LOGO, width=Inches(2.2))

    # AWS Advanced Tier
    cell = logo_table.rows[0].cells[2]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(AWS_ADV_LOGO):
        cell.paragraphs[0].add_run().add_picture(AWS_ADV_LOGO, width=Inches(1.8))

    doc.add_paragraph("\n" * 3)
    date_p = doc.add_paragraph()
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_p.add_run(branding_info["doc_date_str"]).bold = True

    doc.add_page_break()

    # --- CONTENT PROCESSING ---
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    lines = text_content.split('\n')
    i = 0
    in_toc_section = False
    toc_already_added = False

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if i > 0 and lines[i-1].strip(): doc.add_paragraph("")
            i += 1
            continue

        line_clean = re.sub(r'\*+', '', line).strip()
        clean_text = re.sub(r'^#+\s*', '', line_clean).strip()
        upper_text = clean_text.upper()

        # ---------------- SECTION 1: TOC ----------------
        if "1 TABLE OF CONTENTS" in upper_text:
            if not toc_already_added:
                doc.add_heading("1 TABLE OF CONTENTS", level=1)
                toc_already_added = True
                in_toc_section = True
            i += 1
            continue

        # Check if TOC ended
        if in_toc_section and "2 PROJECT OVERVIEW" in upper_text:
            in_toc_section = False
            doc.add_page_break() # TOC on its own page

        # ---------------- SECTION 4: ARCHITECTURE ----------------
        if not in_toc_section and not architecture_rendered and "4 SOLUTION ARCHITECTURE" in upper_text:
            architecture_rendered = True
            doc.add_heading(clean_text, level=1)
            diagram_path = SOW_DIAGRAM_MAP.get(sow_type_name)
            if diagram_path and os.path.exists(diagram_path):
                doc.add_paragraph("")
                doc.add_picture(diagram_path, width=Inches(6.0))
                cap = doc.add_paragraph(f"{sow_type_name} – Architecture Diagram")
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1
            continue

        # ---------------- SECTION 5: COST TABLE ----------------
        if not in_toc_section and not cost_table_rendered and "5 COST ESTIMATION TABLE" in upper_text:
            cost_table_rendered = True
            doc.add_heading(clean_text, level=1)
            add_infra_cost_table(doc, sow_type_name, text_content)
            i += 1
            continue

        # ---------------- TABLE PARSING ----------------
        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            if len(table_lines) >= 3:
                headers = [c.strip() for c in table_lines[0].split('|') if c.strip()]
                table = doc.add_table(rows=1, cols=len(headers))
                table.style = "Table Grid"
                for idx, h in enumerate(headers): table.rows[0].cells[idx].text = h
                for row_line in table_lines[2:]:
                    row_cells = table.add_row().cells
                    cells = [c.strip() for c in row_line.split('|') if c.strip()]
                    for idx, c in enumerate(cells):
                        if idx < len(row_cells): row_cells[idx].text = c
            continue

        # ---------------- HEADINGS ----------------
        if line.startswith('# '):
            doc.add_heading(clean_text, level=1)
        elif line.startswith('## '):
            h = doc.add_heading(clean_text, level=2)
            if in_toc_section: h.paragraph_format.left_indent = Inches(0.4)
        elif line.startswith('### '):
            h = doc.add_heading(clean_text, level=3)
            if in_toc_section: h.paragraph_format.left_indent = Inches(0.8)
        
        # ---------------- BULLETS ----------------
        elif line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(clean_text[2:], style="List Bullet")
            if in_toc_section: p.paragraph_format.left_indent = Inches(0.4)
        
        # ---------------- NORMAL TEXT ----------------
        else:
            p = doc.add_paragraph(clean_text)
            segregation_keywords = ["PARTNER EXECUTIVE SPONSOR", "CUSTOMER EXECUTIVE SPONSOR", "AWS EXECUTIVE SPONSOR", "PROJECT ESCALATION CONTACTS", "ASSUMPTIONS", "DEPENDENCIES"]
            if any(k in upper_text for k in segregation_keywords):
                if p.runs: p.runs[0].bold = True
        i += 1
            
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- INITIALIZATION ---
if 'generated_sow' not in st.session_state:
    st.session_state.generated_sow = ""

if 'stakeholders' not in st.session_state:
    import pandas as pd
    st.session_state.stakeholders = {
        "Partner": pd.DataFrame([{"Name": "Gaurav Kankaria", "Title": "Head of Analytics & ML", "Email": "gaurav.kankaria@oneture.com"}]),
        "Customer": pd.DataFrame([{"Name": "Cheten Dev", "Title": "Head of Product Design", "Email": "cheten.dev@nykaa.com"}]),
        "AWS": pd.DataFrame([{"Name": "Anubhav Sood", "Title": "AWS Account Executive", "Email": "anbhsood@amazon.com"}]),
        "Escalation": pd.DataFrame([
            {"Name": "Omkar Dhavalikar", "Title": "AI/ML Lead", "Email": "omkar.dhavalikar@oneture.com"},
            {"Name": "Gaurav Kankaria", "Title": "Head of Analytics and AIML", "Email": "gaurav.kankaria@oneture.com"}
        ])
    }

def clear_sow():
    st.session_state.generated_sow = ""

# --- SIDEBAR: PROJECT INTAKE ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("SOW Architect")
    st.caption("Enterprise POC/MVP Engine")
    
    with st.expander("🔑 API Key", expanded=False):
        api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("📋 1. Project Intake")
    sow_type_options = list(SOW_COST_TABLE_MAP.keys())
    selected_sow_name = st.selectbox("1.1 Scope of Work Type", sow_type_options)

    st.divider()
    industry_options = ["Retail / E-commerce", "BFSI", "Manufacturing", "Telecom", "Healthcare", "Energy / Utilities", "Logistics", "Media", "Government", "Other (specify)"]
    industry_type = st.selectbox("1.2 Industry / Domain", industry_options)
    final_industry = st.text_input("Specify Industry", placeholder="Enter industry...") if industry_type == "Other (specify)" else industry_type
    duration = st.text_input("Timeline / Duration", "4 Weeks")
    
    if st.button("🗑️ Reset All Fields", on_click=clear_sow, use_container_width=True):
        st.rerun()

# --- MAIN UI ---
st.title("🚀 GenAI Scope of Work Architect")
st.header("📸 Cover Page Branding")
customer_logo = st.file_uploader("Upload Customer Logo (Optional)", type=["png", "jpg", "jpeg"])
doc_date = st.date_input("Document Date", date.today())
st.divider()

st.header("2. Objectives & Stakeholders")
st.subheader("🎯 2.1 Objective")
objective = st.text_area("Define the core business objective:", placeholder="e.g., Development of a Gen AI based WIMO Bot...", height=120)
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

# --- GENERATION ---
if st.button("✨ Generate SOW Document", type="primary", use_container_width=True):
    if not api_key:
        st.warning("⚠️ Enter a Gemini API Key in the sidebar.")
    elif not objective:
        st.error("⚠️ Business Objective is required.")
    else:
        import requests
        with st.spinner(f"Architecting {selected_sow_name}..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
            def get_md(df): return df.to_markdown(index=False)
            prompt_text = f"""
            Generate a COMPLETE formal enterprise SOW for {selected_sow_name} in {final_industry}.
            
            STRICT PAGE & SECTION FLOW:
            1 TABLE OF CONTENTS
            2 PROJECT OVERVIEW
              2.1 OBJECTIVE: {objective}
              2.2 PROJECT TEAM:
                  ### Partner Executive Sponsor
                  {get_md(st.session_state.stakeholders["Partner"])}
                  ### Customer Executive Sponsor
                  {get_md(st.session_state.stakeholders["Customer"])}
                  ### AWS Executive Sponsor
                  {get_md(st.session_state.stakeholders["AWS"])}
                  ### Project Escalation Contacts
                  {get_md(st.session_state.stakeholders["Escalation"])}
              2.3 ASSUMPTIONS & DEPENDENCIES (Separate 2-5 bullet points for each)
              2.4 Project Success Criteria
            3 SCOPE OF WORK - TECHNICAL PROJECT PLAN
            4 SOLUTION ARCHITECTURE / ARCHITECTURAL DIAGRAM
            5 COST ESTIMATION TABLE
            6 RESOURCES & COST ESTIMATES

            RULES:
            - Section 4 must include: "Specifics to be discussed basis POC".
            - Section 5 must include: "Placeholder for Cost Table".
            - No markdown bolding marks (**). Output: Markdown only.
            """
            payload = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "systemInstruction": {"parts": [{"text": "You are a senior Solutions Architect. Strictly follow numbering and flow. No markdown bolding."}]}
            }
            try:
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    st.session_state.generated_sow = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.balloons()
                else: st.error(f"API Error: {res.text}")
            except Exception as e: st.error(f"Error: {str(e)}")

# --- STEP 3: REVIEW & EXPORT ---
if st.session_state.generated_sow:
    st.divider()
    st.header("3. Review & Export")
    tab_edit, tab_preview = st.tabs(["✍️ Document Editor", "📄 Visual Preview"])
    with tab_edit:
        st.session_state.generated_sow = st.text_area(label="Modify content:", value=st.session_state.generated_sow, height=700, key="sow_editor")
    with tab_preview:
        st.markdown(f'<div class="sow-preview">', unsafe_allow_html=True)
        # Visual diagram logic
        header_pattern = r'(?i)(^#*\s*4\s+SOLUTION ARCHITECTURE.*)'
        match = re.search(header_pattern, st.session_state.generated_sow, re.MULTILINE)
        if match:
            start, end = match.span()
            st.markdown(st.session_state.generated_sow[:end])
            diagram_path_out = SOW_DIAGRAM_MAP.get(selected_sow_name)
            if diagram_path_out and os.path.exists(diagram_path_out):
                st.image(diagram_path_out, caption=f"{selected_sow_name} Architecture", use_container_width=True)
            st.markdown(st.session_state.generated_sow[end:])
        else:
            st.markdown(st.session_state.generated_sow)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾 Prepare Microsoft Word Document"):
        branding_info = {
            "sow_name": selected_sow_name,
            "customer_logo_bytes": customer_logo.getvalue() if customer_logo else None,
            "doc_date_str": doc_date.strftime("%d %B %Y")
        }
        docx_data = create_docx_logic(st.session_state.generated_sow, branding_info, selected_sow_name)
        st.download_button(label="📥 Download Now (.docx)", data=docx_data, file_name=f"SOW_{selected_sow_name.replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
