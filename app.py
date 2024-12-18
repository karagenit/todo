from auth import get_creds
from tasks import get_tasks, patch_task, insert_task, move_task
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

creds = get_creds()
tasks = get_tasks(creds)

app = Flask(__name__)

def should_display_task(task):
    today = datetime.now().date()
    no_start_date = not task.get('start_date')
    starts_today_or_earlier = task.get('start_date') and datetime.strptime(task['start_date'], '%Y-%m-%d').date() <= today
    no_parent = not task.get('parent')
    return (no_start_date or starts_today_or_earlier) and no_parent

def task_sort_key(task):
    sort_key = ''
    if not task.get('due_date'):
        priority = task.get('priority', 0)
        if priority == 3:
            sort_key = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        elif priority == 2:
            sort_key = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        elif priority == 1:
            sort_key = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        elif priority == 0:
            sort_key = (datetime.now() + timedelta(days=-7)).strftime('%Y-%m-%d')

    sort_key = task.get('due_date', '9999-12-31')
    # Add priority to the sort order as a tiebreaker for equal dates. Uses 3-priority so higher priority is first since this is sorted least to greatest. 
    # TODO having some issue with no-due-date P3 showing first... seems like priority field isn't being read correctly??
    return sort_key + '-' + str(3 - task.get('priority', 0))

@app.route('/')
def index():
    today = datetime.now().date()

    summary_stats = {
        'p3': sum(1 for task in tasks if task.get('priority', 0) == 3),
        'p2': sum(1 for task in tasks if task.get('priority', 0) == 2),
        'p1': sum(1 for task in tasks if task.get('priority', 0) == 1),
        'p0': sum(1 for task in tasks if task.get('priority', 0) == 0),
        'overdue': sum(1 for task in tasks if task.get('due_date') and datetime.strptime(task['due_date'], '%Y-%m-%d').date() < today),
        'today': sum(1 for task in tasks if task.get('due_date') and today <= datetime.strptime(task['due_date'], '%Y-%m-%d').date() < today + timedelta(days=1)),
        'week':  sum(1 for task in tasks if task.get('due_date') and today + timedelta(days=1) <= datetime.strptime(task['due_date'], '%Y-%m-%d').date() <= today + timedelta(days=7)),
        'month': sum(1 for task in tasks if task.get('due_date') and today + timedelta(days=7) < datetime.strptime(task['due_date'], '%Y-%m-%d').date() <= today + timedelta(days=30))
    }

    ready_tasks = [task for task in tasks if should_display_task(task)]
    sorted_tasks = sorted(ready_tasks, key=task_sort_key)
    for task in sorted_tasks:
        task['children'] = [{}]
        for potential_child in tasks:
            if potential_child.get('parent') == task['id']:
                task['children'].append(potential_child)
    
    display_tasks = [{}] + sorted_tasks[:5]

    return render_template('index.html', tasks=display_tasks, stats=summary_stats)

@app.route('/update', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description', '')
    priority = request.form.get('priority', type=int)
    start_date = request.form.get('start_date', '')
    due_date = request.form.get('due_date', '')
    parent_id = request.form.get('parent_id')
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

    if task_id:
        patch_task(creds, task_id, title, description, priority, start_date, due_date, completed, status, due)
        for task in tasks:
            if task['id'] == task_id:
                task['title'] = title
                task['description'] = description
                task['priority'] = priority
                task['start_date'] = start_date
                task['due_date'] = due_date
                break
    else:
        result = insert_task(creds, title, description, priority, start_date, due_date, completed, status, due)
        if parent_id:
            move_task(creds, result['id'], parent_id)
        tasks.append({
            'id': result['id'],
            'parent': parent_id,
            'title': title,
            'description': description,
            'priority': priority,
            'start_date': start_date,
            'due_date': due_date
        })
    
    return redirect('/')

@app.route('/reload')
def reload_tasks():
    global tasks
    tasks = get_tasks(creds)
    return redirect('/')

app.run(debug=True, port=5001)