import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from database import (
    add_progress,
    create_user,
    get_progress,
    get_user_by_email,
    init_db,
    verify_password,
)

from ai_service import generate_ai_response


# Load environment variables
load_dotenv()


# Create Flask application
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "edugenie-development-secret-key"
)

app.config["JSON_SORT_KEYS"] = False


# Initialize database
init_db()


# --------------------------------------------------
# LOGIN REQUIRED DECORATOR
# --------------------------------------------------

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:

            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "Login required"
                }), 401

            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# --------------------------------------------------
# REGISTER
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:

        return render_template(
            "register.html",
            error="All fields are required."
        )

    if len(password) < 6:

        return render_template(
            "register.html",
            error="Password must contain at least 6 characters."
        )

    try:

        user_id = create_user(
            name,
            email,
            password
        )

    except ValueError as error:

        return render_template(
            "register.html",
            error=str(error)
        )

    session["user_id"] = user_id
    session["user_name"] = name

    return redirect(url_for("dashboard"))


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    user = get_user_by_email(email)

    if not user or not verify_password(
        password,
        user["password_hash"]
    ):

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return redirect(url_for("dashboard"))


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    progress = get_progress(
        session["user_id"]
    )

    return render_template(
        "dashboard.html",
        user_name=session.get(
            "user_name",
            "Learner"
        ),
        progress=progress
    )


# --------------------------------------------------
# QUIZ PAGE
# --------------------------------------------------

@app.route("/quiz")
@login_required
def quiz():

    return render_template("quiz.html")


# --------------------------------------------------
# AI API
# --------------------------------------------------

@app.post("/api/ai")
@login_required
def ai_api():

    data = request.get_json(
        silent=True
    ) or {}

    prompt = (
        data.get("prompt")
        or ""
    ).strip()

    mode = (
        data.get("mode")
        or "explain"
    ).strip().lower()

    if not prompt:

        return jsonify({
            "error": "Please enter a question or topic."
        }), 400

    try:

        answer, provider = generate_ai_response(
            prompt,
            mode
        )

        return jsonify({
            "answer": answer,
            "provider": provider
        })

    except Exception as error:

        app.logger.exception(
            "AI request failed"
        )

        return jsonify({
            "error": f"AI service error: {error}"
        }), 500


# --------------------------------------------------
# SAVE PROGRESS
# --------------------------------------------------

@app.post("/api/progress")
@login_required
def progress_api():

    data = request.get_json(
        silent=True
    ) or {}

    activity = (
        data.get("activity")
        or ""
    ).strip()

    score = int(
        data.get("score", 0)
    )

    total = int(
        data.get("total", 0)
    )

    if not activity:

        return jsonify({
            "error": "Activity name is required."
        }), 400

    add_progress(
        session["user_id"],
        activity,
        score,
        total
    )

    return jsonify({
        "message": "Progress saved."
    })


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    host = os.getenv(
        "HOST",
        "127.0.0.1"
    )

    port = int(
        os.getenv(
            "PORT",
            "5000"
        )
    )

    debug = (
        os.getenv(
            "FLASK_DEBUG",
            "1"
        ) == "1"
    )

    app.run(
        host=host,
        port=port,
        debug=debug
    )