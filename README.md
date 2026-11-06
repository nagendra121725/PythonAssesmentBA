# Python Assessment Portal

Flask + SQLite assessment portal for 40 randomized MCQs and 10 beginner Python coding tasks (50 marks total).

## Features
- 40 MCQs selected randomly from a 50-question bank (1 mark each).
- 10 beginner coding questions (1 mark each), automatically checked against predefined input/output test cases.
- 60-minute assessment, one submitted attempt per roll number.
- Immediate student result; faculty dashboard with MCQ, coding and total marks, submitted code, and CSV export.
- SQLite database; configure a Render persistent disk for durable results.

## Local run
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. Set `SECRET_KEY`, `ADMIN_PASSWORD`, and `DATABASE_PATH` before deployment.

## Render
Build command: `pip install -r requirements.txt`
Start command: `gunicorn app:app`
Environment variables:
- `SECRET_KEY`: unique random secret
- `ADMIN_PASSWORD`: strong faculty password
- `DATABASE_PATH`: `/var/data/assessment.db`

Attach a persistent disk mounted at `/var/data`.

## Important code-execution note
The beginner code evaluator uses AST allowlisting, a short subprocess timeout, restricted built-ins and no imports/attribute access except selected string methods. This reduces risk but is not a hardened multi-tenant sandbox. For high-stakes or public untrusted code execution, integrate a dedicated sandbox service (e.g. Judge0) or run isolated containers with strict CPU, memory, filesystem and network controls.
