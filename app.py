import streamlit as st
from datetime import date
import io
import re
import json
import requests
import time
from urllib.parse import quote

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

# --- ARCHITECTURE PATTERN MAPPING ---
PATTERN_MAPPING = {
    "Multi Agent Store Advisor": "AGENTIC_RAG",
    "Intelligent Search": "RAG_TEXT",
    "Recommendation": "RECOMMENDER",
    "AI Agents Demand Forecasting": "RECOMMENDER",
    "Banner Audit using LLM": "VISION_LLM",
    "Image Enhancement": "VISION_LLM",
    "Virtual Try-On": "VISION_LLM",
    "Agentic AI L1 Support": "AGENTIC_RAG",
    "Product Listing Standardization": "CONTENT_GEN",
    "AI Agents Based Pricing Module": "RECOMMENDER",
    "Cost, Margin Visibility & Insights using LLM": "RAG_TEXT",
    "AI Trend Simulator": "RECOMMENDER",
    "Virtual Data Analyst (Text to SQL)": "TEXT_TO_SQL",
    "Multilingual Call Analysis": "VOICE_AI",
    "Customer Review Analysis": "RAG_TEXT",
    "Sales Co-Pilot": "AGENTIC_RAG",
    "Research Co-Pilot": "AGENTIC_RAG",
    "Product Copy Generator": "CONTENT_GEN",
    "Multi-agent e-KYC & Onboarding": "AGENTIC_RAG",
    "Document / Report Audit": "RAG_TEXT",
    "RBI Circular Scraping & Insights Bot": "RAG_TEXT",
    "Visual Inspection": "VISION_LLM",
    "AIoT based CCTV Surveillance": "IOT_STREAM",
    "Multilingual Voice Bot": "VOICE_AI",
    "SOP Creation": "AGENTIC_RAG"
}

# --- API HELPER WITH EXPONENTIAL BACKOFF ---
def make_api_call(url, payload):
    """
    Handles API calls with exponential backoff to manage 429 Rate Limit errors.
    Retries up to 5 times with delays of 1s, 2s, 4s, 8s, 16s.
    """
    retries = 5
    for i in range(retries):
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                if i < retries - 1:
                    time.sleep(2**i)
                    continue
                else:
                    st.error("API Error: Quota exceeded. Please wait a moment and try again.")
                    return response
            else:
                return response
        except Exception as e:
            if i < retries - 1:
                time.sleep(2**i)
                continue
            else:
                raise e
    return None

# --- ENHANCED DIAGRAM GENERATOR (Subgraphs & Flow Mapping) ---
def generate_architecture_dot(arch_json):
    """
    Creates a professional layered DOT string matching the reference images.
    """
    ui = arch_json.get('ui', {})
    orch = arch_json.get('orchestration', {})
    llm_info = arch_json.get('llm', {})
    
    dot = [
        'digraph G {',
        '  rankdir=LR; compound=true; newrank=true;',
        '  nodesep=0.5; ranksep=1.0;',
        '  node [shape=rect, style="rounded,filled", fontname="Arial Bold", fontsize=10, margin="0.2,0.1"];',
        '  edge [fontname="Arial", fontsize=9, color="#64748b", fontcolor="#334155"];',
        '',
        '  # Layer 1: Customer / Frontend',
        '  subgraph cluster_0 {',
        '    label="Customer Environment"; style="dashed,rounded"; color="#cbd5e1"; fontname="Arial Bold"; fontsize=11;',
        f'    UI [label="User Interface\\n({ui.get("type", "Web App")})", fillcolor="#3b82f6", fontcolor=white];',
        '  }',
        '',
        '  # Layer 2: Core Orchestration',
        '  subgraph cluster_1 {',
        '    label="AWS Cloud (VPC)"; style="rounded"; bgcolor="#f8fafc"; color="#94a3b8"; fontname="Arial Bold"; fontsize=11;',
        f'    ORCH [label="Orchestrator\\n({orch.get("service", "AWS Lambda")})", fillcolor="#10b981", fontcolor=white];',
        '    ',
        '    if_framework [style=invis, shape=point, width=0];'
    ]

    if arch_json.get('agent_framework'):
        fw = ", ".join(arch_json.get('agent_framework', []))
        dot.append(f'    FRAMEWORK [label="Agent Framework\\n({fw})", fillcolor="#8b5cf6", fontcolor=white];')
        dot.append('    ORCH -> FRAMEWORK [label="1. Orchestrate"];')
        core_node = "FRAMEWORK"
    else:
        core_node = "ORCH"

    dot.append('  }')
    dot.append('')
    
    # Layer 3: GenAI Services
    dot.append('  subgraph cluster_2 {')
    dot.append('    label="GenAI & Data Services"; style="rounded"; color="#94a3b8"; fontname="Arial Bold"; fontsize=11;')
    dot.append(f'    LLM [label="Model Provider\\n{llm_info.get("provider", "Amazon Bedrock")}\\n({llm_info.get("model_family", "Mistral")})", fillcolor="#f59e0b", fontcolor=white];')
    
    if arch_json.get('vector_store'):
        dot.append(f'    VS [label="Vector Store\\n({arch_json.get("vector_store")})", fillcolor="#64748b", fontcolor=white];')
        dot.append(f'    EMB [label="Embedding Model\\n({arch_json.get("embeddings", {}).get("provider", "Titan")})", fillcolor="#64748b", fontcolor=white];')
    
    if arch_json.get('databases'):
        db_name = arch_json.get('databases')[0]
        dot.append(f'    DB [label="Database\\n({db_name})", fillcolor="#64748b", fontcolor=white];')
    
    dot.append('  }')

    # Final Wiring with numbered flow
    dot.append('')
    dot.append('  UI -> ORCH [label="1. Request"];')
    
    if arch_json.get('vector_store'):
        dot.append('  ORCH -> EMB [label="2. Vectorize"];')
        dot.append('  EMB -> VS [label="3. Search"];')
        dot.append('  VS -> ORCH [label="4. Context"];')
        dot.append(f'  {core_node} -> LLM [label="5. Inference"];')
        dot.append('  LLM -> UI [label="6. Response", constraint=false];')
    else:
        dot.append(f'  {core_node} -> LLM [label="2. Inference"];')
        dot.append('  LLM -> UI [label="3. Response", constraint=false];')

    if arch_json.get('databases'):
        dot.append('  ORCH -> DB [label="Metadata"];')

    dot.append('}')
    return "\n".join(dot)

# --- CACHED UTILITIES ---
def create_docx_logic(text_content, branding_info, diagram_image=None):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    
    # Cover Page
    if branding_info.get('aws_pn_logo_bytes'):
        p_top = doc.add_paragraph()
        try:
            p_top.add_run().add_picture(io.BytesIO(branding_info['aws_pn_logo_bytes']), width=Inches(1.0))
        except:
            p_top.add_run("aws partner network").bold = True

    doc.add_paragraph("\n" * 3)
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run(branding_info['solution_name'])
    run.font.size, run.font.bold = Pt(26), True
    
    doc.add_paragraph("\n" * 4)
    logo_table = doc.add_table(rows=1, cols=3)
    def insert_logo(cell, data, width, text):
        if data:
            try: cell.paragraphs[0].add_run().add_picture(io.BytesIO(data), width=Inches(width))
            except: cell.paragraphs[0].add_run(text).bold = True
        else: cell.paragraphs[0].add_run(text).bold = True

    insert_logo(logo_table.rows[0].cells[0], branding_info.get('customer_logo_bytes'), 1.4, "[Customer Logo]")
    insert_logo(logo_table.rows[0].cells[1], branding_info.get('oneture_logo_bytes'), 2.2, "ONETURE")
    insert_logo(logo_table.rows[0].cells[2], branding_info.get('aws_adv_logo_bytes'), 1.3, "AWS Advanced")

    doc.add_page_break()
    
    # Content
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    lines = text_content.split('\n')
    i = 0
    overview_started = False
    arch_section_injected = False

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue

        clean_text = re.sub(r'^#+\s*', '', re.sub(r'\*+', '', line)).strip()
        upper_text = clean_text.upper()

        # Logic to skip the placeholder text if we are about to inject the diagram
        if "[ARCHITECTURAL DIAGRAM IMAGE PLACEHOLDER]" in upper_text or "DIAGRAM ILLUSTRATES THE PROPOSED" in upper_text:
            i += 1
            continue

        if "2 PROJECT OVERVIEW" in upper_text and not overview_started:
            doc.add_page_break()
            overview_started = True
            doc.add_heading(clean_text, level=1)
        elif "4 SOLUTION ARCHITECTURE" in upper_text:
            doc.add_heading(clean_text, level=1)
            if diagram_image and not arch_section_injected:
                doc.add_paragraph("The following diagram illustrates the proposed technical architecture for this solution on AWS, designed for scalability and secure GenAI orchestration.")
                try:
                    # Center the image
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.add_run().add_picture(io.BytesIO(diagram_image), width=Inches(6.0))
                except:
                    doc.add_paragraph("[Error rendering diagram image]")
                arch_section_injected = True
        elif line.startswith('|'):
            # Simple table processor placeholder
            p = doc.add_paragraph(line)
        elif line.startswith('# '): doc.add_heading(clean_text, level=1)
        elif line.startswith('## '): doc.add_heading(clean_text, level=2)
        elif line.startswith('### '): doc.add_heading(clean_text, level=3)
        else: doc.add_paragraph(clean_text)
        i += 1
            
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- INITIALIZATION ---
if 'generated_sow' not in st.session_state:
    st.session_state.generated_sow = ""
if 'arch_dot_string' not in st.session_state:
    st.session_state.arch_dot_string = ""
if 'arch_diagram_bytes' not in st.session_state:
    st.session_state.arch_diagram_bytes = None

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
    st.session_state.arch_dot_string = ""
    st.session_state.arch_diagram_bytes = None

# --- SIDEBAR & UI ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("SOW Architect")
    st.caption("Enterprise POC/MVP Engine")
    
    with st.expander("🔑 API Key", expanded=False):
        api_key = st.text_input("Gemini API Key", type="password")
    
    st.divider()
    st.header("📋 1. Project Intake")

    solution_options = [
        "Multi Agent Store Advisor", "Intelligent Search", "Recommendation", 
        "AI Agents Demand Forecasting", "Banner Audit using LLM", "Image Enhancement", 
        "Virtual Try-On", "Agentic AI L1 Support", "Product Listing Standardization", 
        "AI Agents Based Pricing Module", "Cost, Margin Visibility & Insights using LLM", 
        "AI Trend Simulator", "Virtual Data Analyst (Text to SQL)", "Multilingual Call Analysis", 
        "Customer Review Analysis", "Sales Co-Pilot", "Research Co-Pilot", 
        "Product Copy Generator", "Multi-agent e-KYC & Onboarding", "Document / Report Audit", 
        "RBI Circular Scraping & Insights Bot", "Visual Inspection", 
        "AIoT based CCTV Surveillance", "Multilingual Voice Bot", "SOP Creation", "Other (Please specify)"
    ]
    solution_type = st.selectbox("1.1 Solution Type", solution_options)
    final_solution = st.text_input("Specify Solution Name", placeholder="Enter solution...") if solution_type == "Other (Please specify)" else solution_type

    engagement_options = ["Proof of Concept (PoC)", "Pilot", "MVP", "Production Rollout", "Assessment / Discovery", "Support"]
    engagement_type = st.selectbox("1.2 Engagement Type", engagement_options)

    industry_options = ["Retail / E-commerce", "BFSI", "Manufacturing", "Telecom", "Healthcare", "Energy / Utilities", "Logistics", "Media", "Government", "Other (specify)"]
    industry_type = st.selectbox("1.3 Industry / Domain", industry_options)
    final_industry = st.text_input("Specify Industry", placeholder="Enter industry...") if industry_type == "Other (specify)" else industry_type

    duration = st.text_input("Timeline / Duration", "4 Weeks")
    
    if st.button("🗑️ Reset All Fields", on_click=clear_sow, use_container_width=True):
        st.rerun()

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

if st.button("✨ Generate SOW Document", type="primary", use_container_width=True):
    if not api_key: st.error("Please enter Gemini API Key")
    elif not objective: st.error("Please define project objective")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        pattern = PATTERN_MAPPING.get(solution_type, "AGENTIC_RAG")
        
        with st.spinner("Generating SOW & Architecture..."):
            get_md = lambda df: df.to_markdown(index=False)
            prompt_sow = f"""
            Generate a COMPLETE formal enterprise Scope of Work (SOW) for {final_solution} in {final_industry}.
            
            MANDATORY STRUCTURE:
            1 TABLE OF CONTENTS
            2 PROJECT OVERVIEW
              2.1 OBJECTIVE
              2.2 PROJECT SPONSOR(S) / STAKEHOLDER(S)
              2.3 ASSUMPTIONS & DEPENDENCIES
              2.4 PROJECT SUCCESS CRITERIA
            3 SCOPE OF WORK – TECHNICAL PROJECT PLAN
            4 SOLUTION ARCHITECTURE
            5 RESOURCES & COST ESTIMATES

            INPUTS:
            Objective: {objective}
            Metrics: {', '.join(outcomes)}
            Stakeholder Tables:
            {get_md(st.session_state.stakeholders["Partner"])}
            {get_md(st.session_state.stakeholders["Customer"])}

            RULES: Professional tone. Plain text only. No markdown bolding marks (**).
            """
            
            res_sow = make_api_call(url, {"contents": [{"parts": [{"text": prompt_sow}]}]})
            if res_sow and res_sow.status_code == 200:
                st.session_state.generated_sow = res_sow.json()['candidates'][0]['content']['parts'][0]['text']
            
            prompt_arch = f"""
            Generate JSON for AWS Architecture: {final_solution}, Pattern: {pattern}.
            Include: ui, orchestration, llm (provider, model_family), agent_framework, vector_store, data_sources.
            """
            res_arch = make_api_call(url, {"contents": [{"parts": [{"text": prompt_arch}]}], "generationConfig": {"responseMimeType": "application/json"}})
            if res_arch and res_arch.status_code == 200:
                arch_json = json.loads(res_arch.json()['candidates'][0]['content']['parts'][0]['text'])
                dot_str = generate_architecture_dot(arch_json)
                st.session_state.arch_dot_string = dot_str
                
                try:
                    q_url = f"https://quickchart.io/graphviz?graph={quote(dot_str)}"
                    img_res = requests.get(q_url, timeout=10)
                    if img_res.status_code == 200: st.session_state.arch_diagram_bytes = img_res.content
                except: pass
                
                st.balloons()

if st.session_state.generated_sow:
    st.divider()
    st.header("3. Review & Export")
    tab_edit, tab_preview = st.tabs(["✍️ Editor", "📄 Preview"])
    with tab_edit:
        st.session_state.generated_sow = st.text_area("SOW Content", value=st.session_state.generated_sow, height=500)
    with tab_preview:
        st.markdown('<div class="sow-preview">', unsafe_allow_html=True)
        # Pre-rendering logic for Visual Preview: strip the placeholder and inject diagram
        preview_text = st.session_state.generated_sow
        
        # Regex to find where Section 4 starts
        arch_match = re.search(r'(#*\s*4\s+SOLUTION ARCHITECTURE)', preview_text, re.IGNORECASE)
        
        if arch_match and st.session_state.arch_dot_string:
            pos = arch_match.end()
            # Split the text at Section 4
            before_arch = preview_text[:pos]
            after_arch = preview_text[pos:]
            
            # Clean up placeholders in the 'after' section
            after_arch = re.sub(r'\[ARCHITECTURAL DIAGRAM.*?\]', '', after_arch, flags=re.IGNORECASE)
            
            st.markdown(before_arch)
            st.graphviz_chart(st.session_state.arch_dot_string)
            st.markdown(after_arch)
        else:
            st.markdown(preview_text)
            
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾 Download .docx", use_container_width=True):
        branding = {
            'solution_name': final_solution, 
            'aws_pn_logo_bytes': aws_pn_logo.getvalue() if aws_pn_logo else None,
            'customer_logo_bytes': customer_logo.getvalue() if customer_logo else None,
            'oneture_logo_bytes': oneture_logo.getvalue() if oneture_logo else None,
            'aws_adv_logo_bytes': aws_adv_logo.getvalue() if aws_adv_logo else None,
            'doc_date_str': doc_date.strftime("%d %B %Y")
        }
        docx_data = create_docx_logic(st.session_state.generated_sow, branding, st.session_state.arch_diagram_bytes)
        st.download_button("📥 Save Now", docx_data, file_name=f"SOW_{final_solution.replace(' ', '_')}.docx")
