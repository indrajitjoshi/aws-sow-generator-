import streamlit as st
from datetime import date
import io
import re
import os

# --- FILE PATHING & DIAGRAM MAPPING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOW_DIAGRAM_MAP = {
    "L1 Support Bot POC SOW":
        os.path.join(BASE_DIR, "diagrams", "L1 Support Bot POC SOW.png"),

    "Ready Search POC Scope of Work Document":
        os.path.join(BASE_DIR, "diagrams", "Ready Search POC Scope of Work Document.png"),

    "AI based Image Enhancement POC SOW":
        os.path.join(BASE_DIR, "diagrams", "AI based Image Enhancement POC SOW.png"),

    "Beauty Advisor POC SOW":
        os.path.join(BASE_DIR, "diagrams", "Beauty Advisor POC SOW.png"),

    "AI based Image Inspection POC SOW":
        os.path.join(BASE_DIR, "diagrams", "AI based Image Inspection POC SOW.png"),

    "Gen AI for SOP POC SOW":
        os.path.join(BASE_DIR, "diagrams", "Gen AI for SOP POC SOW.png"),

    "Project Scope Document":
        os.path.join(BASE_DIR, "diagrams", "Project Scope Document.png"),

    "Gen AI Speech To Speech":
        os.path.join(BASE_DIR, "diagrams", "Gen AI Speech To Speech.png"),

    "PoC Scope Document":
        os.path.join(BASE_DIR, "diagrams", "PoC Scope Document.png")
}

# --- CALCULATOR LINK MAPPING ---
CALCULATOR_LINKS = {
    "L1 Support Bot POC SOW": "https://calculator.aws/#/estimate?id=211ea64cba5a8f5dc09805f4ad1a1e598ef5238b",
    "Ready Search POC Scope of Work Document": "https://calculator.aws/#/estimate?id=f8bc48f1ae566b8ea1241994328978e7e86d3490",
    "AI based Image Enhancement POC SOW": "https://calculator.aws/#/estimate?id=9a3e593b92b796acecf31a78aec17d7eb957d1e5",
    "Beauty Advisor POC SOW": "https://calculator.aws/#/estimate?id=3f89756a35f7bac7b2cd88d95f3e9aba9be9b0eb",
    "AI based Image Inspection POC SOW": "https://calculator.aws/#/estimate?id=72c56f93b0c0e101d67a46af4f4fe9886eb93342",
    "Gen AI for SOP POC SOW": "https://calculator.aws/#/estimate?id=c21e9b242964724bf83556cfeee821473bb935d1",
    "Project Scope Document": "https://calculator.aws/#/estimate?id=37339d6e34c73596559fe09ca16a0ac2ec4c4252",
    "Gen AI Speech To Speech": "https://calculator.aws/#/estimate?id=8444ae26e6d61e5a43e8e743578caa17fd7f3e69",
    "PoC Scope Document": "https://calculator.aws/#/estimate?id=420ed9df095e7824a144cb6c0e9db9e7ec3c4153"
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

# --- CACHED UTILITIES ---
def create_docx_logic(text_content, branding_info, sow_type_name):
    """
    Generates the Word document with strict page isolation and markdown cleanup.
    """
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    import docx.oxml.shared
    import docx.opc.constants

    def add_hyperlink(paragraph, text, url):
        # Helper to add hyperlinks to docx paragraphs
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

    doc = Document()
    
    # --- PAGE 1: COVER PAGE ---
    if branding_info.get('aws_pn_logo_bytes'):
        p_top = doc.add_paragraph()
        p_top.alignment = WD_ALIGN_PARAGRAPH.LEFT
        try:
            run = p_top.add_run()
            run.add_picture(io.BytesIO(branding_info['aws_pn_logo_bytes']), width=Inches(1.0))
        except:
            p_top.add_run("aws partner network").bold = True

    doc.add_paragraph("\n" * 3)
    
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(branding_info['sow_name'])
    run.font.size = Pt(26)
    run.font.bold = True
    
    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle_p.add_run("Scope of Work Document")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    
    doc.add_paragraph("\n" * 4)
    
    logo_table = doc.add_table(rows=1, cols=3)
    logo_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    def insert_logo_to_cell(cell, bytes_data, width_val, fallback_text):
        cell.paragraphs[0].text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if bytes_data:
            try:
                p.add_run().add_picture(io.BytesIO(bytes_data), width=Inches(width_val))
            except:
                p.add_run(fallback_text).bold = True
        else:
            p.add_run(fallback_text).bold = True

    insert_logo_to_cell(logo_table.rows[0].cells[0], branding_info.get('customer_logo_bytes'), 1.4, "[Customer Logo]")
    insert_logo_to_cell(logo_table.rows[0].cells[1], branding_info.get('oneture_logo_bytes'), 2.2, "ONETURE")
    insert_logo_to_cell(logo_table.rows[0].cells[2], branding_info.get('aws_adv_logo_bytes'), 1.3, "AWS Advanced")

    doc.add_paragraph("\n" * 4)
    
    date_p = doc.add_paragraph()
    date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = date_p.add_run(branding_info['doc_date_str'])
    run.font.size = Pt(12)
    run.font.bold = True
    
    doc.add_page_break()
    
    # --- CONTENT PROCESSING ---
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    lines = text_content.split('\n')
    i = 0
    in_toc_section = False
    toc_already_added = False
    overview_started = False

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            if i > 0 and lines[i-1].strip():
                doc.add_paragraph("")
            i += 1
            continue

        line_clean = re.sub(r'\*+', '', line).strip()
        clean_text = re.sub(r'^#+\s*', '', line_clean).strip()
        upper_text = clean_text.upper()

        # Trigger for Section 4: Insert Architecture Diagram
        if "4 SOLUTION ARCHITECTURE" in upper_text and (line.startswith('#') or line.startswith('4')):
            doc.add_heading(clean_text, level=1)
            diagram_path = SOW_DIAGRAM_MAP.get(sow_type_name)
            if diagram_path and os.path.exists(diagram_path):
                doc.add_paragraph("")
                try:
                    doc.add_picture(diagram_path, width=Inches(6.0))
                    p_cap = doc.add_paragraph(f"{sow_type_name} – Architecture Diagram")
                    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                except:
                    doc.add_paragraph("[Architecture Diagram - Missing or Incompatible Format]")
                doc.add_paragraph("")
            i += 1
            continue

        if ("2 PROJECT OVERVIEW" in upper_text) and (line.startswith('#') or line.startswith('2')) and not overview_started:
            doc.add_page_break()
            in_toc_section = False
            overview_started = True
            doc.add_heading(clean_text, level=1)
            i += 1
            continue

        if "1 TABLE OF CONTENTS" in upper_text:
            if not toc_already_added:
                in_toc_section = True
                toc_already_added = True
                doc.add_heading("1 TABLE OF CONTENTS", level=1)
            i += 1
            continue

        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 3:
                data_lines = [l for l in table_lines if not set(l).issubset({'|', '-', ' ', ':'})]
                if len(data_lines) >= 2:
                    headers = [c.strip() for c in data_lines[0].split('|') if c.strip()]
                    table = doc.add_table(rows=1, cols=len(headers))
                    table.style = 'Table Grid'
                    hdr_cells = table.rows[0].cells
                    for idx, h in enumerate(headers):
                        hdr_cells[idx].text = h
                    for row_str in data_lines[1:]:
                        row_cells = table.add_row().cells
                        r_data = [c.strip() for c in row_str.split('|') if c.strip()]
                        for idx, c_text in enumerate(r_data):
                            if idx < len(row_cells):
                                # Check for "Estimate" to insert hyperlink
                                if "Estimate" in c_text:
                                    p = row_cells[idx].paragraphs[0]
                                    prefix = c_text.replace("Estimate", "").strip()
                                    if prefix:
                                        p.add_run(prefix + " ")
                                    calc_url = CALCULATOR_LINKS.get(sow_type_name, "https://calculator.aws")
                                    add_hyperlink(p, "Estimate", calc_url)
                                else:
                                    row_cells[idx].text = c_text
                doc.add_paragraph("")
            continue

        if line.startswith('# '):
            doc.add_heading(clean_text, level=1)
        elif line.startswith('## '):
            p = doc.add_heading(clean_text, level=2)
            if in_toc_section:
                p.paragraph_format.left_indent = Inches(0.4)
        elif line.startswith('### '):
            p = doc.add_heading(clean_text, level=3)
            if in_toc_section:
                p.paragraph_format.left_indent = Inches(0.8)
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = re.sub(r'^[-*]\s*', '', clean_text)
            p = doc.add_paragraph(bullet_text, style='List Bullet')
            if in_toc_section:
                p.paragraph_format.left_indent = Inches(0.4)
        else:
            p = doc.add_paragraph(clean_text)
            if in_toc_section and len(clean_text) > 3 and clean_text[0].isdigit():
                 p.paragraph_format.left_indent = Inches(0.4)
            
            # Segregation bolding logic for all key sections and stakeholder sub-headers
            segregation_keywords = [
                "PARTNER EXECUTIVE SPONSOR", "CUSTOMER EXECUTIVE SPONSOR", 
                "AWS EXECUTIVE SPONSOR", "PROJECT ESCALATION CONTACTS",
                "DEPENDENCIES:", "ASSUMPTIONS:", "SPONSOR:", "CONTACTS:"
            ]
            if any(key in upper_text for key in segregation_keywords):
                if p.runs:
                    p.runs[0].bold = True
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

    sow_type_options = list(SOW_DIAGRAM_MAP.keys())
    selected_sow_name = st.selectbox("1.1 Scope of Work Type", sow_type_options)

    # Sidebar architecture preview
    st.divider()
    st.header("🧩 Architecture Preview")
    diagram_path_sidebar = SOW_DIAGRAM_MAP.get(selected_sow_name)
    if diagram_path_sidebar and os.path.exists(diagram_path_sidebar):
        st.image(diagram_path_sidebar, caption="Architecture Diagram", use_container_width=True)
    else:
        st.warning("No architecture diagram available.")

    st.divider()
    industry_options = ["Retail / E-commerce", "BFSI", "Manufacturing", "Telecom", "Healthcare", "Energy / Utilities", "Logistics", "Media", "Government", "Other (specify)"]
    industry_type = st.selectbox("1.2 Industry / Domain", industry_options)
    final_industry = st.text_input("Specify Industry", placeholder="Enter industry...") if industry_type == "Other (specify)" else industry_type

    duration = st.text_input("Timeline / Duration", "4 Weeks")
    
    if st.button("🗑️ Reset All Fields", on_click=clear_sow, use_container_width=True):
        st.rerun()

# --- MAIN UI ---
st.title("🚀 GenAI Scope of Work Architect")

# --- STEP 0: COVER PAGE BRANDING ---
st.header("📸 Cover Page Branding")
brand_col1, brand_col2 = st.columns(2)
with brand_col1:
    aws_pn_logo = st.file_uploader("Top Left: AWS Partner Network Logo", type=['png', 'jpg', 'jpeg'], key="aws_pn")
    customer_logo = st.file_uploader("Slot 1: Customer Logo", type=['png', 'jpg', 'jpeg'], key="cust_logo")

with brand_col2:
    oneture_logo = st.file_uploader("Slot 2: Oneture Logo", type=['png', 'jpg', 'jpeg'], key="one_logo")
    aws_adv_logo = st.file_uploader("Slot 3: AWS Advanced Logo", type=['png', 'jpg', 'jpeg'], key="aws_adv")
    doc_date = st.date_input("Document Date", date.today())

st.divider()

# --- STEP 2: OBJECTIVES & STAKEHOLDERS ---
st.header("2. Objectives & Stakeholders")

st.subheader("🎯 2.1 Objective")
objective = st.text_area(
    "Define the core business objective:", 
    placeholder="e.g., Development of a Gen AI based WIMO Bot to demonstrate feasibility...",
    height=120
)
outcomes = st.multiselect(
    "Select success metrics:", 
    ["Reduced Response Time", "Automated SOP Mapping", "Cost Savings", "Higher Accuracy", "Metadata Richness", "Revenue Growth", "Security Compliance", "Scalability", "Integration Feasibility"],
    default=["Higher Accuracy", "Cost Savings"]
)

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
            
            def get_md(df):
                return df.to_markdown(index=False)

            prompt_text = f"""
            Generate a COMPLETE formal enterprise Scope of Work (SOW) for {selected_sow_name} in {final_industry}.
            
            STRICT PAGE & SECTION FLOW:
            1 TABLE OF CONTENTS (Indented sub-items)
            2 PROJECT OVERVIEW
              2.1 OBJECTIVE (Strictly 2-3 lines based on user input: {objective})
              2.2 PROJECT SPONSOR(S) / STAKEHOLDER(S) / PROJECT TEAM
                  You MUST display the following FOUR sections clearly and distinctly, each with its own heading followed by the corresponding table:
                  ### Partner Executive Sponsor
                  {get_md(st.session_state.stakeholders["Partner"])}
                  
                  ### Customer Executive Sponsor
                  {get_md(st.session_state.stakeholders["Customer"])}
                  
                  ### AWS Executive Sponsor
                  {get_md(st.session_state.stakeholders["AWS"])}
                  
                  ### Project Escalation Contacts
                  {get_md(st.session_state.stakeholders["Escalation"])}
              2.3 ASSUMPTIONS & DEPENDENCIES
              2.4 PoC Success Criteria
            3 SCOPE OF WORK – TECHNICAL PROJECT PLAN
            4 SOLUTION ARCHITECTURE / ARCHITECTURAL DIAGRAM
            5 COST ESTIMATION TABLE
            6 RESOURCES & COST ESTIMATES

            CRITICAL INSERTION RULE (DO NOT VIOLATE):
            Immediately AFTER the section "4 SOLUTION ARCHITECTURE / ARCHITECTURAL DIAGRAM" and BEFORE the section "6 RESOURCES & COST ESTIMATES", you MUST insert a section titled "5 COST ESTIMATION TABLE" with the following table:
            
            | SystemInfra Cost / month | AWS Calculator Cost |
            | POC Development | $2,993.60 USD Estimate |

            Note: In the second row, the word "Estimate" is the designated placeholder for the link.

            CONTENT REQUIREMENTS FOR 2.4 (PoC Success Criteria):
            Strictly include these 5 outcomes:
            1. Accurate Compliance Validation: Accurate detection of compliance/non-compliance against design guidelines; identification of errors (blocking) vs warnings (quality).
            2. Structured Metadata (Tags) Extraction: Auto-generation of tags including compliance status, CTA type, Offer type, Products shown, Brands shown, and Brand ambassador presence.
            3. Ad Score Generation: Working framework (0-100) reflecting quality and compliance.
            4. Recommendations & Feedback: Clear actionable recommendations (e.g. "increase resolution") aligned with guidelines.
            5. Usability & Workflow Demonstration: Seamless end-to-end flow: Upload -> Compliance -> Summary -> Score -> Recommendations.

            CONTENT REQUIREMENTS FOR 3 (SCOPE OF WORK - TECHNICAL PROJECT PLAN):
            Strictly include these 4 phases:
            1. Infrastructure Setup: Setup AWS services (Bedrock, S3, Lambda, etc.) and gather samples/guidelines.
            2. Create Core Workflows: Banner Upload & Validation, Compliance & Tagging Flow, Issue Detection & Recommendation Flow, Ad Scoring Flow.
            3. Backend Components: Implement Compliance Engine, build Tagging Module, and store in Amazon S3.
            4. Testing and Feedback: Create PoC UI, validate accuracy against manual reviewer results, and gather stakeholder feedback.

            CONTENT RULES:
            - Section 4 must include the text: "Specifics to be discussed basis POC".
            - NO filler text or introductory sentences between headers.
            - Remove ALL markdown bolding marks (**) inside headings or body text.
            - Use plain text output only.

            INPUT DETAILS:
            - SOW Document Type: {selected_sow_name}
            - Timeline: {duration}
            
            Tone: Professional consulting. Output: Markdown only.
            """
            
            payload = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "systemInstruction": {"parts": [{"text": "You are a senior Solutions Architect. You generate detailed SOW documents. Strictly follow numbering and flow. Ensure stakeholder sections in 2.2 are distinct with their own sub-headers and tables. Sections 2.4 and 3 must be comprehensive as described. No markdown bolding."}]}
            }
            
            try:
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    st.session_state.generated_sow = res.json()['candidates'][0]['content']['parts'][0]['text']
                    st.balloons()
                else:
                    st.error(f"API Error: {res.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- STEP 3: REVIEW & EXPORT ---
if st.session_state.generated_sow:
    st.divider()
    st.header("3. Review & Export")
    tab_edit, tab_preview = st.tabs(["✍️ Document Editor", "📄 Visual Preview"])
    
    with tab_edit:
        st.session_state.generated_sow = st.text_area(
            label="Modify generated content:", 
            value=st.session_state.generated_sow, 
            height=700, 
            key="sow_editor"
        )
    
    with tab_preview:
        st.markdown(f'<div class="sow-preview">', unsafe_allow_html=True)
        header_pattern = r'(?i)(^#*\s*4\s+SOLUTION ARCHITECTURE.*)'
        match = re.search(header_pattern, st.session_state.generated_sow, re.MULTILINE)
        
        preview_text = st.session_state.generated_sow
        # Handle the dynamic link in HTML preview
        calc_url_preview = CALCULATOR_LINKS.get(selected_sow_name, "https://calculator.aws")
        preview_text = preview_text.replace("Estimate", f'<a href="{calc_url_preview}" target="_blank">Estimate</a>')

        if match:
            start, end = match.span()
            st.markdown(preview_text[:end], unsafe_allow_html=True)
            diagram_path_out = SOW_DIAGRAM_MAP.get(selected_sow_name)
            if diagram_path_out and os.path.exists(diagram_path_out):
                st.image(diagram_path_out, caption=f"{selected_sow_name} Architecture", use_container_width=True)
            st.markdown(preview_text[end:], unsafe_allow_html=True)
        else:
            st.markdown(preview_text, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    
    if st.button("💾 Prepare Microsoft Word Document"):
        branding_info = {
            'sow_name': selected_sow_name,
            'aws_pn_logo_bytes': aws_pn_logo.getvalue() if aws_pn_logo else None,
            'customer_logo_bytes': customer_logo.getvalue() if customer_logo else None,
            'oneture_logo_bytes': oneture_logo.getvalue() if oneture_logo else None,
            'aws_adv_logo_bytes': aws_adv_logo.getvalue() if aws_adv_logo else None,
            'doc_date_str': doc_date.strftime("%d %B %Y")
        }
        
        docx_data = create_docx_logic(st.session_state.generated_sow, branding_info, selected_sow_name)
        
        st.download_button(
            label="📥 Download Now (.docx)", 
            data=docx_data, 
            file_name=f"SOW_{selected_sow_name.replace(' ', '_')}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            use_container_width=True
        )
