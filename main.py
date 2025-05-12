import types
import torch
torch.classes.__path__ = types.SimpleNamespace(_path=[])

import streamlit as st
import docx2txt
import pdfplumber
import re
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF
from keybert import KeyBERT

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

st.set_page_config(page_title="Cloud-ml Project", layout="wide")
st.title("📝Resume Analyzer with Smart Suggestions")

uploaded_files = st.file_uploader("Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)
job_description = st.text_area("Paste the Job Description (Optional)")

if uploaded_files:
    results = []

    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)
        file_size = get_file_size(uploaded_file)
        uploaded_file.seek(0)

        if uploaded_file.name.endswith('.pdf'):
            text = extract_text_from_pdf(uploaded_file)
        else:
            text = extract_text_from_docx(uploaded_file)

        # Basic resume detection
        if not re.search(r'(experience|education|skills|projects|resume|curriculum vitae)', text, re.I):
            st.warning(f"⚠️ The file '{uploaded_file.name}' may not be a resume. Please verify.")
            continue

        analysis = analyze_resume(text, file_size)
        score = calculate_overall_score(analysis)

        results.append({
            "file_name": uploaded_file.name,
            "text": text,
            "analysis": analysis,
            "score": score
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    best_resume = results[0]

    st.subheader("📊 Resume Score Comparison")
    st.table({res["file_name"]: res["score"] for res in results})

    st.subheader(f"🏆 Best Resume: {best_resume['file_name']} (Score: {best_resume['score']})")

    sec_scores = section_scores(best_resume['analysis'])

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
    for main_section, checks in best_resume['analysis'].items():
        st.markdown(f"### {main_section}")
        for item, result in checks.items():
            if result == "✅":
                st.success(f"✅ {item}")
            else:
                st.error(f"❌ {item}")

    st.subheader("📥 Download Resume Analysis Report")
    if st.button("Generate Report PDF"):
        pdf = generate_pdf_report(best_resume['analysis'], best_resume['score'])
        st.download_button(label="Download PDF",
                           data=pdf,
                           file_name="best_resume_analysis_report.pdf",
                           mime='application/pdf')

    st.subheader("⚡ Areas To Improve")
    for section, checks in best_resume['analysis'].items():
        for item, result in checks.items():
            if result == "❌":
                st.warning(f"⚡ Improve: **{item}**")

    st.subheader("💡 Smart Suggestions")
    smart = generate_smart_suggestions(best_resume['text'], job_description)
    for sug in smart["suggestions"]:
        st.info(sug)
