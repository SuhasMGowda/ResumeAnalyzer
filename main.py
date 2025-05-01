import streamlit as st
import docx2txt
import pdfplumber
import re
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF
from keybert import KeyBERT

# --- Helper Functions ---

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_text_from_docx(file):
    return docx2txt.process(file)

def get_file_size(file):
    return len(file.read()) / 1024  # in KB

def analyze_resume(text, file_size):
    analysis = {
        "Document Synopsis": {
            "ATS Compliance": "✅" if ".pdf" in text.lower() or ".docx" in text.lower() else "❌",
            "Page Count": "✅" if text.count('\n') // 50 <= 2 else "❌",
            "File Size": "✅" if file_size < 500 else "❌",
            "Word Count": "✅" if len(text.split()) >= 250 else "❌",
        },
        "Data Identification": {
            "Phone Number": "✅" if re.search(r'\d{10}', text) else "❌",
            "E-mail Address": "✅" if re.search(r'[\w\.-]+@[\w\.-]+', text) else "❌",
            "LinkedIn URL": "✅" if "linkedin.com" in text.lower() else "❌",
            "Education": "✅" if re.search(r'(B\.?Tech|M\.?Tech|Bachelor|Master|University)', text, re.I) else "❌",
            "Work History": "✅" if re.search(r'(experience|internship|employment)', text, re.I) else "❌",
            "Skills / Achievements": "✅" if re.search(r'(skills|achievements|projects)', text, re.I) else "❌",
            "Date Formatting": "✅" if re.search(r'\b(20\d{2}|19\d{2})\b', text) else "❌",
        },
        "Lexical Analysis": {
            "Personal Pronouns": "✅" if not re.search(r'\b(I|me|my|mine)\b', text, re.I) else "❌",
            "Numericized Data": "✅" if re.search(r'\d+%', text) else "❌",
            "Vocabulary Level": "✅",  
            "Reading Level": "✅",    
            "Common Words": "✅",     
        },
        "Semantic Analysis": {
            "Measurable Achievements": "✅" if re.search(r'\d+', text) else "❌",
            "Soft Skills": "✅" if re.search(r'(teamwork|communication|leadership)', text, re.I) else "❌",
            "Hard Skills": "✅" if re.search(r'(Python|Java|SQL|Machine Learning)', text, re.I) else "❌",
            "Skill Efficiency Ratio": "✅", 
        }
    }
    return analysis

def calculate_overall_score(analysis):
    total_checks = 0
    passed_checks = 0
    for section, items in analysis.items():
        for item, result in items.items():
            total_checks += 1
            if result == "✅":
                passed_checks += 1
    return int((passed_checks / total_checks) * 100)

def section_scores(analysis):
    scores = {}
    for section, items in analysis.items():
        total = len(items)
        passed = sum(1 for v in items.values() if v == "✅")
        scores[section] = int((passed/total)*100)
    return scores

def generate_pdf_report(analysis, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Resume Analysis Report", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Overall Resume Score: {score}/100", ln=True, align="C")
    pdf.ln(10)
    for section, items in analysis.items():
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=section, ln=True)
        pdf.set_font("Arial", size=12)
        for item, result in items.items():
            mark = "Pass" if result == "✅" else "Fail"
            pdf.cell(0, 10, f"{item}: {mark}", ln=True)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin1')

def generate_smart_suggestions(text, job_desc=None):
    suggestions = []
    if job_desc:
        kw_model = KeyBERT()
        resume_kw = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)
        job_kw = kw_model.extract_keywords(job_desc, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)
        resume_kw_set = {kw for kw, _ in resume_kw}
        job_kw_set = {kw for kw, _ in job_kw}
        missing = job_kw_set - resume_kw_set
        if missing:
            suggestions.append(f"❗ Consider adding these keywords relevant to the job: {', '.join(missing)}")
    else:
        suggestions.append("✔ Add a job description to get tailored keyword suggestions.")

    return {
        "suggestions": suggestions
    }

# --- Streamlit App ---

st.set_page_config(page_title="Resume Checker", layout="wide")
st.title("📝 Professional Resume Checker with Smart Suggestions")

uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "docx"])
job_description = st.text_area("Paste the Job Description (Optional)")

if uploaded_file:
    file_size = get_file_size(uploaded_file)
    uploaded_file.seek(0)

    if uploaded_file.name.endswith('.pdf'):
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_docx(uploaded_file)

    st.subheader("📄 Uploaded Resume File")
    st.write(f"**File Name:** {uploaded_file.name}")

    analysis = analyze_resume(text, file_size)
    overall_score = calculate_overall_score(analysis)
    sec_scores = section_scores(analysis)

    st.subheader("📊 Overall Resume Score")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_score,
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "#4CAF50"},
               'steps': [{'range': [0, 50], 'color': '#ff4b4b'},
                         {'range': [50, 75], 'color': '#ffa534'},
                         {'range': [75, 100], 'color': '#4CAF50'}]}
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.subheader("📈 Section-wise Scores")
    fig_bar = go.Figure(go.Bar(
        x=list(sec_scores.values()),
        y=list(sec_scores.keys()),
        orientation='h',
        marker=dict(color='#2196f3'),
    ))
    fig_bar.update_layout(xaxis=dict(range=[0, 100]), height=300, margin=dict(l=50, r=50, t=20, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🧩 Detailed Analysis")
    for main_section, checks in analysis.items():
        st.markdown(f"### {main_section}")
        for item, result in checks.items():
            if result == "✅":
                st.success(f"✅ {item}")
            else:
                st.error(f"❌ {item}")

    st.subheader("📥 Download Resume Analysis Report")
    if st.button("Generate Report PDF"):
        pdf = generate_pdf_report(analysis, overall_score)
        st.download_button(label="Download PDF",
                           data=pdf,
                           file_name="resume_analysis_report.pdf",
                           mime='application/pdf')

    st.subheader("⚡ Areas To Improve")
    for section, checks in analysis.items():
        for item, result in checks.items():
            if result == "❌":
                st.warning(f"⚡ Improve: **{item}**")

    st.subheader("💡 Smart Suggestions")
    smart = generate_smart_suggestions(text, job_description)
    for sug in smart["suggestions"]:
        st.info(sug)
