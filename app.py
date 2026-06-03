import os
from flask import Flask,render_template,request, redirect, session
from db import Base,engine, SessionLocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

Base.metadata.create_all(bind = engine)

#HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

#----SIGNUP
@app.route("/signup", methods = ["GET", "POST"])
def signup():
    db = SessionLocal()
    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            existing_user = db.query(models.User).filter_by(email = email).first()
            if existing_user:
                return render_template("signup.html", error="User already exists")

            user = models.User(email=email, password=password)
            db.add(user)
            db.commit()

            return redirect("/login")
        return render_template("signup.html")
    finally:
        db.close()

#LOGIN
@app.route("/login", methods = ["GET","POST"])
def login():
    db = SessionLocal()
    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = db.query(models.User).filter_by(email=email, password=password).first()

            if user:
                session["user"] = user.email
                return redirect("/dashboard")
            else:
                return render_template("login.html", error="Invalid credentials")

        return render_template("login.html")
    finally:
        db.close()


#DASHBOARD
@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result = None
    user_goal = None
    resume_text = None
    file = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")
        file = request.files.get("file")

        if file and file.filename != "":
            if file.filename.lower().endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Error processing PDF: {str(e)}"}

            elif file.filename.lower().endswith(".docx"):
                try:
                    document = docx.Document(file)
                    text = ""
                    for para in document.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Error processing DOCX: {str(e)}"}
            else:
                result = {"error": "Unsupported file type. Please upload PDF or DOCX."}

        has_file = file and file.filename != ""
        
        if (not resume_text or resume_text.strip() == "") and not has_file:
            result = {"error": "Please paste your resume text or upload a PDF/DOCX file."}
        elif has_file and (not resume_text or resume_text.strip() == ""):
            result = {"error": "Uploaded file contains no readable text or failed to parse."}
        elif resume_text and user_goal:
            try:
                result = analyze_resume(resume_text, user_goal)

                db = SessionLocal()
                try:
                    user = db.query(models.User).filter_by(email=session["user"]).first()
                    
                    report = models.Reports(
                        user_id = user.id,
                        resume_text = resume_text,
                        result = json.dumps(result)
                    )
                    db.add(report)
                    db.commit()
                finally:
                    db.close()
            except Exception as e:
                result = {"error": f"Error analyzing resume: {str(e)}"}

    return render_template(
        "dashboard.html", 
        result = result,
        user = session.get("user")
    )
        
#history
@app.route("/history")
def history():
        if "user" not in session:
            return redirect("/login")
        
        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(email=session["user"]).first()

            reports = db.query(models.Reports).filter_by(user_id=user.id).all()

            # convert JSON string > dict
            parsed_reports = []
            for r in reports:
                try:
                    parsed_result = json.loads(r.result)
                except Exception:
                    parsed_result = {}

                parsed_reports.append({
                    "resume": r.resume_text,
                    "result": parsed_result
                })

            return render_template("history.html", reports=parsed_reports)
        finally:
            db.close()
#logout route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")   


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

# Route for user authentication (Login)

# Route for new user registration

# Main dashboard route handling file uploads

# Fetch and display user history

# Parse PDF files using PyPDF2

# Parse Word documents using python-docx
