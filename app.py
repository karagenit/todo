from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
from sort import task_sort_key, get_sorted_tasks
from task import Task
from filter_args import FilterArgs
import api
import tasklist
import summary
from filter import filter_tasks
from session import get_user_data, set_user_data, clear_user_data, require_auth
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


@app.route('/')
@require_auth
def index():
    tasks_data = get_user_data('tasks', [])
    tasks = [Task.from_dict(t) if isinstance(t, dict) else t for t in tasks_data]
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
@require_auth
def update_task():
    creds = api.get_session_creds(get_user_data('creds'))
    tasks_data = get_user_data('tasks', [])
    tasks = [Task.from_dict(t) if isinstance(t, dict) else t for t in tasks_data]
    task = Task.from_form_submission(request.form)
    tasklist.upsert_task(creds, tasks, task)
    
    # Update session with serialized tasks
    set_user_data('tasks', [t.to_dict() for t in tasks])
    
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
@require_auth
def reload_tasks():
    creds = api.get_session_creds(get_user_data('creds'))
    tasks = tasklist.from_api(creds)
    set_user_data('tasks', [t.to_dict() for t in tasks])
    return redirect('/')

@app.route('/auth')
def auth():
    try:
        existing_creds = get_user_data('creds')
        creds = api.get_session_creds(existing_creds)
        set_user_data('creds', api.creds_to_dict(creds))
        tasks = tasklist.from_api(creds)
        set_user_data('tasks', [t.to_dict() for t in tasks])
        return redirect('/')
    except Exception as e:
        clear_user_data()
        return f"Authentication failed: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)