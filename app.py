import streamlit as st
from datetime import date
import io
import re
import json
import requests
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
    "Agentic AI L1 Support": "AGENTIC_RAG",
    "Sales Co-Pilot": "AGENTIC_RAG",
    "Research Co-Pilot": "AGENTIC_RAG",
    "SOP Creation": "AGENTIC_RAG",
    "Multi Agent Store Advisor": "AGENTIC_RAG",
    "Multi-agent e-KYC & Onboarding": "AGENTIC_RAG",
    "Intelligent Search": "RAG_TEXT",
    "Document / Report Audit": "RAG_TEXT",
    "RBI Circular Scraping & Insights Bot": "RAG_TEXT",
    "Customer Review Analysis": "RAG_TEXT",
    "Cost, Margin Visibility & Insights using LLM": "RAG_TEXT",
    "Virtual Data Analyst (Text to SQL)": "TEXT_TO_SQL",
    "AI Agents Demand Forecasting": "RECOMMENDER",
    "AI Agents Based Pricing Module": "RECOMMENDER",
    "AI Trend Simulator": "RECOMMENDER",
    "Recommendation": "RECOMMENDER",
    "Product Listing Standardization": "CONTENT_GEN",
    "Product Copy Generator": "CONTENT_GEN",
    "Banner Audit using LLM": "VISION_LLM",
    "Image Enhancement": "VISION_LLM",
    "Virtual Try-On": "VISION_LLM",
    "Visual Inspection": "VISION_LLM",
    "Multilingual Call Analysis": "VOICE_AI",
    "Multilingual Voice Bot": "VOICE_AI",
    "AIoT based CCTV Surveillance": "IOT_STREAM"
}

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

    insert_logo(logo_table.rows[0].cells[0], branding_info.get('customer_logo_bytes'), 1.4, "[Customer]")
    insert_logo(logo_table.rows[0].cells[1], branding_info.get('oneture_logo_bytes'), 2.2, "ONETURE")
    insert_logo(logo_table.rows[0].cells[2], branding_info.get('aws_adv_logo_bytes'), 1.3, "AWS")

    doc.add_page_break()
    
    # Content
    lines = text_content.split('\n')
    i = 0
    overview_started = False
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue

        clean_text = re.sub(r'^#+\s*', '', re.sub(r'\*+', '', line)).strip()
        upper_text = clean_text.upper()

        if "2 PROJECT OVERVIEW" in upper_text and not overview_started:
            doc.add_page_break()
            overview_started = True
            doc.add_heading(clean_text, level=1)
        elif "4 SOLUTION ARCHITECTURE" in upper_text:
            doc.add_heading(clean_text, level=1)
            if diagram_image:
                doc.add_paragraph("The technical architecture on AWS is illustrated below:")
                doc.add_picture(io.BytesIO(diagram_image), width=Inches(6.0))
        elif line.startswith('|'):
            # Table processing logic
            pass 
        elif line.startswith('# '): doc.add_heading(clean_text, level=1)
        elif line.startswith('## '): doc.add_heading(clean_text, level=2)
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
        "AWS": pd.DataFrame([{"Name": "Anubhav Sood", "Title": "AE", "Email": "anbhsood@amazon.com"}]),
        "Escalation": pd.DataFrame([{"Name": "Omkar Dhavalikar", "Title": "Lead", "Email": "omkar.dhavalikar@oneture.com"}])
    }

# --- SIDEBAR & UI ---
with st.sidebar:
    st.title("SOW Architect")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    solution_type = st.selectbox("Solution Type", list(PATTERN_MAPPING.keys()) + ["Other"])
    final_solution = st.text_input("Solution Name", value=solution_type)
    engagement_type = st.selectbox("Engagement", ["PoC", "Pilot", "MVP", "Prod"])
    industry_type = st.selectbox("Industry", ["Retail", "BFSI", "Manufacturing", "Healthcare"])
    duration = st.text_input("Timeline", "4 Weeks")

st.title("🚀 GenAI Scope of Work Architect")

brand_col1, brand_col2 = st.columns(2)
with brand_col1:
    aws_pn_logo = st.file_uploader("AWS Partner Logo", type=['png', 'jpg'])
    customer_logo = st.file_uploader("Customer Logo", type=['png', 'jpg'])
with brand_col2:
    oneture_logo = st.file_uploader("Oneture Logo", type=['png', 'jpg'])
    aws_adv_logo = st.file_uploader("AWS Adv Logo", type=['png', 'jpg'])
    doc_date = st.date_input("Date", date.today())

objective = st.text_area("Objective", height=100)

if st.button("✨ Generate SOW Document", type="primary", use_container_width=True):
    if not api_key: st.error("Please enter API Key")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        pattern = PATTERN_MAPPING.get(solution_type, "AGENTIC_RAG")
        
        with st.spinner("Generating Architecture & SOW..."):
            # 1. SOW Text
            prompt_sow = f"Generate a full professional SOW for {final_solution}. Include Section 1 TOC, 2 Overview, 3 Technical Plan, 4 Solution Architecture, 5 Costs."
            res_sow = requests.post(url, json={"contents": [{"parts": [{"text": prompt_sow}]}]})
            if res_sow.status_code == 200:
                st.session_state.generated_sow = res_sow.json()['candidates'][0]['content']['parts'][0]['text']
            
            # 2. Architecture JSON for Diagram
            prompt_arch = f"Generate JSON for AWS Architecture: {final_solution}, Pattern: {pattern}. Include: ui, orchestration, llm, agent_framework, vector_store."
            res_arch = requests.post(url, json={"contents": [{"parts": [{"text": prompt_arch}]}], "generationConfig": {"responseMimeType": "application/json"}})
            if res_arch.status_code == 200:
                arch_json = json.loads(res_arch.json()['candidates'][0]['content']['parts'][0]['text'])
                dot_str = generate_architecture_dot(arch_json)
                st.session_state.arch_dot_string = dot_str
                
                # Render PNG via API for DOCX inclusion
                try:
                    q_url = f"https://quickchart.io/graphviz?graph={quote(dot_str)}"
                    img_res = requests.get(q_url, timeout=10)
                    if img_res.status_code == 200: st.session_state.arch_diagram_bytes = img_res.content
                except: pass

if st.session_state.generated_sow:
    tab_edit, tab_preview = st.tabs(["✍️ Editor", "📄 Preview"])
    with tab_edit:
        st.session_state.generated_sow = st.text_area("SOW Content", value=st.session_state.generated_sow, height=500)
    with tab_preview:
        st.markdown('<div class="sow-preview">', unsafe_allow_html=True)
        if st.session_state.arch_dot_string:
            st.markdown("### 4 SOLUTION ARCHITECTURE")
            st.graphviz_chart(st.session_state.arch_dot_string)
            st.divider()
        st.markdown(st.session_state.generated_sow)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💾 Download .docx"):
        branding = {'solution_name': final_solution, 'aws_pn_logo_bytes': aws_pn_logo.getvalue() if aws_pn_logo else None,
                    'customer_logo_bytes': customer_logo.getvalue() if customer_logo else None,
                    'oneture_logo_bytes': oneture_logo.getvalue() if oneture_logo else None,
                    'aws_adv_logo_bytes': aws_adv_logo.getvalue() if aws_adv_logo else None,
                    'doc_date_str': doc_date.strftime("%d %b %Y")}
        docx = create_docx_logic(st.session_state.generated_sow, branding, st.session_state.arch_diagram_bytes)
        st.download_button("📥 Save Now", docx, file_name=f"SOW_{final_solution}.docx")
