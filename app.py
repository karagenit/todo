from auth import get_creds
from tasks import get_tasks, patch_task
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

creds = get_creds()
tasks = get_tasks(creds)

app = Flask(__name__)

@app.route('/')
def index():
    today = datetime.now().date()
    tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    startable_tasks = [task for task in tasks if not task.get('start_date') or datetime.strptime(task['start_date'], '%Y-%m-%d').date() <= today]
    priority_tasks = sorted(startable_tasks, key=lambda x: (-x.get('priority', 0), x.get('due_date', '9999-12-31')))
    due_tasks = sorted(tasks, key=lambda x: x.get('due_date', '9999-12-31'))

    triage_tasks = [task for task in tasks if task.get('priority', 0) == 0]
    values = [
        {'id': 'priority', 'label': 'Priority Tasks', 'tasks': priority_tasks[:3]},
        {'id': 'due', 'label': 'Due Soon', 'tasks': due_tasks[:3]},
        {'id': 'triage', 'label': 'Needs Triage', 'tasks': triage_tasks[:3]}
    ]
    return render_template('index.html', tasks=values, tomorrow=tomorrow)
@app.route('/update', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', type=int)
    start_date = request.form.get('start_date')
    due_date = request.form.get('due_date')

    patch_task(creds, task_id, title, description, priority, start_date, due_date)
    
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = title
            task['description'] = description
            task['priority'] = priority
            task['start_date'] = start_date
            task['due_date'] = due_date
            break
    
    return redirect('/')

@app.route('/reload')
def reload_tasks():
    global tasks
    tasks = get_tasks(creds)
    return redirect('/')

app.run(debug=True, port=5001)