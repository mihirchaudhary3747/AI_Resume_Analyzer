# 🤖 AI Resume Analyzer

An intelligent resume analysis web application built with **Streamlit** and powered by **LLaMA 3.3 70B** via Groq API. Upload your resume and get instant ATS scores, skill gap analysis, career path suggestions, and personalized resume tips.

---

## ✨ Features

### 👤 User Side
- **Resume Upload** — Upload PDF resumes for instant AI analysis
- **Resume Score** — Overall quality score out of 100
- **ATS Compatibility Score** — How well your resume performs with Applicant Tracking Systems
- **Skill Analysis** — Missing skills and recommended skills for your field
- **Improvement Suggestions** — Actionable tips to improve your resume
- **Career Progression Path** — Suggested career trajectory based on your profile
- **Salary Range** — Expected salary range for your field and experience level
- **AI Tips Chatbox** — Ask any resume-related question and get instant AI advice
- **Bonus Videos** — Resume writing and interview preparation videos

### 🔐 Admin Side
- **Dashboard** — Total users, average score, top field, fresher percentage
- **User Data Table** — View all uploaded resume records
- **CSV Export** — Download all user data as CSV
- **Charts** — Doughnut charts for predicted field and experience level distribution

---

## 🛠️ Tech Stack

| Technology | Usage |
|---|---|
| Python | Core language |
| Streamlit | Web application framework |
| Groq API | AI inference (LLaMA 3.3 70B) |
| PyMuPDF (fitz) | PDF text extraction |
| SQLite | Database for storing user data |
| Plotly | Interactive charts |
| yt-dlp | YouTube video metadata |
| Pillow | Image handling |

---

## 📁 Project Structure

```
AI-Resume-Analyzer/
├── App.py                  # Main Streamlit application
├── ai_analyzer.py          # AI resume analysis logic (Groq API)
├── Courses.py              # Course and video recommendations
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── .gitignore              # Git ignore rules
├── Logo/
│   └── certificate.png     # App logo
└── Uploaded_resume/        # Uploaded PDFs (not committed)
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key at [console.groq.com](https://console.groq.com)

### 5. Create required folders
```bash
mkdir Logo
mkdir Uploaded_resume
```
Add your logo image as `Logo/certificate.png`

### 6. Run the application
```bash
streamlit run App.py
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key for LLaMA inference |

---

## 🖥️ Usage

### User Mode
1. Select **User** from the sidebar
2. Upload your resume as a **PDF**
3. Wait for AI analysis to complete
4. View your scores, skill gaps, and suggestions
5. Ask resume tips in the chatbox
6. Download your full analysis report as JSON

### Admin Mode
1. Select **Admin** from the sidebar
2. Enter credentials:
   - Username: `mihir`
   - Password: `jaat47`
3. View all user data, stats, and charts

---

## 📸 Screenshots

> Add your screenshots here after deployment

---

## 🚀 Deployment

You can deploy this app for free on **Streamlit Community Cloud**:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set your `GROQ_API_KEY` in the Secrets section
5. Click **Deploy**

---

## 📦 Requirements

```
streamlit
pandas
plotly
pymupdf
pillow
groq
python-dotenv
yt-dlp
sqlite3
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 👨‍💻 Developer

**Mihir Tomar**

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## ⭐ Support

If you found this project helpful, please give it a **star** on GitHub!
