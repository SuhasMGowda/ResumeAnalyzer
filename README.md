# 📄 Resume Checker Web App

A professional **Resume Analyzer** built with **Streamlit**.  
This app evaluates resumes for **ATS compliance**, **data completeness**, **language quality**, and **semantic strength** — helping you boost your chances of getting shortlisted!

---

## 🚀 Features

- Upload your **PDF** or **DOCX** resume.
- Get an **Overall Resume Score** with a clean gauge meter.
- Analyze across 4 key sections:
  - 📄 **Document Synopsis** (ATS compliance, file size, page count, word count)
  - 🗂 **Data Identification** (phone, email, LinkedIn, education, work history)
  - 📝 **Lexical Analysis** (personal pronouns, vocabulary level, numeric data)
  - 💬 **Semantic Analysis** (skills, achievements, skill efficiency)
- ✅ / ❌ status indicators with improvement suggestions.
- Section-wise scores visualized through a **bar chart**.
- Download a full **PDF Analysis Report**.
- Clean and responsive UI.

---

## 🛠 Tech Stack

- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [docx2txt](https://pypi.org/project/docx2txt/)
- [FPDF](https://pyfpdf.github.io/fpdf2/)

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/resume-checker.git
   cd resume-checker
   ```

2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**
   ```bash
   streamlit run main.py
   ```

---

## 📂 Project Structure

```
resume-checker/
├── app.py              # Main Streamlit application
├── requirements.txt    # List of dependencies
└── README.md           # Project documentation
```

---
