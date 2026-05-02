print("🔥 NEW VERSION RUNNING")

import json
import re
import os
import sqlite3
import base64
import random
import time
import datetime

import streamlit as st
import pandas as pd
import plotly.express as px
import fitz

from PIL import Image
from dotenv import load_dotenv
from yt_dlp import YoutubeDL
from Courses import resume_videos, interview_videos
from ai_analyzer import analyze_resume_ai, client

load_dotenv()


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def clean_resume_text(text):
    text = re.sub(r'/\w+>', ' ', text)
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s\.\-\n]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_yt_video(link):
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get("title", "Unknown Video Title")
    except Exception:
        return "Video title unavailable"

def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


connection = sqlite3.connect("resume_data.db")
cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_data (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email_ID TEXT NOT NULL,
    resume_score TEXT NOT NULL,
    Timestamp TEXT NOT NULL,
    Page_no TEXT NOT NULL,
    Predicted_Field TEXT NOT NULL,
    User_level TEXT NOT NULL,
    Actual_skills TEXT NOT NULL,
    Recommended_skills TEXT NOT NULL,
    Recommended_courses TEXT NOT NULL
)
''')
connection.commit()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    insert_sql = '''
    INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    values = (name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, values)
    connection.commit()


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon='./Logo/certificate.png',
)
st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #0f172a; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label { color: white !important; }
div[data-baseweb="select"] span { color: black !important; }
ul[role="listbox"] li { color: black !important; }
</style>
""", unsafe_allow_html=True)


def run():
    img = Image.open('./Logo/certificate.png')
    st.image(img)

    st.sidebar.markdown("## 🚀 AI Resume Analyzer")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Select Mode")
    choice = st.sidebar.selectbox(
        "Choose your role",
        ["User", "Admin"],
        label_visibility="collapsed"
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info("Upload your resume and get AI-powered insights, ATS score, and skill recommendations.")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<div class='sidebar-footer'>Developed by Mihir Tomar</div>",
        unsafe_allow_html=True
    )

    # ══════════════════════════════════════
    # USER SIDE
    # ══════════════════════════════════════
    if choice == 'User':
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload your resume, and get smart recommendations</h5>''',
                    unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])

        if pdf_file is not None:
            with st.info('Uploading your Resume...'):
                time.sleep(4)

            os.makedirs('./Uploaded_resume', exist_ok=True)
            save_image_path = './Uploaded_resume/' + str(time.time()) + "_" + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            resume_text = extract_text_from_pdf(save_image_path)
            resume_text = clean_resume_text(resume_text)

            if not resume_text.strip():
                st.error("Could not extract text from resume. Please upload a valid PDF.")
                return

            st.header("🤖 AI Resume Analysis")

            with st.spinner("Analyzing resume with AI..."):
                data = analyze_resume_ai(resume_text)

            try:
                st.success("Analysis Completed Successfully ✅")
                score = min(max(int(data['score']), 0), 100)
                ats_score = min(max(int(data['ats_score']), 0), 100)
                skill_strength = max(0, 100 - len(data["skills_missing"]) * 10)
                confidence = max(0, score - len(data["skills_missing"]) * 5)

                st.markdown("""
                <style>
                .metric-card {
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 1rem;
                    text-align: center;
                    border: 1px solid #e9ecef;
                }
                .metric-num { font-size: 30px; font-weight: 600; line-height: 1; margin-bottom: 4px; }
                .metric-lbl { font-size: 11px; color: #6c757d; letter-spacing: 0.4px; }
                .pill-red {
                    display:inline-block; margin:3px; padding:4px 11px;
                    background:#FCEBEB; color:#A32D2D;
                    border:1px solid #F09595; border-radius:20px; font-size:11px; font-weight:500;
                }
                .pill-green {
                    display:inline-block; margin:3px; padding:4px 11px;
                    background:#EAF3DE; color:#3B6D11;
                    border:1px solid #97C459; border-radius:20px; font-size:11px; font-weight:500;
                }
                .sug-item {
                    padding:9px 13px; margin:5px 0;
                    background:#f8f9fa; border-radius:8px;
                    border:1px solid #e9ecef;
                    font-size:13px; color:#495057;
                }
                .career-pill {
                    display:inline-block; padding:5px 13px; margin:3px;
                    background:#EEEDFE; color:#3C3489;
                    border:1px solid #AFA9EC; border-radius:20px; font-size:12px; font-weight:500;
                }
                </style>
                """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#534AB7">{score}</div><div class="metric-lbl">Resume score</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#0F6E56">{ats_score}</div><div class="metric-lbl">ATS score</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#854F0B">{skill_strength}%</div><div class="metric-lbl">Skill strength</div></div>', unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#993C1D">{confidence}%</div><div class="metric-lbl">Confidence</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Score breakdown")
                st.progress(score);          st.caption(f"Resume score: {score} / 100")
                st.progress(ats_score);      st.caption(f"ATS score: {ats_score} / 100")
                st.progress(skill_strength); st.caption(f"Skill strength: {skill_strength}%")
                st.progress(confidence);     st.caption(f"Confidence: {confidence}%")

                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.markdown(f'<div class="metric-card"><div class="metric-lbl">Predicted field</div><br><span class="career-pill">{data["field"]}</span></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="metric-card"><div class="metric-lbl">Experience level</div><br><span class="career-pill">{data["level"]}</span></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Missing skills**")
                    pills = "".join(f'<span class="pill-red">{s}</span>' for s in data["skills_missing"])
                    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown("**Recommended skills**")
                    pills = "".join(f'<span class="pill-green">{s}</span>' for s in data["skills_recommended"])
                    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Improvement suggestions**")
                for i, tip in enumerate(data["improvements"], 1):
                    st.markdown(f'<div class="sug-item"><b>{i}.</b> {tip}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Career progression**")
                steps = data["career_path"].split("→")
                pills = " → ".join(f'<span class="career-pill">{s.strip()}</span>' for s in steps)
                st.markdown(f'<div>{pills} &nbsp;&nbsp; <span style="color:#085041;font-weight:500">&#8377; {data["salary_range"]}</span></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("⬇ Download analysis report", json.dumps(data, indent=4),
                                   "resume_analysis.json", "application/json", use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 💬 Ask AI for Resume Tips")
                user_question = st.text_input(
                    label="",
                    placeholder="Get any tips from AI regarding resumes...",
                    key="resume_tip_input"
                )
                if user_question:
                    with st.spinner("Getting tips from AI..."):
                        try:
                            tip_response = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {"role": "system", "content": "You are a professional resume coach and career advisor. Answer ONLY resume-related tips and advice. If the question is not about resumes or careers, politely say you can only help with resume tips. Keep answers concise, practical, and actionable. Use bullet points where helpful."},
                                    {"role": "user", "content": user_question}
                                ],
                                temperature=0.5,
                                max_tokens=500,
                            )
                            tip_answer = tip_response.choices[0].message.content
                            st.markdown(f"""
                            <div style="background:#f0f7ff;border:1px solid #b3d4f5;border-left:4px solid #534AB7;border-radius:10px;padding:14px 18px;margin-top:10px;font-size:13px;color:#1a1a2e;line-height:1.7;">
                            {tip_answer.replace(chr(10), '<br>')}
                            </div>
                            """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Could not get tips: {e}")

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)
                insert_data("User", "user@email.com", str(score), timestamp, "1",
                            data["field"], data["level"], str(data["current_skills"]),
                            str(data["skills_recommended"]), "AI Generated")

            except Exception as e:
                st.error(f"UI ERROR: {e}")

            st.header("**Bonus Video for Resume Writing Tips💡**")
            resume_vid = random.choice(resume_videos)
            st.subheader("✅ **" + fetch_yt_video(resume_vid) + "**")
            st.video(resume_vid)

            st.header("**Bonus Video for Interview Tips💡**")
            interview_vid = random.choice(interview_videos)
            st.subheader("✅ **" + fetch_yt_video(interview_vid) + "**")
            st.video(interview_vid)

        else:
            st.error('Upload Resume for analysis..')

    # ══════════════════════════════════════
    # ADMIN SIDE  ← now correctly at choice level
    # ══════════════════════════════════════
    else:
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            if ad_user == 'mihir' and ad_password == 'jaat47':

                st.markdown("""
                <style>
                .adm-header{display:flex;align-items:center;justify-content:space-between;padding-bottom:1rem;border-bottom:1px solid #e9ecef;margin-bottom:1.5rem}
                .adm-title{font-size:20px;font-weight:600;color:#1a1a2e}
                .adm-sub{font-size:12px;color:#6c757d;margin-top:2px}
                .adm-badge{font-size:11px;font-weight:500;padding:4px 12px;border-radius:20px;background:#EAF3DE;color:#3B6D11;border:1px solid #97C459}
                .stat-card{background:#f8f9fa;border-radius:10px;padding:1rem;text-align:center;border:1px solid #e9ecef}
                .stat-num{font-size:26px;font-weight:600;line-height:1;margin-bottom:4px}
                .stat-lbl{font-size:11px;color:#6c757d;letter-spacing:0.3px}
                </style>
                <div class="adm-header">
                    <div>
                        <div class="adm-title">Admin Dashboard</div>
                        <div class="adm-sub">Resume Analyzer &nbsp;·&nbsp; All user data</div>
                    </div>
                    <div class="adm-badge">Logged in as Mihir</div>
                </div>
                """, unsafe_allow_html=True)

                cursor.execute('SELECT * FROM user_data')
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=['ID','Name','Email','Resume Score','Timestamp',
                                                  'Total Page','Predicted Field','User Level',
                                                  'Actual Skills','Recommended Skills','Recommended Course'])

                total       = len(df)
                avg_score   = round(pd.to_numeric(df['Resume Score'], errors='coerce').mean(), 1) if total > 0 else 0
                top_field   = df['Predicted Field'].mode()[0] if total > 0 else "N/A"
                fresher_pct = round(df['User Level'].str.contains('Fresher', case=False, na=False).sum() / total * 100) if total > 0 else 0

                c1, c2, c3, c4 = st.columns(4)
                with c1: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#534AB7">{total}</div><div class="stat-lbl">Total users</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#0F6E56">{avg_score}</div><div class="stat-lbl">Avg resume score</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#854F0B;font-size:16px;padding-top:6px">{top_field}</div><div class="stat-lbl">Top field</div></div>', unsafe_allow_html=True)
                with c4: st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:#993C1D">{fresher_pct}%</div><div class="stat-lbl">Freshers</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**User data**")
                st.dataframe(df[['ID','Name','Email','Resume Score','Predicted Field','User Level','Timestamp']],
                             use_container_width=True, hide_index=True)
                st.markdown(get_table_download_link(df, 'User_Data.csv', '⬇ Download CSV report'), unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                plot_data = pd.read_sql('SELECT * FROM user_data', connection)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Predicted field distribution**")
                    field_counts = plot_data['Predicted_Field'].value_counts()
                    fig1 = px.pie(values=field_counts.values, names=field_counts.index, hole=0.5,
                                  color_discrete_sequence=['#534AB7','#1D9E75','#BA7517','#D85A30','#D4537E'])
                    fig1.update_layout(margin=dict(t=0,b=0,l=0,r=0), legend=dict(font=dict(size=11)))
                    fig1.update_traces(textinfo='percent', hovertemplate='%{label}: %{value}')
                    st.plotly_chart(fig1, use_container_width=True)

                with c2:
                    st.markdown("**User experience level**")
                    level_counts = plot_data['User_level'].value_counts()
                    fig2 = px.pie(values=level_counts.values, names=level_counts.index, hole=0.5,
                                  color_discrete_sequence=['#534AB7','#1D9E75','#BA7517','#D85A30'])
                    fig2.update_layout(margin=dict(t=0,b=0,l=0,r=0), legend=dict(font=dict(size=11)))
                    fig2.update_traces(textinfo='percent', hovertemplate='%{label}: %{value}')
                    st.plotly_chart(fig2, use_container_width=True)

            else:
                st.error("Wrong ID & Password Provided")


run()  # ← correctly OUTSIDE run(), at the bottom