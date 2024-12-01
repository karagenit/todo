from auth import get_creds
from tasks import get_tasks
from flask import Flask, render_template, request, redirect

creds = get_creds()
tasks = get_tasks(creds)

app = Flask(__name__)

@app.route('/')
def index():
    sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 0), reverse=True)
    top_tasks = sorted_tasks[:3]
    pending_task = next((task for task in tasks if task.get('priority', 0) == 0), None)
    
    return render_template('index.html', tasks=top_tasks, pending_task=pending_task)

@app.route('/update', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', type=int)
    start_date = request.form.get('start_date')
    due_date = request.form.get('due_date')

    # TODO update via google api too, not just in-memory. if an error we should handle it without losing user changes
    
    for task in tasks:
        if task['id'] == task_id:
            task['title'] = title
            task['description'] = description
            task['priority'] = priority
            task['start_date'] = start_date
            task['due_date'] = due_date
            break
    
    return redirect('/')
# TODO button to force reload from api

app.run(debug=True)