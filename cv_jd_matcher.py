
import os
import json
import google.generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def extract_cv_details(model, cv_pdf_path):
    with open(cv_pdf_path, "rb") as f:
        pdf_bytes = f.read()
        print(f"Read {len(pdf_bytes)} bytes from CV PDF.")
        prompt = """
Extract candidate information from this resume PDF and output as JSON.
Use this structure:
{
    "name": "",
    "email": "",
    "phone": "",
    "summary": "",
    "skills": [],
    "education": [
        {"school": "", "degree": "", "start_year": "", "end_year": ""}
    ],
    "experience": [
        {"company": "", "position": "", "start_date": "", "end_date": "", "description": ""}
    ]
}
Rules:
- Output must be valid JSON, with no extra text before or after the JSON object.
- If a field is missing, leave it empty or null.
- For 'summary', generate a brief summary of the candidate's profile based on the CV content.
- If your output is not valid JSON, retry and fix it until it is valid JSON.
"""
    response = model.generate_content(
        [
            {"mime_type": "application/pdf", "data": pdf_bytes},
            prompt
        ],
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.0,
            "max_output_tokens": 3000,
        },
    )
    raw = response.text
    print("\nRaw output:\n", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("CV JSON parse error: Could not parse output as JSON.")
        return {}

def extract_jd_details(model, jd_pdf_path):
    with open(jd_pdf_path, "rb") as f:
        pdf_bytes = f.read()
    prompt = """
Extract the following key information from this job description PDF and output as JSON:
- required_skills: list of required skills (if not found, use empty list)
- qualifications: list of qualifications (if not found, use empty list)
- experience_needed: string describing experience needed (if not found, use empty string)
Return only this JSON structure:
{
  "required_skills": [],
  "qualifications": [],
  "experience_needed": ""
}
If a field is missing or not found, set it to null, empty list, or empty string as appropriate. Do not include extra text outside JSON.
"""
    response = model.generate_content(
        [
            {"mime_type": "application/pdf", "data": pdf_bytes},
            prompt
        ],
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.0,
            "max_output_tokens": 3000,
        },
    )
    raw = response.text
    print("\nRaw output:\n", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("JD JSON parse error: Could not parse output as JSON.")
        return {}


def main():
   
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Please set the GOOGLE_API_KEY environment variable.")
        return
    model = genai.GenerativeModel("gemini-2.5-flash")
    cv_pdf_path = input("Enter path to CV PDF: ")
    jd_pdf_path = input("Enter path to Job Description PDF: ")
    print("Extracting CV details...")
    cv_json = extract_cv_details(model, cv_pdf_path)
    print("Extracting Job Description details...")
    jd_json = extract_jd_details(model, jd_pdf_path)

    # Save extracted JSONs to files
    with open("cv.json", "w", encoding="utf-8") as f:
        json.dump(cv_json, f, indent=2, ensure_ascii=False)
    with open("job_description.json", "w", encoding="utf-8") as f:
        json.dump(jd_json, f, indent=2, ensure_ascii=False)

    print("\nCV JSON saved to cv.json")
    print(json.dumps(cv_json, indent=2))
    print("\nJob Description JSON saved to job_description.json")
    print(json.dumps(jd_json, indent=2))

    # Filter relevant fields for scoring
    cv_relevant = {k: cv_json.get(k, None) for k in ["skills", "education", "experience"]}
    jd_relevant = {k: jd_json.get(k, None) for k in ["required_skills", "qualifications", "experience_needed"]}

    # Compute the suitability score
    score_prompt = f'''
You are an expert recruiter. Your task is to evaluate how well the candidate's CV matches the requirements in the job description.
Instructions:
- Only consider the following fields for matching:
    - CV: skills, education, experience
    - Job Description: required_skills, qualifications, experience_needed
- Compare the candidate's skills, education, and experience against the job requirements and qualifications.
- Use weighted scoring: skills 70%, education 20%, experience 10%.
- Assign a suitability score from 0 to 100, where 100 means a perfect match and 0 means no match.
- Explain your reasoning briefly, focusing on the degree of match between the CV and the job description.
- Output only a valid JSON object with two keys: "score" (integer) and "reasoning" (string). Do not include any extra text.

CV:
{json.dumps(cv_relevant)}

Job Description:
{json.dumps(jd_relevant)}

Output format:
{{"score": <int>, "reasoning": "..."}}
'''
    
    score_response = model.generate_content(
        [score_prompt],
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.1,
            "max_output_tokens": 5000,
        },
    )
    print("\nRaw Score Output:\n", score_response)
    try:
        score_json = json.loads(score_response.text)
        print(f"\nSuitability Score: {score_json.get('score', 'N/A')} / 100")
        print(f"Reasoning: {score_json.get('reasoning', '')}")
    except Exception as e:
        print("Could not parse LLM score output.", e)
        try:
            print(score_response.candidates[0].content.parts[0].text)
        except Exception:
            print("No valid LLM output.")

if __name__ == "__main__":
    main()
