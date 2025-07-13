from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import pdfplumber
import cohere

# Initialize Cohere API client
cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))

# ----------- Resume Text Extractor --------------
def input_pdf_setup(upload_file):
    
    if upload_file is not None:
        with pdfplumber.open(upload_file) as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text
    else:
        raise FileNotFoundError("No file uploaded")

# ----------- Cohere LLM Interaction --------------
def get_cohere_response(job_desc, resume_text, prompt):
    
    try:
        full_prompt = f"{prompt}\n\nResume:\n{resume_text}\n\nJob Description:\n{job_desc}"
        print("Prompt length:", len(full_prompt))

        response = cohere_client.generate(
            model='command-xlarge-nightly',  # Use 'command-r-plus' if available to you
            prompt=full_prompt,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.generations[0].text
    except Exception as e:
        st.error("Cohere API error occurred. Please try again later.")
        print("Cohere Error:", e)
        return "Error: Unable to process your request using Cohere API."

# ----------- Streamlit Frontend --------------
st.set_page_config(page_title="Resume PRO")
st.header("ATS Resume Evaluation System")

input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

# Define prompts
input_prompt1 = """
You are an experienced Technical HR with expertise in Data Science, Full Stack Web Development, Cyber Security, DevOps, and Data Analysis.
Your task is to review the provided resume against the job description.
Please evaluate if the candidate's profile aligns with the role and highlight strengths and weaknesses based on the job requirements.
"""

input_prompt4 = """
You are a skilled ATS (Applicant Tracking System) evaluator with deep domain knowledge in Data Science, Full Stack Web Development, Cyber Security, DevOps, and Data Analysis.
Your task is to evaluate the resume against the provided job description. 
Provide a percentage match, list missing keywords, and offer final feedback.
"""

# Buttons
submit1 = st.button("🧾 Tell Me About the Resume")
submit4 = st.button("📊 Percentage Match")

# Button logic
if submit1:
    if uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_cohere_response(input_text, pdf_content, input_prompt1)
        st.subheader("💡 Evaluation Result:")
        
        st.write(response)
    else:
        st.warning("⚠️ Please upload a resume.")

elif submit4:
    if uploaded_file:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_cohere_response(input_text, pdf_content, input_prompt4)
        st.subheader("📈 ATS Matching Result:")
        st.write(response)
    else:
        st.warning("⚠️ Please upload a resume.")
