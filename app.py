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
    summary_stats = {
        'p3': sum(1 for task in tasks if task.priority == 3),
        'p2': sum(1 for task in tasks if task.priority == 2),
        'p1': sum(1 for task in tasks if task.priority == 1),
        'p0': sum(1 for task in tasks if task.priority == 0),
        'overdue': sum(1 for task in tasks if task.due_date and task.due_date < today),
        'today': sum(1 for task in tasks if task.due_date and today <= task.due_date < today + timedelta(days=1)),
        'week':  sum(1 for task in tasks if task.due_date and today + timedelta(days=1) <= task.due_date <= today + timedelta(days=7)),
        'month': sum(1 for task in tasks if task.due_date and today + timedelta(days=7) < task.due_date <= today + timedelta(days=30))
    }
    sorted_tasks = get_sorted_tasks(tasks)

    for task in sorted_tasks:
        task.children = [{}]
        for potential_child in tasks:
            if potential_child.parent_id == task.id:
                task.children.append(potential_child)
    
    display_tasks = [Task()] + sorted_tasks[:5]

    return render_template('index.html', tasks=display_tasks, stats=summary_stats)

@app.route('/update', methods=['POST'])
def update_task():
    task = Task.from_form_submission(request.form)

    if task.id:
        patch_task(creds, task)
        # Replace the old task in this array with the new task
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                break
        # FIXME for repeating
        # if status == 'completed' and validate_repeat(repeat):
        #     repeat_start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.now().date()
        #     next_start = next_repeat_date(repeat_start_date, datetime.now().date(), repeat).strftime('%Y-%m-%d')
        #     result = insert_task(creds, title, description, priority, next_start, due_date, None, 'needsAction', None, repeat)
        #     tasks.append({
        #         'id': result['id'],
        #         'parent': None,
        #         'title': title,
        #         'description': description,
        #         'priority': priority,
        #         'start_date': next_start,
        #         'due_date': due_date,
        #         'repeat': repeat
        #     })
        #     task_id = result['id']
    else:
        result = insert_task(creds, task)
        task.id = result['id']
        if task.parent_id:
            move_task(creds, task.id, task.parent_id, None)
        tasks.append(task)
        # Needed below when moving the task
        task_id = result['id']
    
    # For non-child tasks, we want to set the order of the task
    # if not parent_id:
    #     sorted_tasks = sorted([task for task in tasks if not task.get('parent')], key=task_sort_key)

    #     task_index = next((i for i, task in enumerate(sorted_tasks) if task['id'] == task_id), -1)
    #     if task_index > 0:
    #         previous_task = sorted_tasks[task_index - 1]
    #         move_task(creds, task_id, None, previous_task['id'])
    
    return redirect('/')

@app.route('/reload')
def reload_tasks():
    global tasks
    tasks = get_tasks(creds)
    return redirect('/')

app.run(debug=True, port=5001)