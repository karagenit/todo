from auth import get_creds
from tasks import get_tasks, patch_task, insert_task, move_task
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
from repeat import validate_repeat, next_repeat_date
from sort import task_sort_key, get_sorted_tasks
from task import Task

creds = get_creds()
tasks = get_tasks(creds)

app = Flask(__name__)

@app.route('/')
def index():
    today = datetime.now().date()

    # TODO need to use the implied due dates from the sorting algo here?
    # TODO FIXME
    summary_stats = {
    #     'p3': sum(1 for task in tasks if task.get('priority', 0) == 3),
    #     'p2': sum(1 for task in tasks if task.get('priority', 0) == 2),
    #     'p1': sum(1 for task in tasks if task.get('priority', 0) == 1),
    #     'p0': sum(1 for task in tasks if task.get('priority', 0) == 0),
    #     'overdue': sum(1 for task in tasks if task.get('due_date') and datetime.strptime(task['due_date'], '%Y-%m-%d').date() < today),
    #     'today': sum(1 for task in tasks if task.get('due_date') and today <= datetime.strptime(task['due_date'], '%Y-%m-%d').date() < today + timedelta(days=1)),
    #     'week':  sum(1 for task in tasks if task.get('due_date') and today + timedelta(days=1) <= datetime.strptime(task['due_date'], '%Y-%m-%d').date() <= today + timedelta(days=7)),
    #     'month': sum(1 for task in tasks if task.get('due_date') and today + timedelta(days=7) < datetime.strptime(task['due_date'], '%Y-%m-%d').date() <= today + timedelta(days=30))
    }

    sorted_tasks = get_sorted_tasks(tasks)
    # TODO FIXME
    # for task in sorted_tasks:
    #     task['children'] = [{}]
    #     for potential_child in tasks:
    #         if potential_child.get('parent') == task['id']:
    #             task['children'].append(potential_child)
    
    display_tasks = [Task()] + sorted_tasks[:5]

    return render_template('index.html', tasks=display_tasks, stats=summary_stats)

@app.route('/update', methods=['POST'])
def update_task():
    task_id = request.form.get('task_id')
    title = request.form.get('title')
    description = request.form.get('description', '')
    priority = request.form.get('priority', type=int, default=0) # TODO this zero is necessary??
    start_date = request.form.get('start_date', '')
    due_date = request.form.get('due_date', '')
    repeat = request.form.get('repeat', '')
    parent_id = request.form.get('parent_id')
    action_tomorrow = request.form.get('action_tomorrow')
    action_complete = request.form.get('action_complete')
    completed = None
    status = 'needsAction'
    due = None
    assigned_date = request.form.get('assigned_date', '')

    if assigned_date:
        due = datetime.strptime(assigned_date, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%SZ')

    # TODO this causes a problem with repeating. it clears the past start date before we can use it to calculate the next one...
    if start_date and datetime.strptime(start_date, '%Y-%m-%d').date() <= datetime.now().date() and action_complete != "true":
        start_date = ''

    if action_tomorrow == "true":
        start_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')

    if action_complete == "true":
        completed = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        due = due or completed
        status = 'completed'
        tasks[:] = [task for task in tasks if task['id'] != task_id]

    if not validate_repeat(repeat):
        repeat = ''

    if task_id:
        patch_task(creds, task_id, title, description, priority, start_date, due_date, completed, status, due, repeat)
        for task in tasks:
            if task['id'] == task_id:
                task['title'] = title
                task['description'] = description
                task['priority'] = priority
                task['start_date'] = start_date
                task['due_date'] = due_date
                task['repeat'] = repeat
                task['assigned_date'] = assigned_date
                break
        if status == 'completed' and validate_repeat(repeat):
            repeat_start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.now().date()
            next_start = next_repeat_date(repeat_start_date, datetime.now().date(), repeat).strftime('%Y-%m-%d')
            result = insert_task(creds, title, description, priority, next_start, due_date, None, 'needsAction', None, repeat)
            tasks.append({
                'id': result['id'],
                'parent': None,
                'title': title,
                'description': description,
                'priority': priority,
                'start_date': next_start,
                'due_date': due_date,
                'repeat': repeat
            })
            task_id = result['id']
    else:
        result = insert_task(creds, title, description, priority, start_date, due_date, completed, status, due, repeat)
        if parent_id:
            move_task(creds, result['id'], parent_id, None)
        tasks.append({
            'id': result['id'],
            'parent': parent_id,
            'title': title,
            'description': description,
            'priority': priority,
            'start_date': start_date,
            'due_date': due_date,
            'repeat': repeat,
            'assigned_date': assigned_date
        })
        # Needed below when moving the task
        task_id = result['id']
    
    # For non-child tasks, we want to set the order of the task
    if not parent_id:
        sorted_tasks = sorted([task for task in tasks if not task.get('parent')], key=task_sort_key)

        task_index = next((i for i, task in enumerate(sorted_tasks) if task['id'] == task_id), -1)
        if task_index > 0:
            previous_task = sorted_tasks[task_index - 1]
            move_task(creds, task_id, None, previous_task['id'])
    
    return redirect('/')

@app.route('/reload')
def reload_tasks():
    global tasks
    tasks = get_tasks(creds)
    return redirect('/')

app.run(debug=True, port=5001)