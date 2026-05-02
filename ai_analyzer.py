import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key="TYPE_YOUR_API_KEY")

def analyze_resume_ai(resume_text):
    try:
        prompt = f"""You are an expert ATS resume analyzer with 15+ years of HR experience.

Analyze the resume below and reply STRICTLY in this format (no markdown, no asterisks):

Score: <0-100>
ATS_Score: <0-100>
Field: <job role>
Level: <Fresher / Junior / Mid-Level / Senior / Expert>
Current_Skills: <comma separated>
Missing_Skills: <comma separated>
Recommended_Skills: <comma separated>

Strengths:
- <strength>
- <strength>
- <strength>

Weaknesses:
- <weakness>
- <weakness>
- <weakness>

Improvements:
- <improvement>
- <improvement>
- <improvement>
- <improvement>
- <improvement>

ATS_Tips:
- <tip>
- <tip>
- <tip>

Career_Path: <title> → <title> → <title>
Salary_Range: <INR range>

Resume:
{resume_text[:3000]}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a strict ATS resume analyzer. Always analyze the ACTUAL resume content. Give REAL scores. Be specific."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1500,
        )

        result = response.choices[0].message.content
        print("RAW:", result)
        return _parse_result(result)

    except Exception as e:
        print("❌ ERROR:", e)
        return _error_response()


def _parse_result(result):
    def extract_line(pattern, text, default="General"):
        match = re.search(pattern, text)
        return match.group(1).strip() if match else default

    def extract_list_line(pattern, text):
        match = re.search(pattern, text)
        if match:
            return [s.strip() for s in match.group(1).split(",") if s.strip()]
        return []

    def extract_bullets(section_name, text):
        pattern = rf"{section_name}:\n((?:-[^\n]+\n?)+)"
        match = re.search(pattern, text)
        if match:
            return [i.strip() for i in re.findall(r"-\s*(.+)", match.group(1)) if i.strip()]
        return []

    score     = max(0, min(100, int(extract_line(r"Score:\s*(\d+)", result, "60"))))
    ats_score = max(0, min(100, int(extract_line(r"ATS_Score:\s*(\d+)", result, "55"))))

    return {
        "score":               score,
        "ats_score":           ats_score,
        "field":               extract_line(r"Field:\s*([^\n]+)", result),
        "level":               extract_line(r"Level:\s*([^\n]+)", result, "Fresher"),
        "career_path":         extract_line(r"Career_Path:\s*([^\n]+)", result, "Not specified"),
        "salary_range":        extract_line(r"Salary_Range:\s*([^\n]+)", result, "Not specified"),
        "current_skills":      extract_list_line(r"Current_Skills:\s*([^\n]+)", result),
        "skills_missing":      extract_list_line(r"Missing_Skills:\s*([^\n]+)", result),
        "skills_recommended":  extract_list_line(r"Recommended_Skills:\s*([^\n]+)", result),
        "strengths":           extract_bullets("Strengths", result),
        "weaknesses":          extract_bullets("Weaknesses", result),
        "improvements":        extract_bullets("Improvements", result),
        "ats_tips":            extract_bullets("ATS_Tips", result),
    }


def _error_response():
    return {
        "score": 0, "ats_score": 0,
        "field": "Error", "level": "Unknown",
        "career_path": "N/A", "salary_range": "N/A",
        "current_skills": [],
        "skills_missing":     ["Analysis failed"],
        "skills_recommended": ["Please try again"],
        "strengths":    ["Could not analyze"],
        "weaknesses":   ["Could not analyze"],
        "improvements": ["Please re-upload your resume"],
        "ats_tips":     ["Try again"],
    }
