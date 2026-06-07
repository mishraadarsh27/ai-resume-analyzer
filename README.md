# 🚀 AI Resume Analyzer

An intelligent, AI-powered web application designed to help job seekers optimize their resumes for specific target roles. By analyzing your current resume against your dream job, it provides actionable insights, identifies missing skills, generates a learning roadmap, and prepares you with tailored interview questions.

## ✨ Features

- **Smart Analysis:** Upload your resume (PDF/DOCX) or paste the text, provide your target role, and let the AI do the rest.
- **Skill Extraction & Gap Analysis:** Identifies the skills you already have and highlights the crucial skills you are missing for your target role.
- **Personalized Roadmap:** Generates a step-by-step learning roadmap to help you bridge your skill gaps.
- **Interview Prep:** Provides role-specific interview questions based on your profile to help you ace your interviews.
- **User Authentication:** Secure login and signup system so you can save your progress.
- **History Dashboard:** Automatically saves your previous resume analyses so you can track your improvement over time.
- **Modern UI:** A sleek, responsive, and beautiful glassmorphism-inspired design.

## 🛠️ Technology Stack

- **Backend:** Python, Flask
- **Database:** TiDB (Distributed MySQL-compatible database) via SQLAlchemy
- **AI Integration:** Groq API (powered by Llama 3)
- **Frontend:** HTML5, Vanilla CSS
- **Deployment:** Pre-configured for Vercel Serverless deployment

## ⚙️ Local Setup Instructions

Follow these steps to run the application on your local machine:

### 1. Clone the repository
```bash
git clone https://github.com/mishraadarsh27/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Create a Virtual Environment
It's recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
```
Activate the virtual environment:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory (you can use `.env.example` as a template) and add the following:
```env
# Your Groq API Key for AI analysis
GROQ_API_KEY=your_groq_api_key_here

# TiDB Database Connection String (or local SQLite: sqlite:///local.db)
DATABASE_URL=your_tidb_connection_string_here

# Flask Secret Key for sessions
SECRET_KEY=supersecretkey123
```

### 5. Run the Application
You can start the server using the provided batch script:
```bash
.\run.bat
```
*(Or simply run `python app.py`)*

The application will be available at `http://localhost:5000` or `http://127.0.0.1:5000`.

## ☁️ Deployment (Vercel)

This project is fully configured for deployment on Vercel. 
1. Push your code to a GitHub repository.
2. Go to the Vercel Dashboard and import your repository.
3. Add the `GROQ_API_KEY`, `DATABASE_URL`, and `SECRET_KEY` in the Vercel Environment Variables settings.
4. Click **Deploy**. Vercel will use the `vercel.json` file to route the serverless functions automatically.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to contribute.

## 📝 License

This project is open-source and available under the MIT License.
