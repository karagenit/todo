from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
from sort import task_sort_key, get_sorted_tasks
from task import Task
from filter_args import FilterArgs
import api
import tasklist
import summary
from filter import filter_tasks

creds = api.get_creds()
tasks = tasklist.from_api(creds)

app = Flask(__name__)

@app.route('/')
def index():
    summary_stats = summary.get_stats(tasks)

    filter_args = FilterArgs(request.args)
    filtered_tasks = filter_tasks(tasks, filter_args)
    sorted_tasks = get_sorted_tasks(filtered_tasks)

    for task in sorted_tasks:
        task.children = [{}]
        for potential_child in tasks:
            if potential_child.parent_id == task.id:
                task.children.append(potential_child)
    
    tasks_to_show = filter_args.count
    display_tasks = [Task()] + sorted_tasks[:tasks_to_show]

    return render_template('index.html', tasks=display_tasks, stats=summary_stats, filter_args=filter_args)

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
    
    return redirect('/' + FilterArgs(request.args).to_url_params())

@app.route('/reload')
def reload_tasks():
    global tasks
    tasks = tasklist.from_api(creds)
    return redirect('/')

app.run(debug=True, port=5001)