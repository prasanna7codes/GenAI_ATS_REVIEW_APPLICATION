from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input,pdf_cotent,prompt):
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input,pdf_content[0],prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

import streamlit as st

# Set Page Config
st.set_page_config(page_title="ATS Resume Expert", layout="wide")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.info("Use this app to analyze your resume against a job description.")

# Main Header
st.title("📄 ATS using GEMINI")

# Input Fields
st.markdown("### 📝 Job Description")
input_text = st.text_area("Paste the job description here:", key="input")

st.markdown("### 📂 Upload Your Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

# Display PDF Upload Status
if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully!")

# Buttons for User Actions
col1, col2 = st.columns(2)
with col1:
    submit1 = st.button("📊 Analyze Resume")
with col2:
    submit3 = st.button("🎯 Match Percentage")

# Input Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please provide a professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with deep expertise in data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description and calculate the percentage match. 
The response should include:
1️⃣ **Match Percentage**  
2️⃣ **Keywords Missing**  
3️⃣ **Final Thoughts**
"""

# Resume Analysis
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("📢 Resume Analysis")
        st.write(response)
    else:
        st.warning("⚠️ Please upload your resume to proceed.")

# Percentage Match
elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("🔍 Match Analysis")
        st.write(response)
    else:
        st.warning("⚠️ Please upload your resume to proceed.")




   




