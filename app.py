import streamlit as st
from datetime import date
import io
import re
import os

# --- FILE PATHING & DIAGRAM MAPPING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "diagrams")

AWS_PN_LOGO = os.path.join(ASSETS_DIR, "aws partner logo.jpg")
ONETURE_LOGO = os.path.join(ASSETS_DIR, "oneture logo1.jpg")
AWS_ADV_LOGO = os.path.join(ASSETS_DIR, "aws advanced logo1.jpg")

SOW_COST_TABLE_MAP = { "L1 Support Bot POC SOW": { "poc_cost": "3,536.40 USD", }, 
                      "Beauty Advisor POC SOW": { "poc_cost": "4,525.66 USD + 200 USD (Amazon Bedrock Cost) = 4,725.66", "prod_cost": "4,525.66 USD + 1,175.82 USD (Amazon Bedrock Cost) = 5,701.48" }, 
                      "Ready Search POC Scope of Work Document":{ "poc_cost": "2,641.40 USD" }, 
                      "AI based Image Enhancement POC SOW": { "poc_cost": "2,814.34 USD" }, 
                      "AI based Image Inspection POC SOW": { "poc_cost": "3,536.40 USD" }, 
                      "Gen AI for SOP POC SOW": { "poc_cost": "2,110.30 USD" }, 
                      "Project Scope Document": { "prod_cost": "2,993.60 USD" }, 
                      "Gen AI Speech To Speech": { "prod_cost": "2,124.23 USD" }, 
                      "PoC Scope Document": { "amazon_bedrock": "1,000 USD", "total": "$ 3,150" }, 
                     }

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

# WORD – COST TABLE
# =====================================================
def add_infra_cost_table(doc, sow_type_name):
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    cost_data = SOW_COST_TABLE_MAP.get(sow_type_name)
    if not cost_data:
        return

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "System"
    hdr[1].text = "Infra Cost"
    hdr[2].text = "AWS Cost Calculator"

    aws_link = "https://calculator.aws/#/"

    if "poc_cost" in cost_data:
        r = table.add_row().cells
        r[0].text = "POC"
        r[1].text = cost_data["poc_cost"]
        r[2].text = aws_link

    if "prod_cost" in cost_data:
        r = table.add_row().cells
        r[0].text = "Production"
        r[1].text = cost_data["prod_cost"]
        r[2].text = aws_link

    if "amazon_bedrock" in cost_data:
        r = table.add_row().cells
        r[0].text = "Amazon Bedrock"
        r[1].text = cost_data["amazon_bedrock"]
        r[2].text = aws_link

    if "total" in cost_data:
        r = table.add_row().cells
        r[0].text = "Total"
        r[1].text = cost_data["total"]
        r[2].text = aws_link

    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# --- CACHED UTILITIES ---
def create_docx_logic(text_content, branding_info, sow_type_name):
    """
    Generates the Word document with strict page isolation and markdown cleanup.
    """
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    # --- One-time render guards ---
    architecture_rendered = False
    cost_table_rendered = False


    # Top-left: AWS Partner Network
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.LEFT
    doc.add_picture(AWS_PN_LOGO, width=Inches(1.6))

    doc.add_paragraph("\n" * 3)

    # Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(branding_info['sow_name'])
    run.font.size = Pt(26)
    run.bold = True

    subtitle_p = doc.add_paragraph()
    subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_p.add_run("Scope of Work Document").font.size = Pt(14)

    doc.add_paragraph("\n" * 4)

    # --- LOGO ROW ---
    logo_table = doc.add_table(rows=1, cols=3)
    logo_table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Customer Logo (user uploaded)
    cell = logo_table.rows[0].cells[0]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if branding_info.get("customer_logo_bytes"):
        cell.paragraphs[0].add_run().add_picture(
        io.BytesIO(branding_info["customer_logo_bytes"]),
        width=Inches(1.8)
    )
    else:
        cell.paragraphs[0].add_run("Customer Logo").bold = True

    # Oneture Logo (fixed)
    cell = logo_table.rows[0].cells[1]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell.paragraphs[0].add_run().add_picture(
    ONETURE_LOGO, width=Inches(2.2)
    )

    # AWS Advanced Tier (fixed)
    cell = logo_table.rows[0].cells[2]
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell.paragraphs[0].add_run().add_picture(
    AWS_ADV_LOGO, width=Inches(1.8)
    )

    doc.add_paragraph("\n" * 3)

    # Date
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
            doc.add_paragraph("")
            i += 1
            continue

        line_clean = re.sub(r'\*+', '', line).strip()
        clean_text = re.sub(r'^#+\s*', '', line_clean).strip()
        upper_text = clean_text.upper()

        # ---------------- TOC START ----------------
        if "1 TABLE OF CONTENTS" in upper_text:
            if not toc_already_added:
                doc.add_heading("1 TABLE OF CONTENTS", level=1)
                toc_already_added = True
                in_toc_section = True
            i += 1
            continue

        # ---------------- TOC END ----------------
        if in_toc_section and "2 PROJECT OVERVIEW" in upper_text:
            in_toc_section = False

        # ---------------- SECTION 4 ----------------
        if (
            not in_toc_section
            and not architecture_rendered
            and "4 SOLUTION ARCHITECTURE" in upper_text
            and (line.startswith('#') or line.startswith('4'))
        ):
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



        # ---------------- SECTION 6 ----------------
        if (
            not in_toc_section
            and not cost_table_rendered
            and "6 RESOURCES & COST ESTIMATES" in upper_text
            and (line.startswith('#') or line.startswith('6'))
        ):
            cost_table_rendered = True

            doc.add_heading(clean_text, level=1)
            add_infra_cost_table(doc, sow_type_name)

            i += 1
            continue



        # ---------------- TABLE PARSING ----------------
        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1

            headers = [c.strip() for c in table_lines[0].split('|') if c.strip()]
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = "Table Grid"

            for idx, h in enumerate(headers):
                table.rows[0].cells[idx].text = h

            for row in table_lines[2:]:
                row_cells = table.add_row().cells
                cells = [c.strip() for c in row.split('|') if c.strip()]
                for idx, c in enumerate(cells):
                    row_cells[idx].text = c

            continue

        # ---------------- HEADINGS ----------------
        if line.startswith('# '):
            doc.add_heading(clean_text, level=1)

        elif line.startswith('## '):
            h = doc.add_heading(clean_text, level=2)
            if in_toc_section:
                h.paragraph_format.left_indent = Inches(0.4)

        elif line.startswith('### '):
            h = doc.add_heading(clean_text, level=3)
            if in_toc_section:
                h.paragraph_format.left_indent = Inches(0.8)

        # ---------------- BULLETS ----------------
        elif line.startswith('- ') or line.startswith('* '):
            p = doc.add_paragraph(clean_text[2:], style="List Bullet")
            if in_toc_section:
                p.paragraph_format.left_indent = Inches(0.4)

        # ---------------- NORMAL TEXT ----------------
        else:
            p = doc.add_paragraph(clean_text)

            segregation_keywords = [
                "PARTNER EXECUTIVE SPONSOR",
                "CUSTOMER EXECUTIVE SPONSOR",
                "AWS EXECUTIVE SPONSOR",
                "PROJECT ESCALATION CONTACTS",
                "ASSUMPTIONS",
                "DEPENDENCIES"
            ]

            if any(k in upper_text for k in segregation_keywords):
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

    sow_type_options = [
        "L1 Support Bot POC SOW",
        "Ready Search POC Scope of Work Document",
        "AI based Image Enhancement POC SOW",
        "Beauty Advisor POC SOW",
        "AI based Image Inspection POC SOW",
        "Gen AI for SOP POC SOW",
        "Project Scope Document",
        "Gen AI Speech To Speech",
        "PoC Scope Document"
    ]
    selected_sow_name = st.selectbox("1.1 Scope of Work Type", sow_type_options)

    # Sidebar architecture preview

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

customer_logo = st.file_uploader(
    "Upload Customer Logo (Optional)",
    type=["png", "jpg", "jpeg"]
)

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
            6 RESOURCES & COST ESTIMATES

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
    
    st.write("")
    
    if st.button("💾 Prepare Microsoft Word Document"):
        branding_info = {
        "sow_name": selected_sow_name,
        "customer_logo_bytes": customer_logo.getvalue() if customer_logo else None,
        "doc_date_str": doc_date.strftime("%d %B %Y")
    }

        
        docx_data = create_docx_logic(st.session_state.generated_sow, branding_info, selected_sow_name)
        
        st.download_button(
            label="📥 Download Now (.docx)", 
            data=docx_data, 
            file_name=f"SOW_{selected_sow_name.replace(' ', '_')}.docx", 
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            use_container_width=True
        )
