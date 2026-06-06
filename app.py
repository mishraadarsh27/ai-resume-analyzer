import os
from flask import Flask, render_template, request, redirect, session, jsonify
from db import Base, engine, SessionLocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

Base.metadata.create_all(bind=engine)

# HOME / LANDING PAGE
@app.route("/")
def home():
    return render_template("landing.html")

# ---- SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = SessionLocal()
    try:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            existing_user = db.query(models.User).filter_by(email=email).first()
            if existing_user:
                return render_template("signup.html", error="User already exists")

            user = models.User(email=email, password=password)
            db.add(user)
            db.commit()

            return redirect("/login")
        return render_template("signup.html")
    finally:
        db.close()

# LOGIN
@app.route("/login", methods=["GET", "POST"])
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

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result = None
    user_goal = None
    resume_text = None
    file = None

    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(email=session["user"]).first()

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
            
            if not result:
                if (not resume_text or resume_text.strip() == "") and not has_file:
                    result = {"error": "Please paste your resume text or upload a PDF/DOCX file."}
                elif has_file and (not resume_text or resume_text.strip() == ""):
                    result = {"error": "Uploaded file contains no readable text or failed to parse."}
                elif resume_text and user_goal:
                    try:
                        result = analyze_resume(resume_text, user_goal)
                        if result and "error" not in result:
                            # Attach target role to results
                            result["role"] = user_goal
                            
                            report = models.Reports(
                                user_id=user.id,
                                resume_text=resume_text,
                                result=json.dumps(result)
                            )
                            db.add(report)
                            db.commit()
                    except Exception as e:
                        result = {"error": f"Error analyzing resume: {str(e)}"}

            # Support AJAX Response
            is_ajax = (request.headers.get("X-Requested-With") == "XMLHttpRequest" or 
                       request.args.get("ajax") == "true")
            if is_ajax:
                return jsonify(result)

        else:
            # GET: Load last scan to make dashboard persistent
            latest_report = db.query(models.Reports).filter_by(user_id=user.id).order_by(models.Reports.id.desc()).first()
            if latest_report:
                try:
                    result = json.loads(latest_report.result)
                except Exception:
                    pass

    finally:
        db.close()

    return render_template(
        "dashboard.html", 
        result=result,
        user=session.get("user")
    )

# HISTORY
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(email=session["user"]).first()
        reports = db.query(models.Reports).filter_by(user_id=user.id).order_by(models.Reports.id.desc()).all()

        # convert JSON string > dict
        parsed_reports = []
        for r in reports:
            try:
                parsed_result = json.loads(r.result)
            except Exception:
                parsed_result = {}

            # Make sure role is set for display
            if "role" not in parsed_result:
                parsed_result["role"] = "Target Career Goal"

            parsed_reports.append({
                "id": r.id,
                "resume": r.resume_text,
                "result": parsed_result
            })

        return render_template("history.html", reports=parsed_reports)
    finally:
        db.close()

# DELETE REPORT
@app.route("/delete-report/<int:report_id>", methods=["POST"])
def delete_report(report_id):
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(email=session["user"]).first()
        report = db.query(models.Reports).filter_by(id=report_id, user_id=user.id).first()
        
        if report:
            db.delete(report)
            db.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")   


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

# Route to delete saved career report scan

# Persistent dashboard load on GET request
