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
    display_tasks = []
    # Only want to display tasks with either no start date or a start date NOT in the future
    task_queue = [task for task in tasks if not task.get('start_date') or datetime.strptime(task['start_date'], '%Y-%m-%d').date() <= today]
    # Get first highest priority task
    task_queue = sorted(task_queue, key=lambda x: (-x.get('priority', 0), x.get('due_date', '9999-12-31')))
    display_tasks.append(task_queue.pop(0))
    # Get first soonest due task
    task_queue = sorted(task_queue, key=lambda x: x.get('due_date', '9999-12-31'))
    display_tasks.append(task_queue.pop(0))
    # Get first task that needs to be triaged as well
    task_queue = [task for task in task_queue if task.get('priority', 0) == 0]
    display_tasks.append(task_queue.pop(0))
    # Render
    return render_template('index.html', tasks=display_tasks)

@app.route('/update', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', type=int)
    start_date = request.form.get('start_date')
    due_date = request.form.get('due_date')
    action_tomorrow = request.form.get('action_tomorrow')
    action_complete = request.form.get('action_complete')
    completed = None
    status = 'needsAction'
    due = None

    if action_tomorrow == "true":
        start_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')

    if action_complete == "true":
        completed = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        due = completed
        status = 'completed'
        tasks[:] = [task for task in tasks if task['id'] != task_id]

    patch_task(creds, task_id, title, description, priority, start_date, due_date, completed, status, due)
    
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