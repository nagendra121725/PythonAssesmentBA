import os, json, csv, io, random, secrets, sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
DATABASE = os.environ.get("DATABASE_PATH", "assessment.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
TEST_MINUTES = 30
QUESTIONS_PER_TEST = 25

# Each question has four choices and one correct option index (0-based).
QUESTIONS = [
("Which function displays output in Python?", ["input()", "print()", "display()", "write()"], 1, "Python fundamentals"),
("Which function accepts keyboard input?", ["scan()", "read()", "input()", "get()"], 2, "Python fundamentals"),
("Which symbol starts a single-line comment?", ["//", "<!--", "#", "**"], 2, "Python fundamentals"),
("Which keyword defines a function?", ["function", "fun", "def", "define"], 2, "Python fundamentals"),
("Which is a valid Python variable name?", ["2value", "student-name", "student_name", "class"], 2, "Python fundamentals"),
("What is the usual extension of a Python source file?", [".pt", ".py", ".pyt", ".python"], 1, "Python fundamentals"),
("Which statement about Python indentation is correct?", ["It is optional everywhere", "It defines code blocks", "It is only for comments", "It replaces variable names"], 1, "Python fundamentals"),
("Python is generally described as a ______ language.", ["high-level", "machine-only", "assembly-only", "markup"], 0, "Python fundamentals"),
("Which built-in function reports an object's type?", ["typeof()", "type()", "datatype()", "kind()"], 1, "Python fundamentals"),
("Which keyword is used to import a module?", ["include", "using", "import", "require"], 2, "Python fundamentals"),
("What is the data type of 3.14?", ["int", "str", "float", "bool"], 2, "Data types and operators"),
("Which data type represents True or False?", ["int", "bool", "str", "float"], 1, "Data types and operators"),
("What is the result of 10 // 3?", ["3.33", "1", "3", "0"], 2, "Data types and operators"),
("Which operator calculates a remainder?", ["/", "//", "%", "**"], 2, "Data types and operators"),
("Which operator performs exponentiation?", ["^", "**", "//", "%%"], 1, "Data types and operators"),
("What is the result of 5 == 5?", ["5", "False", "True", "None"], 2, "Data types and operators"),
("Which keyword is the logical AND operator?", ["&&", "AND", "and", "&and"], 2, "Data types and operators"),
("What does bool(0) return?", ["True", "False", "0", "None"], 1, "Data types and operators"),
("Which converts the string '25' to an integer?", ["str()", "float()", "int()", "chr()"], 2, "Data types and operators"),
("What is the result of 2 + 3 * 4?", ["20", "14", "24", "11"], 1, "Data types and operators"),
("Which statement is used for conditional decision-making?", ["if", "repeat", "switch", "select"], 0, "Conditions and loops"),
("Which keyword checks another condition after an if?", ["otherwise", "elif", "then", "case"], 1, "Conditions and loops"),
("Which loop is commonly used to iterate over a sequence?", ["for", "repeat-until", "do-while", "switch"], 0, "Conditions and loops"),
("Which loop repeats while its condition is true?", ["if", "for-ever", "while", "switch"], 2, "Conditions and loops"),
("What values are produced by list(range(5))?", ["[1,2,3,4,5]", "[0,1,2,3,4]", "[0,1,2,3,4,5]", "[5]"], 1, "Conditions and loops"),
("Which keyword immediately exits a loop?", ["stop", "exit", "break", "terminate"], 2, "Conditions and loops"),
("Which keyword skips to the next loop iteration?", ["pass", "continue", "break", "skip"], 1, "Conditions and loops"),
("What does pass do?", ["Stops the program", "Does nothing; acts as a placeholder", "Restarts a loop", "Returns a value"], 1, "Conditions and loops"),
("How many times does for i in range(3) execute?", ["2", "3", "4", "Infinitely"], 1, "Conditions and loops"),
("What is the result of list(range(2, 8, 2))?", ["[2,4,6]", "[2,4,6,8]", "[1,3,5,7]", "[2,3,4,5,6,7]"], 0, "Conditions and loops"),
("Which collection is ordered and mutable?", ["tuple", "list", "set", "frozenset"], 1, "Data structures"),
("Which brackets create a list?", ["()", "{}", "[]", "<>"], 2, "Data structures"),
("Which collection is ordered and immutable?", ["list", "set", "tuple", "dictionary"], 2, "Data structures"),
("Which collection stores unique elements?", ["list", "tuple", "set", "string"], 2, "Data structures"),
("Which structure stores key-value pairs?", ["list", "dictionary", "tuple", "set"], 1, "Data structures"),
("Which list method adds an item to the end?", ["add()", "insert_end()", "append()", "push()"], 2, "Data structures"),
("What is the first index of a Python sequence?", ["1", "-1", "0", "2"], 2, "Strings and collections"),
("Which operator concatenates strings?", ["*", "+", "&", "%"], 1, "Strings and collections"),
("Which string method converts text to lowercase?", ["lower()", "lowercase()", "small()", "to_lower()"], 0, "Strings and collections"),
("What does len([2, 4, 6, 8]) return?", ["3", "4", "6", "8"], 1, "Strings and collections"),
("Which slice returns the first three characters of s?", ["s[1:3]", "s[:3]", "s[3:]", "s[-3:]"], 1, "Strings and collections"),
("Which keyword returns a value from a function?", ["print", "break", "return", "yieldback"], 2, "Functions and OOP"),
("A lambda expression creates what?", ["an anonymous function", "a loop", "a class", "a module"], 0, "Functions and OOP"),
("Which method commonly initializes a new class instance?", ["__start__()", "__init__()", "__create__()", "__main__()"], 1, "Functions and OOP"),
("Which OOP concept lets a class derive features from another class?", ["encapsulation", "polymorphism", "inheritance", "iteration"], 2, "Functions and OOP"),
("Which structure handles exceptions?", ["try-except", "if-else", "for-while", "def-return"], 0, "Functions and OOP"),
("Which block runs whether an exception occurs or not?", ["except", "finally", "raise", "assert"], 1, "Functions and OOP"),
("What does a function without an explicit return statement return?", ["0", "False", "None", "An empty string"], 2, "Functions and OOP"),
("Which file mode opens a file for appending?", ["r", "w", "a", "x"], 2, "Files and exceptions"),
("Which statement is recommended for automatically closing a file?", ["with", "closefile", "tryopen", "finish"], 0, "Files and exceptions"),
("Which exception is raised by 10 / 0?", ["ValueError", "TypeError", "ZeroDivisionError", "IndexError"], 2, "Files and exceptions"),
]

def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            email TEXT,
            question_ids TEXT NOT NULL,
            started_at TEXT NOT NULL,
            deadline TEXT NOT NULL,
            submitted_at TEXT,
            answers TEXT,
            score INTEGER,
            total INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'in_progress'
        )""")

def parse_dt(value):
    return datetime.fromisoformat(value)

@app.route("/")
def home():
    return render_template("home.html", total_questions=len(QUESTIONS), per_test=QUESTIONS_PER_TEST, minutes=TEST_MINUTES)

@app.route("/start", methods=["POST"])
def start():
    name = request.form.get("student_name", "").strip()
    roll = request.form.get("roll_number", "").strip()
    email = request.form.get("email", "").strip()
    if not name or not roll:
        flash("Please enter your name and roll number.")
        return redirect(url_for("home"))
    conn = db()
    existing = conn.execute("SELECT id FROM attempts WHERE roll_number=? AND status='submitted'", (roll,)).fetchone()
    if existing:
        conn.close()
        flash("A submitted attempt already exists for this roll number. Please contact your faculty if you need a retake.")
        return redirect(url_for("home"))
    ids = random.sample(range(len(QUESTIONS)), QUESTIONS_PER_TEST)
    random.shuffle(ids)
    started = datetime.now(timezone.utc)
    deadline = started + timedelta(minutes=TEST_MINUTES)
    token = secrets.token_urlsafe(24)
    conn.execute("""INSERT INTO attempts(token, student_name, roll_number, email, question_ids, started_at, deadline, total)
                    VALUES(?,?,?,?,?,?,?,?)""",
                 (token, name, roll, email, json.dumps(ids), started.isoformat(), deadline.isoformat(), QUESTIONS_PER_TEST))
    conn.commit()
    conn.close()
    session["attempt_token"] = token
    return redirect(url_for("test"))

@app.route("/test", methods=["GET", "POST"])
def test():
    token = session.get("attempt_token")
    if not token:
        return redirect(url_for("home"))
    conn = db()
    attempt = conn.execute("SELECT * FROM attempts WHERE token=?", (token,)).fetchone()
    if not attempt:
        conn.close()
        return redirect(url_for("home"))
    if attempt["status"] == "submitted":
        conn.close()
        return redirect(url_for("result", token=token))
    deadline = parse_dt(attempt["deadline"])
    remaining = max(0, int((deadline - datetime.now(timezone.utc)).total_seconds()))
    ids = json.loads(attempt["question_ids"])
    if request.method == "POST":
        raw_answers = request.form.to_dict()
        answers = {}
        score = 0
        for pos, qid in enumerate(ids):
            value = raw_answers.get(f"q{pos}")
            if value is not None and value.isdigit():
                selected = int(value)
                if 0 <= selected < 4:
                    answers[str(qid)] = selected
                    if selected == QUESTIONS[qid][2]:
                        score += 1
        if datetime.now(timezone.utc) > deadline:
            # The same submitted answers are graded; late submission is marked as time-expired.
            pass
        conn.execute("""UPDATE attempts SET submitted_at=?, answers=?, score=?, status='submitted' WHERE token=?""",
                     (datetime.now(timezone.utc).isoformat(), json.dumps(answers), score, token))
        conn.commit()
        conn.close()
        return redirect(url_for("result", token=token))
    conn.close()
    quiz = []
    for pos, qid in enumerate(ids):
        q, options, correct, topic = QUESTIONS[qid]
        # Stable per-attempt option shuffle stored in session for consistent refresh/navigation.
        shuffle_key = f"opts_{token}_{qid}"
        if shuffle_key not in session:
            order = list(range(4))
            random.shuffle(order)
            session[shuffle_key] = order
        order = session[shuffle_key]
        quiz.append({"pos": pos, "text": q, "options": [options[i] for i in order], "original_indices": order})
    return render_template("test.html", quiz=quiz, remaining=remaining, student=attempt["student_name"])

@app.route("/result/<token>")
def result(token):
    conn = db()
    attempt = conn.execute("SELECT * FROM attempts WHERE token=?", (token,)).fetchone()
    conn.close()
    if not attempt:
        abort(404)
    ids = json.loads(attempt["question_ids"])
    answers = json.loads(attempt["answers"] or "{}")
    details = []
    score = 0
    for pos, qid in enumerate(ids):
        question, options, correct, topic = QUESTIONS[qid]
        selected = answers.get(str(qid))
        if selected == correct:
            score += 1
        details.append({"number": pos + 1, "question": question, "selected": options[selected] if selected is not None else "Not answered",
                        "correct": options[correct], "is_correct": selected == correct, "topic": topic})
    return render_template("result.html", attempt=attempt, details=details, score=score, total=len(ids))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")
        if secrets.compare_digest(password, ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("dashboard"))
        flash("Incorrect admin password.")
    return render_template("admin_login.html")

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/admin/dashboard")
@admin_required
def dashboard():
    conn = db()
    rows = conn.execute("SELECT * FROM attempts ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("dashboard.html", rows=rows)

@app.route("/admin/export")
@admin_required
def export():
    conn = db()
    rows = conn.execute("SELECT student_name, roll_number, email, score, total, status, started_at, submitted_at FROM attempts ORDER BY id DESC").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student Name", "Roll Number", "Email", "Score", "Total", "Status", "Started At (UTC)", "Submitted At (UTC)"])
    for row in rows:
        writer.writerow(list(row))
    mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="python_assessment_results.csv")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin"))

@app.route("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
