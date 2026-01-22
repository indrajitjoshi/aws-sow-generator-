import streamlit as st
from datetime import date
import io
import re
import os
import time 
import requests
from PIL import Image
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- FILE PATHING & DIAGRAM MAPPING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check if "diagrams" folder exists, if not, use current directory as fallback
ASSETS_DIR = os.path.join(BASE_DIR, "diagrams")
if not os.path.exists(ASSETS_DIR):
    ASSETS_DIR = BASE_DIR

# Static assets
AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

# Centralized Mapping for Consistency
SOW_DIAGRAM_MAP = {
    "L1 Support Bot POC SOW": "L1 Support Bot POC SOW.png",
    "Beauty Advisor POC SOW": "Beauty Advisor POC SOW.png",
    "Ready Search POC Scope of Work Document": "Ready Search POC Scope of Work Document.png",
    "AI based Image Enhancement POC SOW": "AI based Image Enhancement POC SOW.png",
    "AI based Image Inspection POC SOW": "AI based Image Inspection POC SOW.png",
    "Gen AI for SOP POC SOW": "Gen AI for SOP POC SOW.png",
    "Project Scope Document": "Project Scope Document.png",
    "Gen AI Speech To Speech": "Gen AI Speech To Speech.png",
    "PoC Scope Document": "PoC Scope Document.png"
}

SOW_COST_TABLE_MAP = { 
    "L1 Support Bot POC SOW": { "poc_cost": "3,536.40 USD" }, 
    "Beauty Advisor POC SOW": { 
        "poc_cost": "4,525.66 USD + 200 USD (Bedrock) = 4,725.66", 
        "prod_cost": "4,525.66 USD + 1,175.82 USD (Bedrock) = 5,701.48" 
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

def safe_add_picture(doc, image_path, width):
    """Safely adds a picture to the docx document if it exists and is valid."""
    try:
        if not image_path or not os.path.exists(image_path):
            return False
        with Image.open(image_path) as img:
            img.verify()
        doc.add_picture(image_path, width=width)
        return True
    except Exception as e:
        print(f"[IMAGE ERROR] {image_path}: {e}")
        return False

def add_hyperlink(paragraph, text, url):
    import docx.oxml.shared
    import docx.opc.constants
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id)
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

def add_infra_cost_table(doc, sow_type_name, text_content):
    cost_data = SOW_COST_TABLE_MAP.get(sow_type_name)
    if not cost_data:
        return

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
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

def create_docx_logic(text_content, branding_info, sow_type_name):
    doc = Document()
    
    header_patterns = {
        "1": "1 TABLE OF CONTENTS", "2": "2 PROJECT OVERVIEW", "3": "3 ASSUMPTIONS", 
        "4": "4 PROJECT SUCCESS", "5": "5 SCOPE OF WORK", "6": "6 SOLUTION ARCHITECTURE",
        "7": "7 PERFORMANCE", "8": "8 COST ESTIMATION", "9": "9 RESOURCES", "10": "10 FINAL"
    }

    rendered_sections = {k: False for k in header_patterns.keys()}

    # --- COVER PAGE ---
    p_top = doc.add_paragraph()
    safe_add_picture(doc, AWS_PN_LOGO, Inches(1.6))
    doc.add_paragraph("\n" * 3)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(branding_info['sow_name'])
    run.font.size, run.bold = Pt(26), True

    doc.add_paragraph("\n" * 4)
    logo_table = doc.add_table(rows=1, cols=3)
    
    # Customer Logo
    cell = logo_table.rows[0].cells[0]
    if branding_info.get("customer_logo_bytes"):
        cell.paragraphs[0].add_run().add_picture(io.BytesIO(branding_info["customer_logo_bytes"]), width=Inches(1.8))
    else:
        cell.paragraphs[0].add_run("Customer Logo").bold = True

    # Oneture Logo
    cell = logo_table.rows[0].cells[1]
    safe_add_picture(doc, ONETURE_LOGO, Inches(2.2))

    # AWS Logo
    cell = logo_table.rows[0].cells[2]
    safe_add_picture(doc, AWS_ADV_LOGO, Inches(1.8))

    doc.add_page_break()

    # --- CONTENT PROCESSING ---
    lines = text_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        clean_text = re.sub(r'^#+\s*', '', re.sub(r'\*+', '', line)).strip()
        upper_text = clean_text.upper()

        current_header_id = next((h_id for h_id, pat in header_patterns.items() if pat in upper_text), None)

        if current_header_id:
            if not rendered_sections.get(current_header_id):
                if current_header_id == "2": doc.add_page_break()
                doc.add_heading(clean_text, level=1)
                rendered_sections[current_header_id] = True

                # Image Logic for Word
                if current_header_id == "6":
                    filename = SOW_DIAGRAM_MAP.get(sow_type_name)
                    if filename:
                        path = os.path.join(ASSETS_DIR, filename)
                        if not safe_add_picture(doc, path, Inches(5.8)):
                            doc.add_paragraph("[Architecture Diagram Unavailable]")
                        else:
                            cap = doc.add_paragraph(f"{sow_type_name} – Architecture Diagram")
                            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                if current_header_id == "8":
                    add_infra_cost_table(doc, sow_type_name, text_content)
            i += 1
            continue

        # Normal text/bullets
        if line.startswith('## '): doc.add_heading(clean_text, level=2)
        elif line.startswith('### '): doc.add_heading(clean_text, level=3)
        elif line.startswith(('- ', '* ')): doc.add_paragraph(line[2:], style="List Bullet")
        else: doc.add_paragraph(line)
        i += 1
            
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- STREAMLIT UI CONFIG ---
st.set_page_config(page_title="GenAI SOW Architect", layout="wide", page_icon="📄")

# Initialize State
if 'generated_sow' not in st.session_state: st.session_state.generated_sow = ""
if 'stakeholders' not in st.session_state:
    import pandas as pd
    st.session_state.stakeholders = {
        "Partner": pd.DataFrame([{"Name": "Gaurav Kankaria", "Title": "Head of Analytics & ML", "Email": "gaurav.kankaria@oneture.com"}]),
        "Customer": pd.DataFrame([{"Name": "Cheten Dev", "Title": "Head of Product Design", "Email": "cheten.dev@nykaa.com"}]),
        "AWS": pd.DataFrame([{"Name": "Anubhav Sood", "Title": "AWS Account Executive", "Email": "anbhsood@amazon.com"}]),
        "Escalation": pd.DataFrame([{"Name": "Omkar Dhavalikar", "Title": "AI/ML Lead", "Email": "omkar.dhavalikar@oneture.com"}])
    }

# Sidebar
with st.sidebar:
    st.title("SOW Architect")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    selected_sow_name = st.selectbox("Scope of Work Type", list(SOW_DIAGRAM_MAP.keys()))
    industry = st.text_input("Industry", "Retail")
    duration = st.text_input("Timeline", "4 Weeks")

# Main Page
st.title("GenAI Scope of Work Architect")
customer_logo = st.file_uploader("Upload Customer Logo", type=["png", "jpg"])
objective = st.text_area("Objective", "Development of GenAI solution...")

if st.button("✨ Generate SOW Document", type="primary"):
    if not api_key: st.error("Please enter API Key")
    else:
        with st.spinner("Generating..."):
            # Simple prompt for demo
            prompt = f"Generate a formal enterprise SOW for {selected_sow_name}. Include sections: 1 TOC, 2 Overview, 6 Solution Architecture, 8 Cost Estimation."
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                st.session_state.generated_sow = res.json()['candidates'][0]['content']['parts'][0]['text']
                st.balloons()
            else: st.error("API Error")

# Review & Export
if st.session_state.generated_sow:
    tab_edit, tab_preview = st.tabs(["✍️ Editor", "📄 Preview"])
    
    with tab_edit:
        st.session_state.generated_sow = st.text_area("Edit", value=st.session_state.generated_sow, height=500)
    
    with tab_preview:
        # Display the text
        st.markdown(st.session_state.generated_sow)
        
        # Display image logic - Improved detection
        st.divider()
        st.subheader("Architecture Preview")
        filename = SOW_DIAGRAM_MAP.get(selected_sow_name)
        if filename:
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                st.image(path, caption=f"{selected_sow_name} Diagram", use_container_width=True)
            else:
                st.warning(f"Diagram file missing: {filename}")
        else:
            st.info("No diagram mapped for this type.")

    if st.button("💾 Download Word (.docx)"):
        branding = {"sow_name": selected_sow_name, "customer_logo_bytes": customer_logo.getvalue() if customer_logo else None, "doc_date_str": date.today().strftime("%d %B %Y")}
        data = create_docx_logic(st.session_state.generated_sow, branding, selected_sow_name)
        st.download_button("📥 Download Now", data, file_name="SOW.docx")
