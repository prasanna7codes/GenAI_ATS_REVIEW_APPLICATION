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
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Handle None values safely
    return text.strip()

# Streamlit App UI
st.title("Smart ATS - Resume Analyzer")
st.text("Improve Your Resume for ATS Systems")

# User inputs
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Upload a PDF resume")

submit = st.button("Submit")

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
                st.subheader("📊 ATS Analysis Results")
                st.markdown(f"### 🎯 JD Match: **{response_json['JD Match']}**")

                # Display Missing Keywords
                if response_json["MissingKeywords"]:
                    st.warning("🚨 **Missing Keywords:** " + ", ".join(response_json["MissingKeywords"]))
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
