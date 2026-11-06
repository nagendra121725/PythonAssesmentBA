import os, json, csv, io, random, secrets, sqlite3, ast, subprocess, sys, tempfile, textwrap
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, abort

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-before-deployment')
DATABASE = os.environ.get('DATABASE_PATH', 'assessment.db')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
TEST_MINUTES = 60
MCQ_PER_TEST = 40

# 50-question MCQ bank; 40 are selected randomly for each attempt.
QUESTIONS = [
('Which function displays output in Python?', ['input()', 'print()', 'display()', 'write()'], 1, 'Python fundamentals'),
('Which function accepts keyboard input?', ['scan()', 'read()', 'input()', 'get()'], 2, 'Python fundamentals'),
('Which symbol starts a single-line comment?', ['//', '<!--', '#', '**'], 2, 'Python fundamentals'),
('Which keyword defines a function?', ['function', 'fun', 'def', 'define'], 2, 'Python fundamentals'),
('Which is a valid Python variable name?', ['2value', 'student-name', 'student_name', 'class'], 2, 'Python fundamentals'),
('What is the usual extension of a Python source file?', ['.pt', '.py', '.pyt', '.python'], 1, 'Python fundamentals'),
('What does indentation define in Python?', ['Code blocks', 'Comments', 'Variable types', 'Modules'], 0, 'Python fundamentals'),
('Which built-in function reports an object type?', ['typeof()', 'type()', 'datatype()', 'kind()'], 1, 'Python fundamentals'),
('Which keyword imports a module?', ['include', 'using', 'import', 'require'], 2, 'Python fundamentals'),
('What is the data type of 3.14?', ['int', 'str', 'float', 'bool'], 2, 'Data types'),
('Which data type represents True or False?', ['int', 'bool', 'str', 'float'], 1, 'Data types'),
('What is the result of 10 // 3?', ['3.33', '1', '3', '0'], 2, 'Operators'),
('Which operator calculates a remainder?', ['/', '//', '%', '**'], 2, 'Operators'),
('Which operator performs exponentiation?', ['^', '**', '//', '%%'], 1, 'Operators'),
('What is the result of 5 == 5?', ['5', 'False', 'True', 'None'], 2, 'Operators'),
('Which keyword is the logical AND operator?', ['&&', 'AND', 'and', '&and'], 2, 'Operators'),
('What does bool(0) return?', ['True', 'False', '0', 'None'], 1, 'Data types'),
("Which converts the string '25' to an integer?", ['str()', 'float()', 'int()', 'chr()'], 2, 'Type conversion'),
('What is the result of 2 + 3 * 4?', ['20', '14', '24', '11'], 1, 'Operators'),
('Which statement is used for conditional decision-making?', ['if', 'repeat', 'switch', 'select'], 0, 'Control flow'),
('Which keyword checks another condition after if?', ['otherwise', 'elif', 'then', 'case'], 1, 'Control flow'),
('Which loop iterates over a sequence?', ['for', 'repeat-until', 'do-while', 'switch'], 0, 'Loops'),
('Which loop repeats while its condition is true?', ['if', 'for-ever', 'while', 'switch'], 2, 'Loops'),
('What values are produced by list(range(5))?', ['[1,2,3,4,5]', '[0,1,2,3,4]', '[0,1,2,3,4,5]', '[5]'], 1, 'Loops'),
('Which keyword immediately exits a loop?', ['stop', 'exit', 'break', 'terminate'], 2, 'Loops'),
('Which keyword skips to the next loop iteration?', ['pass', 'continue', 'break', 'skip'], 1, 'Loops'),
('What does pass do?', ['Stops program', 'Acts as a placeholder', 'Restarts loop', 'Returns a value'], 1, 'Control flow'),
('How many times does for i in range(3) execute?', ['2', '3', '4', 'Infinitely'], 1, 'Loops'),
('What is list(range(2, 8, 2))?', ['[2,4,6]', '[2,4,6,8]', '[1,3,5,7]', '[2,3,4,5,6,7]'], 0, 'Loops'),
('Which collection is ordered and mutable?', ['tuple', 'list', 'set', 'frozenset'], 1, 'Data structures'),
('Which brackets create a list?', ['()', '{}', '[]', '<>'], 2, 'Data structures'),
('Which collection is ordered and immutable?', ['list', 'set', 'tuple', 'dictionary'], 2, 'Data structures'),
('Which collection stores unique elements?', ['list', 'tuple', 'set', 'string'], 2, 'Data structures'),
('Which structure stores key-value pairs?', ['list', 'dictionary', 'tuple', 'set'], 1, 'Data structures'),
('Which list method adds an item to the end?', ['add()', 'insert_end()', 'append()', 'push()'], 2, 'Lists'),
('What is the first index of a Python sequence?', ['1', '-1', '0', '2'], 2, 'Indexing'),
('Which operator concatenates strings?', ['*', '+', '&', '%'], 1, 'Strings'),
('Which string method converts text to lowercase?', ['lower()', 'lowercase()', 'small()', 'to_lower()'], 0, 'Strings'),
('What does len([2, 4, 6, 8]) return?', ['3', '4', '6', '8'], 1, 'Lists'),
('Which slice returns the first three characters of s?', ['s[1:3]', 's[:3]', 's[3:]', 's[-3:]'], 1, 'Strings'),
('Which keyword returns a value from a function?', ['print', 'break', 'return', 'yieldback'], 2, 'Functions'),
('A lambda expression creates what?', ['Anonymous function', 'Loop', 'Class', 'Module'], 0, 'Functions'),
('Which method commonly initializes a class instance?', ['__start__()', '__init__()', '__create__()', '__main__()'], 1, 'OOP'),
('Which OOP concept lets a class derive features from another class?', ['Encapsulation', 'Polymorphism', 'Inheritance', 'Iteration'], 2, 'OOP'),
('Which structure handles exceptions?', ['try-except', 'if-else', 'for-while', 'def-return'], 0, 'Exceptions'),
('Which block runs whether an exception occurs or not?', ['except', 'finally', 'raise', 'assert'], 1, 'Exceptions'),
('What does a function without an explicit return statement return?', ['0', 'False', 'None', 'Empty string'], 2, 'Functions'),
('Which file mode opens a file for appending?', ['r', 'w', 'a', 'x'], 2, 'Files'),
('Which statement is recommended for automatically closing a file?', ['with', 'closefile', 'tryopen', 'finish'], 0, 'Files'),
('Which exception is raised by 10 / 0?', ['ValueError', 'TypeError', 'ZeroDivisionError', 'IndexError'], 2, 'Exceptions'),
]

# Ten beginner programming tasks. Each has input samples and exact expected output.
CODING = [
 {'title':'Print Hello World','prompt':'Write a program that prints exactly: Hello World','starter':'# Write your Python solution here','tests':[('', 'Hello World')]},
 {'title':'Add Two Numbers','prompt':'Read two integers from separate input lines and print their sum.','starter':'# Write your Python solution here','tests':[('4\n7\n','11'),('-3\n8\n','5')]},
 {'title':'Even or Odd','prompt':'Read one integer. Print Even if it is divisible by 2; otherwise print Odd.','starter':'# Write your Python solution here','tests':[('8\n','Even'),('5\n','Odd')]},
 {'title':'Largest of Two Numbers','prompt':'Read two integers and print the larger value. If equal, print that value.','starter':'# Write your Python solution here','tests':[('12\n9\n','12'),('3\n10\n','10')]},
 {'title':'Positive, Negative or Zero','prompt':'Read an integer and print Positive, Negative or Zero.','starter':'# Write your Python solution here','tests':[('6\n','Positive'),('-2\n','Negative'),('0\n','Zero')]},
 {'title':'Sum from 1 to N','prompt':'Read N and print the sum of all integers from 1 through N.','starter':'# Write your Python solution here','tests':[('5\n','15'),('1\n','1')]},
 {'title':'Factorial','prompt':'Read a non-negative integer N and print N factorial.','starter':'# Write your Python solution here','tests':[('5\n','120'),('0\n','1')]},
 {'title':'Reverse a String','prompt':'Read a line of text and print it in reverse order.','starter':'# Write your Python solution here','tests':[('python\n','nohtyp'),('level\n','level')]},
 {'title':'Count Vowels','prompt':'Read a line of text and print the number of English vowels (a, e, i, o, u), case-insensitive.','starter':'# Write your Python solution here','tests':[('Education\n','5'),('sky\n','0')]},
 {'title':'Largest Element in a List','prompt':'Read N on the first line, then N integers on the next line (space-separated). Print the largest integer.','starter':'# Write your Python solution here','tests':[('5\n3 9 2 7 4\n','9'),('3\n-5 -2 -8\n','-2')]},
]

ALLOWED_NODES = (ast.Module, ast.Expr, ast.Assign, ast.AugAssign, ast.Name, ast.Load, ast.Store, ast.Constant,
 ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.If, ast.For, ast.While, ast.Break, ast.Continue,
 ast.Pass, ast.Call, ast.keyword, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
 ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
 ast.In, ast.NotIn, ast.Subscript, ast.Slice, ast.List, ast.Tuple, ast.Dict, ast.Set, ast.ListComp,
 ast.comprehension, ast.IfExp, ast.FunctionDef, ast.arguments, ast.arg, ast.Return, ast.Attribute)
ALLOWED_CALLS = {'print','input','int','float','str','bool','len','range','sum','min','max','abs','round','sorted','enumerate','zip','list','tuple','set','map'}

def db():
    conn = sqlite3.connect(DATABASE); conn.row_factory = sqlite3.Row; return conn

def init_db():
    with db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS attempts (
          id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT UNIQUE NOT NULL, student_name TEXT NOT NULL,
          roll_number TEXT NOT NULL, email TEXT, question_ids TEXT NOT NULL, started_at TEXT NOT NULL,
          deadline TEXT NOT NULL, submitted_at TEXT, answers TEXT, score INTEGER, total INTEGER NOT NULL,
          status TEXT NOT NULL DEFAULT 'in_progress', coding_answers TEXT, mcq_score INTEGER, coding_score INTEGER)''')
        cols = {r['name'] for r in conn.execute('PRAGMA table_info(attempts)')}
        for name, typ in [('coding_answers','TEXT'),('mcq_score','INTEGER'),('coding_score','INTEGER')]:
            if name not in cols: conn.execute(f'ALTER TABLE attempts ADD COLUMN {name} {typ}')

def parse_dt(v): return datetime.fromisoformat(v)

def evaluate_code(source, task):
    if not source or len(source) > 5000: return 0, 'Code is empty or exceeds 5,000 characters.'
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES): return 0, f'Unsupported Python construct: {type(node).__name__}'
            if isinstance(node, ast.Name) and node.id.startswith('__'): return 0, 'Special names are not allowed.'
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in ALLOWED_CALLS: return 0, 'Only approved built-in functions may be called.'
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr not in {'lower','split'} or not (isinstance(node.func.value, ast.Name) or (isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == 'input')): return 0, 'Only approved string methods may be called.'
                else: return 0, 'Only approved built-in functions may be called.'
            if isinstance(node, ast.While): return 0, 'While loops are disabled for this beginner assessment; use for loops.'
        # Execute only validated syntax in a separate Python process with a strict timeout.
        runner = r'''import sys, json, builtins
payload=json.loads(sys.stdin.read())
src=payload['src']; data=payload['data']
safe={k:getattr(builtins,k) for k in ''' + repr(sorted(ALLOWED_CALLS)) + r'''}
safe['__builtins__']=safe
for line in data:
    it=iter(line.splitlines())
    def inp(prompt=''):
        try: return next(it)
        except StopIteration: raise EOFError('No more input')
    safe['input']=inp
    old=sys.stdout
    from io import StringIO
    out=StringIO(); sys.stdout=out
    try: exec(compile(src,'<student>','exec'), {'__builtins__':safe}, {})
    finally: sys.stdout=old
    print(json.dumps(out.getvalue().strip()))
'''
        payload={'src':source,'data':[t[0] for t in task['tests']]}
        def limits():
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
                resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
            except Exception:
                pass
        proc = subprocess.run([sys.executable, '-I', '-c', runner], input=json.dumps(payload), text=True,
                              capture_output=True, timeout=2, cwd=tempfile.gettempdir(), env={'PATH':os.environ.get('PATH','')}, preexec_fn=limits if os.name == 'posix' else None)
        if proc.returncode != 0: return 0, 'Runtime error. Check your input handling and output.'
        outputs=[json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
        passed=sum(1 for got, test in zip(outputs, task['tests']) if got.strip()==test[1].strip())
        if passed == len(task['tests']): return 1, f'Passed {passed}/{len(task["tests"])} test cases.'
        return 0, f'Passed {passed}/{len(task["tests"])} test cases.'
    except subprocess.TimeoutExpired: return 0, 'Execution timed out (2-second limit).'
    except Exception: return 0, 'Could not evaluate code. Check Python syntax and input format.'

@app.route('/')
def home(): return render_template('home.html', total_questions=50, mcq_count=40, coding_count=10, minutes=TEST_MINUTES)

@app.route('/start', methods=['POST'])
def start():
    name=request.form.get('student_name','').strip(); roll=request.form.get('roll_number','').strip(); email=request.form.get('email','').strip()
    if not name or not roll: flash('Please enter your name and roll number.'); return redirect(url_for('home'))
    conn=db(); existing=conn.execute("SELECT id FROM attempts WHERE roll_number=? AND status='submitted'",(roll,)).fetchone()
    if existing: conn.close(); flash('A submitted attempt already exists for this roll number. Contact faculty for a retake.'); return redirect(url_for('home'))
    ids=random.sample(range(len(QUESTIONS)),MCQ_PER_TEST); random.shuffle(ids)
    started=datetime.now(timezone.utc); deadline=started+timedelta(minutes=TEST_MINUTES); token=secrets.token_urlsafe(24)
    conn.execute('INSERT INTO attempts(token,student_name,roll_number,email,question_ids,started_at,deadline,total) VALUES(?,?,?,?,?,?,?,?)',
                 (token,name,roll,email,json.dumps(ids),started.isoformat(),deadline.isoformat(),50)); conn.commit(); conn.close()
    session['attempt_token']=token; return redirect(url_for('test'))

@app.route('/test', methods=['GET','POST'])
def test():
    token=session.get('attempt_token')
    if not token: return redirect(url_for('home'))
    conn=db(); attempt=conn.execute('SELECT * FROM attempts WHERE token=?',(token,)).fetchone()
    if not attempt: conn.close(); return redirect(url_for('home'))
    if attempt['status']=='submitted': conn.close(); return redirect(url_for('result',token=token))
    deadline=parse_dt(attempt['deadline']); remaining=max(0,int((deadline-datetime.now(timezone.utc)).total_seconds()))
    ids=json.loads(attempt['question_ids'])
    if request.method=='POST':
        raw=request.form.to_dict(); answers={}; mcq_score=0
        for pos,qid in enumerate(ids):
            val=raw.get(f'q{pos}')
            if val is not None and val.isdigit() and 0<=int(val)<4:
                answers[str(qid)]=int(val)
                if int(val)==QUESTIONS[qid][2]: mcq_score+=1
        coding_answers={}; coding_score=0; feedback=[]
        for i, task in enumerate(CODING):
            code=raw.get(f'code{i}','')
            mark,msg=evaluate_code(code,task); coding_score+=mark
            coding_answers[str(i)]={'code':code,'mark':mark,'feedback':msg}; feedback.append(msg)
        if datetime.now(timezone.utc)>deadline:
            # The timer submits automatically; retain received responses and flag expiry in status.
            status='submitted (time expired)'
        else: status='submitted'
        total=mcq_score+coding_score
        conn.execute('UPDATE attempts SET submitted_at=?,answers=?,coding_answers=?,mcq_score=?,coding_score=?,score=?,status=? WHERE token=?',
          (datetime.now(timezone.utc).isoformat(),json.dumps(answers),json.dumps(coding_answers),mcq_score,coding_score,total,status,token))
        conn.commit(); conn.close(); return redirect(url_for('result',token=token))
    conn.close(); quiz=[]
    for pos,qid in enumerate(ids):
        q,opts,correct,topic=QUESTIONS[qid]; order=list(range(4)); random.shuffle(order)
        quiz.append({'pos':pos,'text':q,'options':[opts[i] for i in order],'original_indices':order})
    return render_template('test.html',quiz=quiz,coding=CODING,remaining=remaining,student=attempt['student_name'])

@app.route('/result/<token>')
def result(token):
    conn=db(); attempt=conn.execute('SELECT * FROM attempts WHERE token=?',(token,)).fetchone(); conn.close()
    if not attempt: abort(404)
    ids=json.loads(attempt['question_ids']); answers=json.loads(attempt['answers'] or '{}'); coding=json.loads(attempt['coding_answers'] or '{}')
    details=[]
    for pos,qid in enumerate(ids):
        question,opts,correct,topic=QUESTIONS[qid]; selected=answers.get(str(qid))
        details.append({'number':pos+1,'question':question,'selected':opts[selected] if selected is not None else 'Not answered','correct':opts[correct],'is_correct':selected==correct,'topic':topic})
    return render_template('result.html',attempt=attempt,details=details,coding=coding,score=attempt['score'] or 0,total=50)

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method=='POST':
        if secrets.compare_digest(request.form.get('password',''),ADMIN_PASSWORD): session['admin']=True; return redirect(url_for('dashboard'))
        flash('Incorrect admin password.')
    return render_template('admin_login.html')

def admin_required(fn):
    @wraps(fn)
    def wrapper(*a,**kw):
        if not session.get('admin'): return redirect(url_for('admin'))
        return fn(*a,**kw)
    return wrapper

@app.route('/admin/dashboard')
@admin_required
def dashboard():
    conn=db(); rows=conn.execute('SELECT * FROM attempts ORDER BY id DESC').fetchall(); conn.close()
    stats={'attempts':len(rows),'submitted':sum(1 for r in rows if r['score'] is not None),'average':round(sum((r['score'] or 0) for r in rows if r['score'] is not None)/max(1,sum(1 for r in rows if r['score'] is not None)),1)}
    return render_template('dashboard.html',rows=rows,stats=stats)

@app.route('/admin/attempt/<int:attempt_id>')
@admin_required
def attempt_detail(attempt_id):
    conn=db(); r=conn.execute('SELECT * FROM attempts WHERE id=?',(attempt_id,)).fetchone(); conn.close()
    if not r: abort(404)
    coding=json.loads(r['coding_answers'] or '{}')
    return render_template('attempt_detail.html',r=r,coding=coding)

@app.route('/admin/export')
@admin_required
def export():
    conn=db(); rows=conn.execute('SELECT student_name,roll_number,email,mcq_score,coding_score,score,total,status,started_at,submitted_at FROM attempts ORDER BY id DESC').fetchall(); conn.close()
    out=io.StringIO(); w=csv.writer(out); w.writerow(['Student Name','Roll Number','Email','MCQ Marks / 40','Coding Marks / 10','Total / 50','Status','Started At UTC','Submitted At UTC'])
    for row in rows: w.writerow(list(row))
    mem=io.BytesIO(out.getvalue().encode('utf-8-sig')); mem.seek(0)
    return send_file(mem,mimetype='text/csv',as_attachment=True,download_name='python_assessment_results.csv')

@app.route('/admin/logout')
def admin_logout(): session.pop('admin',None); return redirect(url_for('admin'))
@app.route('/health')
def health(): return {'status':'ok'}
init_db()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=False)
