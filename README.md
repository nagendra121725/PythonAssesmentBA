# Python Programming Online Assessment Portal

A Flask + SQLite web application for a public student assessment.

## Included features
- 50-question Python MCQ bank (basic to medium)
- 25 randomly selected questions per attempt
- Randomized answer option order per student
- 30-minute countdown and automatic submission from the browser
- Server-side grading; answer key is not sent to the test page
- Immediate result and answer review
- Faculty login and results dashboard
- CSV export of student scores
- One submitted attempt per roll number

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run: `pip install -r requirements.txt`
4. Set environment variables before starting:
   - `SECRET_KEY` to a long random secret
   - `ADMIN_PASSWORD` to your own strong faculty password
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000`

## Deploy publicly on Render
1. Create a GitHub repository and upload all files in this project.
2. Create a new **Web Service** in Render and connect that repository.
3. Render detects `render.yaml`, or enter:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Add environment variables:
   - `SECRET_KEY`: a long random value
   - `ADMIN_PASSWORD`: a strong private admin password
5. Attach a persistent disk mounted at `/var/data` and set:
   - `DATABASE_PATH=/var/data/assessment.db`
6. Deploy. Render will provide a public `https://...onrender.com` URL to share with students.

## Important deployment notes
- Do not use the default admin password in a public deployment.
- SQLite data needs persistent storage. Without a persistent disk, results may be lost during redeploy/restart.
- Configure a persistent disk/volume on your hosting plan and confirm its pricing and availability.
- This starter app limits one completed attempt per roll number. It does not provide institutional single sign-on or strong anti-cheating/proctoring.
- The student timer is enforced using a server-side deadline when a submission reaches the server. A student who closes the browser without submitting may remain listed as in progress.
- The app uses UTC timestamps in the admin dashboard/export.
