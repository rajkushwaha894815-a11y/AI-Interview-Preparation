import os
import random

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from utils.database import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    save_interview,
    get_user_interviews,
    get_all_users,
    get_total_users,
    get_total_interviews,
    get_user_performance
)

from utils.ai import (
    generate_question,
    evaluate_answer
)

from utils.resume_parser import (
    extract_resume_text,
    analyze_resume
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

app.secret_key = "ai-interview-preparation-secret-key"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            return """
            <h2>Please fill all fields.</h2>
            <a href="/register">Go Back</a>
            """

        existing_user = get_user_by_email(
            email
        )

        if existing_user:

            return """
            <h2>Email already registered.</h2>
            <p>Please use another email or login.</p>
            <a href="/login">Login</a>
            """

        password_hash = generate_password_hash(
            password
        )

        user = create_user(
            name,
            email,
            password_hash
        )

        if not user:

            return """
            <h2>Registration failed.</h2>
            <a href="/register">Try Again</a>
            """

        session["user_id"] = user["id"]

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = get_user_by_email(
            email
        )

        if user:

            password_correct = check_password_hash(
                user["password"],
                password
            )

            if password_correct:

                session["user_id"] = user["id"]

                return redirect(
                    url_for("dashboard")
                )

        return """
        <h2>Invalid email or password.</h2>
        <a href="/login">Try Again</a>
        """

    return render_template(
        "login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    user = get_user_by_id(
        user_id
    )

    if not user:

        session.clear()

        return redirect(
            url_for("login")
        )

    interviews = get_user_interviews(
        user_id
    )

    performance = get_user_performance(
        user_id
    )

    return render_template(
        "dashboard.html",
        user=user,
        interviews=interviews,
        performance=performance
    )


# ============================================================
# NORMAL INTERVIEW - START
# DYNAMIC FIELD + TOPIC + QUESTION COUNT
# ============================================================

@app.route(
    "/interview",
    methods=["GET", "POST"]
)
def interview():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------------
    # SHOW INTERVIEW PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "interview.html"
        )

    # --------------------------------------------------------
    # GET USER INPUT
    # --------------------------------------------------------

    interview_field = request.form.get(
        "interview_field",
        "Technical"
    ).strip()

    topic = request.form.get(
        "topic",
        ""
    ).strip()

    difficulty = request.form.get(
        "difficulty",
        "Medium"
    ).strip()

    language = request.form.get(
        "language",
        "English"
    ).strip()

    question_count_value = request.form.get(
        "question_count",
        "5"
    ).strip()

    # --------------------------------------------------------
    # VALIDATE FIELD
    # --------------------------------------------------------

    if not interview_field:

        return render_template(
            "interview.html",
            error="Please enter an interview field."
        )

    # --------------------------------------------------------
    # QUESTION COUNT
    # --------------------------------------------------------

    if question_count_value == "custom":

        custom_count = request.form.get(
            "custom_count",
            "5"
        ).strip()

        try:

            question_count = int(
                custom_count
            )

        except ValueError:

            question_count = 5

    else:

        try:

            question_count = int(
                question_count_value
            )

        except ValueError:

            question_count = 5

    # --------------------------------------------------------
    # LIMIT QUESTIONS
    # --------------------------------------------------------

    question_count = max(
        1,
        min(
            question_count,
            100
        )
    )

    # --------------------------------------------------------
    # GENERATE QUESTIONS
    # --------------------------------------------------------

    questions = []

    attempts = 0

    while (
        len(questions) < question_count
        and attempts < question_count * 5
    ):

        question = generate_question(
            interview_field,
            difficulty
        )

        if question:

            if question not in questions:

                questions.append(
                    question
                )

        attempts += 1

    # --------------------------------------------------------
    # SAFETY FALLBACK
    # --------------------------------------------------------

    while len(questions) < question_count:

        question = generate_question(
            interview_field,
            difficulty
        )

        if question:

            questions.append(
                question
            )

        else:

            questions.append(
                f"Explain an important concept "
                f"related to {interview_field}."
            )

    # --------------------------------------------------------
    # STORE SESSION
    # --------------------------------------------------------

    session["interview_questions"] = questions

    session["interview_index"] = 0

    session["interview_scores"] = []

    session["interview_evaluations"] = []

    session["interview_answers"] = []

    session["interview_type"] = interview_field

    session["interview_field"] = interview_field

    session["interview_topic"] = topic

    session["interview_difficulty"] = difficulty

    session["interview_language"] = language

    session["interview_question_count"] = question_count

    session["interview_completed"] = False

    # --------------------------------------------------------
    # START FIRST QUESTION
    # --------------------------------------------------------

    return render_template(
        "interview_question.html",

        question=questions[0],

        question_number=1,

        total_questions=len(
            questions
        ),

        interview_type=interview_field,

        interview_field=interview_field,

        topic=topic,

        difficulty=difficulty,

        language=language
    )


# ============================================================
# NORMAL INTERVIEW - SUBMIT ANSWER
# ============================================================

@app.route(
    "/submit-answer",
    methods=["POST"]
)
def submit_answer():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    questions = session.get(
        "interview_questions",
        []
    )

    current_index = session.get(
        "interview_index",
        0
    )

    scores = session.get(
        "interview_scores",
        []
    )

    evaluations = session.get(
        "interview_evaluations",
        []
    )

    answers = session.get(
        "interview_answers",
        []
    )

    interview_type = session.get(
        "interview_type",
        "Technical"
    )

    interview_field = session.get(
        "interview_field",
        interview_type
    )

    topic = session.get(
        "interview_topic",
        ""
    )

    difficulty = session.get(
        "interview_difficulty",
        "Medium"
    )

    language = session.get(
        "interview_language",
        "English"
    )

    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if not questions:

        return redirect(
            url_for("interview")
        )

    if current_index >= len(
        questions
    ):

        return redirect(
            url_for("interview_final")
        )

    # --------------------------------------------------------
    # CURRENT QUESTION
    # --------------------------------------------------------

    question = questions[
        current_index
    ]

    answer = request.form.get(
        "answer",
        ""
    ).strip()

    # --------------------------------------------------------
    # EVALUATE ANSWER
    # --------------------------------------------------------

    result = evaluate_answer(
        interview_type,
        question,
        answer
    )

    score = result[
        "score"
    ]

    evaluation = result[
        "evaluation"
    ]

    # --------------------------------------------------------
    # SAVE DATABASE RECORD
    # --------------------------------------------------------

    save_interview(
        user_id=user_id,
        interview_type=interview_type,
        difficulty=difficulty,
        question=question,
        answer=answer,
        evaluation=evaluation,
        score=score
    )

    # --------------------------------------------------------
    # SAVE SESSION DATA
    # --------------------------------------------------------

    scores.append(
        score
    )

    evaluations.append(
        evaluation
    )

    answers.append(
        answer
    )

    session["interview_scores"] = scores

    session["interview_evaluations"] = evaluations

    session["interview_answers"] = answers

    # --------------------------------------------------------
    # NEXT QUESTION
    # --------------------------------------------------------

    next_index = (
        current_index + 1
    )

    session["interview_index"] = next_index

    # --------------------------------------------------------
    # MORE QUESTIONS
    # --------------------------------------------------------

    if next_index < len(
        questions
    ):

        return render_template(
            "interview_question.html",

            question=questions[
                next_index
            ],

            question_number=next_index + 1,

            total_questions=len(
                questions
            ),

            interview_type=interview_type,

            interview_field=interview_field,

            topic=topic,

            difficulty=difficulty,

            language=language,

            previous_score=score
        )

    # --------------------------------------------------------
    # INTERVIEW COMPLETED
    # --------------------------------------------------------

    session[
        "interview_completed"
    ] = True

    return redirect(
        url_for("interview_final")
    )


# ============================================================
# NORMAL INTERVIEW - FINAL RESULT
# ============================================================

@app.route("/interview-final")
def interview_final():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    questions = session.get(
        "interview_questions",
        []
    )

    scores = session.get(
        "interview_scores",
        []
    )

    evaluations = session.get(
        "interview_evaluations",
        []
    )

    answers = session.get(
        "interview_answers",
        []
    )

    interview_type = session.get(
        "interview_type",
        "Technical"
    )

    interview_field = session.get(
        "interview_field",
        interview_type
    )

    topic = session.get(
        "interview_topic",
        ""
    )

    difficulty = session.get(
        "interview_difficulty",
        "Medium"
    )

    language = session.get(
        "interview_language",
        "English"
    )

    if not scores:

        return redirect(
            url_for("interview")
        )

    # --------------------------------------------------------
    # CALCULATE SCORE
    # --------------------------------------------------------

    total_score = sum(
        scores
    )

    total_questions = len(
        scores
    )

    average_score = round(
        total_score / total_questions,
        2
    )

    percentage = round(
        (average_score / 10) * 100,
        1
    )

    # --------------------------------------------------------
    # PERFORMANCE MESSAGE
    # --------------------------------------------------------

    if average_score >= 9:

        performance_message = (
            "Excellent performance! "
            "Your answers show strong understanding "
            "and good interview communication."
        )

    elif average_score >= 8:

        performance_message = (
            "Very good performance! "
            "You have a strong foundation. "
            "Continue practicing to improve further."
        )

    elif average_score >= 7:

        performance_message = (
            "Good performance! "
            "Your basic concepts are clear, "
            "but you can improve technical depth."
        )

    elif average_score >= 5:

        performance_message = (
            "Average performance. "
            "Focus on explaining concepts clearly "
            "and adding practical examples."
        )

    else:

        performance_message = (
            "Keep practicing. "
            "Focus on your fundamentals, "
            "answer structure, and communication."
        )

    # --------------------------------------------------------
    # STRENGTHS
    # --------------------------------------------------------

    strengths = []

    if average_score >= 7:

        strengths.append(
            "Good understanding of interview questions"
        )

    if average_score >= 8:

        strengths.append(
            "Strong technical or conceptual explanation"
        )

    if total_questions >= 5:

        strengths.append(
            "Completed a complete mock interview"
        )

    if not strengths:

        strengths.append(
            "You completed the interview and identified "
            "areas for further practice."
        )

    # --------------------------------------------------------
    # IMPROVEMENTS
    # --------------------------------------------------------

    improvements = []

    if average_score < 8:

        improvements.append(
            "Improve the depth of your answers"
        )

    if average_score < 7:

        improvements.append(
            "Strengthen your fundamental concepts"
        )

    if average_score < 6:

        improvements.append(
            "Practice answering questions in complete sentences"
        )

    improvements.append(
        "Use practical examples whenever possible"
    )

    improvements.append(
        "Keep improving communication and confidence"
    )

    # --------------------------------------------------------
    # RESULT DATA
    # --------------------------------------------------------

    results = []

    for index in range(
        total_questions
    ):

        results.append({
            "question_number": index + 1,

            "question": questions[
                index
            ],

            "answer": (
                answers[index]
                if index < len(answers)
                else ""
            ),

            "score": scores[
                index
            ],

            "evaluation": (
                evaluations[index]
                if index < len(evaluations)
                else ""
            )
        })

    return render_template(
        "interview_final.html",

        interview_type=interview_type,

        interview_field=interview_field,

        topic=topic,

        difficulty=difficulty,

        language=language,

        total_score=total_score,

        total_questions=total_questions,

        average_score=average_score,

        percentage=percentage,

        performance_message=performance_message,

        strengths=strengths,

        improvements=improvements,

        results=results
    )


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    user = get_user_by_id(
        user_id
    )

    if not user:

        session.clear()

        return redirect(
            url_for("login")
        )

    interviews = get_user_interviews(
        user_id
    )

    return render_template(
        "history.html",
        user=user,
        interviews=interviews
    )


# ============================================================
# RESUME ANALYSIS
# ============================================================

@app.route(
    "/resume",
    methods=["GET", "POST"]
)
def resume():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------------
    # SHOW PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "resume.html"
        )

    # --------------------------------------------------------
    # GET FILE
    # --------------------------------------------------------

    uploaded_file = request.files.get(
        "resume"
    )

    if not uploaded_file:

        return render_template(
            "resume.html",
            error="Please select a resume file."
        )

    filename = uploaded_file.filename

    if not filename:

        return render_template(
            "resume.html",
            error="Please select a valid resume file."
        )

    filename_lower = filename.lower()

    # --------------------------------------------------------
    # FILE TYPE CHECK
    # --------------------------------------------------------

    if not (
        filename_lower.endswith(".pdf")
        or filename_lower.endswith(".docx")
    ):

        return render_template(
            "resume.html",
            error="Only PDF and DOCX files are supported."
        )

    # --------------------------------------------------------
    # SAVE + ANALYZE
    # --------------------------------------------------------

    try:

        upload_folder = os.path.join(
            app.root_path,
            "uploads"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        safe_filename = os.path.basename(
            filename
        )

        file_path = os.path.join(
            upload_folder,
            safe_filename
        )

        uploaded_file.save(
            file_path
        )

        resume_text = extract_resume_text(
            file_path
        )

        analysis = analyze_resume(
            resume_text
        )

        session["resume_text"] = resume_text

        return render_template(
            "resume.html",
            resume_text=resume_text,
            analysis=analysis
        )

    except Exception as e:

        return render_template(
            "resume.html",
            error=str(e)
        )


# ============================================================
# CREATE RESUME QUESTIONS
# ============================================================

def create_resume_questions(
    resume_text
):

    questions = []

    resume_lower = resume_text.lower()

    # --------------------------------------------------------
    # PYTHON
    # --------------------------------------------------------

    if "python" in resume_lower:

        questions.extend([
            "You have mentioned Python in your resume. Explain how you have used Python in your projects.",
            "What Python concepts are you most comfortable with?",
            "Tell me about a Python project you have worked on."
        ])

    # --------------------------------------------------------
    # JAVA
    # --------------------------------------------------------

    if "java" in resume_lower:

        questions.extend([
            "You have mentioned Java in your resume. Explain your experience with Java.",
            "Which Java concepts have you used in your projects?",
            "How comfortable are you with Java and DSA?"
        ])

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    if "html" in resume_lower:

        questions.extend([
            "You have mentioned HTML in your resume. Explain how you have used HTML in a project.",
            "What is the difference between HTML and HTML5?"
        ])

    # --------------------------------------------------------
    # CSS
    # --------------------------------------------------------

    if "css" in resume_lower:

        questions.extend([
            "You have mentioned CSS in your resume. How did you use CSS in your project?",
            "What techniques do you use to make a website responsive?"
        ])

    # --------------------------------------------------------
    # FLASK
    # --------------------------------------------------------

    if "flask" in resume_lower:

        questions.extend([
            "You have mentioned Flask in your resume. Why did you choose Flask?",
            "Explain how Flask is used in your project."
        ])

    # --------------------------------------------------------
    # OPENCV
    # --------------------------------------------------------

    if "opencv" in resume_lower:

        questions.extend([
            "You have mentioned OpenCV in your resume. How did you use OpenCV?",
            "Explain one practical use of OpenCV in your project."
        ])

    # --------------------------------------------------------
    # C++
    # --------------------------------------------------------

    if "c++" in resume_lower:

        questions.extend([
            "You have mentioned C++ in your resume. Which C++ concepts are you comfortable with?",
            "Tell me about a project where you used C++."
        ])

    elif "c" in resume_lower:

        questions.extend([
            "You have mentioned C in your resume. Which C programming concepts are you comfortable with?",
            "Explain the importance of pointers in C."
        ])

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    if (
        "sql" in resume_lower
        or "mysql" in resume_lower
        or "postgresql" in resume_lower
        or "database" in resume_lower
    ):

        questions.extend([
            "You have mentioned database skills in your resume. Explain how you have used a database in your project.",
            "What is the difference between a primary key and a foreign key?"
        ])

    # --------------------------------------------------------
    # GIT
    # --------------------------------------------------------

    if (
        "git" in resume_lower
        or "github" in resume_lower
    ):

        questions.extend([
            "You have mentioned Git or GitHub in your resume. How do you use it in your projects?",
            "Why is version control important for software development?"
        ])

    # --------------------------------------------------------
    # AI / ML
    # --------------------------------------------------------

    if (
        "artificial intelligence" in resume_lower
        or "machine learning" in resume_lower
        or "ai" in resume_lower
    ):

        questions.extend([
            "You have mentioned AI or Machine Learning in your resume. Explain your experience with it.",
            "What problem did your AI or Machine Learning project solve?"
        ])

    # --------------------------------------------------------
    # PROJECT
    # --------------------------------------------------------

    if "project" in resume_lower:

        questions.extend([
            "Tell me about the most important project mentioned in your resume.",
            "What problem does your project solve?",
            "What challenges did you face while developing your project?",
            "What technologies did you use in your project and why?",
            "If you had more time, what improvements would you make to your project?"
        ])

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    questions.extend([
        "Tell me about yourself based on your resume.",
        "Which skill mentioned in your resume are you currently improving?",
        "What was your biggest learning from your projects?",
        "Which project are you most confident explaining in an interview?",
        "What role are you preparing for based on your technical skills?"
    ])

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    questions = list(
        dict.fromkeys(
            questions
        )
    )

    random.shuffle(
        questions
    )

    return questions[:5]


# ============================================================
# RESUME INTERVIEW - START
# ============================================================

@app.route("/resume-interview")
def resume_interview():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    resume_text = session.get(
        "resume_text"
    )

    if not resume_text:

        return redirect(
            url_for("resume")
        )

    questions = create_resume_questions(
        resume_text
    )

    # --------------------------------------------------------
    # SAFETY FALLBACK
    # --------------------------------------------------------

    if len(questions) < 5:

        questions.extend([
            "Tell me about your technical skills.",
            "Tell me about your most important project.",
            "What technical skill are you currently improving?",
            "What challenge did you face during your project?",
            "Why should we hire you?"
        ])

    questions = list(
        dict.fromkeys(
            questions
        )
    )[:5]

    # --------------------------------------------------------
    # STORE SESSION
    # --------------------------------------------------------

    session[
        "resume_interview_questions"
    ] = questions

    session[
        "resume_interview_index"
    ] = 0

    session[
        "resume_interview_scores"
    ] = []

    session[
        "resume_interview_completed"
    ] = False

    return render_template(
        "resume_interview.html",

        question=questions[0],

        question_number=1,

        total_questions=5
    )


# ============================================================
# RESUME INTERVIEW - SUBMIT
# ============================================================

@app.route(
    "/resume-submit",
    methods=["POST"]
)
def resume_submit():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    questions = session.get(
        "resume_interview_questions",
        []
    )

    current_index = session.get(
        "resume_interview_index",
        0
    )

    scores = session.get(
        "resume_interview_scores",
        []
    )

    if not questions:

        return redirect(
            url_for("resume")
        )

    if current_index >= len(
        questions
    ):

        return redirect(
            url_for("resume_final")
        )

    question = questions[
        current_index
    ]

    answer = request.form.get(
        "answer",
        ""
    ).strip()

    result = evaluate_answer(
        "Resume",
        question,
        answer
    )

    score = result[
        "score"
    ]

    evaluation = result[
        "evaluation"
    ]

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    save_interview(
        user_id=user_id,

        interview_type="Resume",

        difficulty="Resume Based",

        question=question,

        answer=answer,

        evaluation=evaluation,

        score=score
    )

    scores.append(
        score
    )

    session[
        "resume_interview_scores"
    ] = scores

    next_index = (
        current_index + 1
    )

    session[
        "resume_interview_index"
    ] = next_index

    # --------------------------------------------------------
    # NEXT QUESTION
    # --------------------------------------------------------

    if next_index < len(
        questions
    ):

        return render_template(
            "resume_interview.html",

            question=questions[
                next_index
            ],

            question_number=next_index + 1,

            total_questions=len(
                questions
            ),

            previous_score=score
        )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    session[
        "resume_interview_completed"
    ] = True

    return redirect(
        url_for("resume_final")
    )


# ============================================================
# RESUME FINAL
# ============================================================

@app.route("/resume-final")
def resume_final():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    scores = session.get(
        "resume_interview_scores",
        []
    )

    if not scores:

        return redirect(
            url_for("resume")
        )

    total_score = sum(
        scores
    )

    total_questions = len(
        scores
    )

    average_score = round(
        total_score / total_questions,
        2
    )

    # --------------------------------------------------------
    # PERFORMANCE MESSAGE
    # --------------------------------------------------------

    if average_score >= 8:

        performance_message = (
            "Excellent performance! "
            "Keep practicing to maintain your level."
        )

    elif average_score >= 6:

        performance_message = (
            "Good performance! "
            "Continue practicing to improve your interview skills."
        )

    elif average_score >= 4:

        performance_message = (
            "You are making progress. "
            "Practice your answers and technical concepts regularly."
        )

    else:

        performance_message = (
            "Keep practicing. "
            "Focus on clear explanations and stronger answers."
        )

    return render_template(
        "resume_final.html",

        scores=scores,

        total_score=total_score,

        total_questions=total_questions,

        average_score=average_score,

        performance_message=performance_message
    )


# ============================================================
# ADMIN
# ============================================================

@app.route("/admin")
def admin():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return redirect(
            url_for("login")
        )

    user = get_user_by_id(
        user_id
    )

    if not user:

        return redirect(
            url_for("login")
        )

    if not user["is_admin"]:

        return """
        <h2>Access Denied</h2>

        <p>
            You do not have permission
            to access the Admin Panel.
        </p>

        <a href="/dashboard">
            Back to Dashboard
        </a>
        """

    users = get_all_users()

    total_users = get_total_users()

    total_interviews = get_total_interviews()

    return render_template(
        "admin.html",

        users=users,

        total_users=total_users,

        total_interviews=total_interviews,

        average_score=0,

        best_score=0,

        interviews=[]
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# TEST
# ============================================================

@app.route("/test")
def test():

    return """
    <h1>
        AI Interview Preparation
    </h1>

    <p>
        Flask server is working successfully! ✅
    </p>

    <p>
        Dynamic Interview System is integrated.
    </p>

    <p>
        Resume Analysis is integrated.
    </p>

    <p>
        Resume Interview is integrated.
    </p>

    <p>
        Performance Dashboard is integrated.
    </p>

    <a href="/">
        Go to Home
    </a>
    """


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "AI INTERVIEW PREPARATION APP"
    )

    print(
        "Dynamic Interview System"
    )

    print(
        "Flask server is starting..."
    )

    print(
        "========================================"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )