from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import time 

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input,pdf_context,prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    try:

        response = model.generate_content([input,pdf_context[0],prompt ])

        return response.text
    except ResourceExhausted as e:
        st.error("API quota exceeded. PLease wait a minute and try again.")
        print("Quota exceeded erro:",e)
        return "Quota exceeded. Please try again later."
    
def input_pdf_setup(upload_file):
    if upload_file is not None:
        ## convert the pdf into img
        images = pdf2image.convert_from_bytes(upload_file.read())

        first_page = images[0]


        ## convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr,format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts =[
            {
                "mime_type": "images/jpeg",
                "data":base64.b64encode(img_byte_arr).decode() 
            }
        ]

        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
##streamlit app
st.set_page_config(page_title="Resume PRO")
st.header("ATs tracking system")
input_text = st.text_area("Job Description: ",key="input")
uploaded_file = st.file_uploader("Upload your resume(PDF)...",type=["pdf"])

## condition
if uploaded_file is not None:
    st.write("PDF Uploaded Succesfully")

user_query = st.text_input("Ask any question related to resume or job description ")

submit1 = st.button("Tell Me About the Resume")

submit2 = st.button("How Can I Improvise my skills")

submit3 = st.button("wHAT ARE THE keywords that ARE MISSING")

submit4 =st.button("Percentage match")

submit5 = st.button("ASK Query")

input_prompt1 = """
    You are an experienced Technical HR With Tech Experience in the filed of Data Science,Full stack web development,Cyber Security,Devlops,Data Anlayst, your task is to review the provided resume against the job description for these profiles.
    Please share your professional evaluation on whether the candidate's profile aligns with the role.
    Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt4 = """
    You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of Data Science,Full stack web development,Cyber Security,Devlops,Data Anlayst and deep ATS functionility,
    your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches job description.First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt1,pdf_content,input_text)
        st.subheader("The Response is ")
        st.write(response)
    else:
        st.write("PLease Upload the resume ")
elif submit4:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_prompt4,pdf_content,input_text)
        st.subheader("The Response is ")
        st.write(response)
    else:
        st.write("PLease Upload the resume ")

elif submit5:
    if uploaded_file and user_query.strip() != "":
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response("Answer this query: "+ user_query,pdf_content,input_text)
        st.subheader("Response upload the resume ")
        st.write(response)
    elif not uploaded_file:
        st.warning("Please upload the resume")
    elif user_query.strip() =="":
        st.write("PLease Enter a query. ")