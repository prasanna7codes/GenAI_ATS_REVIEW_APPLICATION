import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = "".join(page.extract_text() or "" for page in reader.pages)  # Efficiently extract text
    return text.strip()

# ----------- Streamlit UI Setup -----------

# Sidebar for Branding & Instructions
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/8/80/Artificial_Intelligence_%26_AI_%26_Machine_Learning_-_30212411048.jpg", use_container_width=True)
st.sidebar.title("💼 Smart ATS - Resume Analyzer")
st.sidebar.write("**How it Works?**")
st.sidebar.info(
    """
    1️⃣ Paste the Job Description 📑  
    2️⃣ Upload Your Resume (PDF) 📂  
    3️⃣ Click 'Analyze' to get ATS insights ✅  
    """
)

# Main Page Header
st.markdown("<h1 style='text-align: center;'>📑 Smart ATS - Resume Analyzer</h1>", unsafe_allow_html=True)
st.write("---")

# User Inputs
jd = st.text_area("📝 Paste the Job Description Here:", height=150)
uploaded_file = st.file_uploader("📂 Upload Your Resume (PDF)", type="pdf")

# Submit Button
submit = st.button("🚀 Analyze Resume")

if submit:
    if uploaded_file is not None:
        # Extract text from uploaded PDF
        text = input_pdf_text(uploaded_file)

        # Enforced JSON format in the prompt
        formatted_prompt = f"""
        You are an ATS (Applicant Tracking System) expert evaluating resumes.  
        Analyze the resume against the job description and return only a **valid JSON response** in the following format:  

        {{
            "JD Match": "XX%",  
            "MissingKeywords": ["Keyword1", "Keyword2"],  
            "Profile Summary": "Summary here"  
        }}

        ❗ **Do NOT include explanations, greetings, or extra text—return only JSON.** ❗

        Resume: {text}  
        Job Description: {jd}  
        """

        # Get response from Gemini
        response_text = get_gemini_response(formatted_prompt)

        try:
            # Extract only JSON part from response
            start = response_text.find("{")
            end = response_text.rfind("}")

            if start != -1 and end != -1:
                clean_json = response_text[start:end+1]  # Extract JSON
                response_json = json.loads(clean_json)  # Convert to dictionary

                # Display JD Match Percentage
                st.markdown("<h2 style='text-align: center;'>📊 ATS Analysis Results</h2>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align: center; color: green;'>🎯 JD Match: {response_json['JD Match']}</h3>", unsafe_allow_html=True)

                # Display Missing Keywords
                if response_json["MissingKeywords"]:
                    st.warning(f"🚨 **Missing Keywords:** {', '.join(response_json['MissingKeywords'])}")
                else:
                    st.success("✅ No missing keywords! Your resume is well-optimized.")

                # Display Profile Summary
                st.subheader("📝 Profile Summary")
                st.write(response_json["Profile Summary"])

            else:
                st.error("❌ The AI response does not contain valid JSON. Please try again.")

        except json.JSONDecodeError:
            st.error("❌ Error processing the ATS response. Please try again.")

    else:
        st.warning("⚠️ Please upload a resume to proceed.")
