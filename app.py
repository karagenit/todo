from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
from repeat import validate_repeat, next_repeat_date
from sort import task_sort_key, get_sorted_tasks
from task import Task
import api
import tasklist

creds = api.get_creds()
tasks = tasklist.from_api(creds)

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
    tasklist.upsert_task(creds, tasks, task)
    
    # FIXME
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
    tasks = tasklist.from_api(creds)
    return redirect('/')

app.run(debug=True, port=5001)