"""Flask application for managing todo tasks."""
import os

from flask import Flask, render_template, request, redirect
from sort import get_sorted_tasks
from task import Task
from filter_args import FilterArgs
from auth import get_session_creds, auth_bp
import tasklist
import summary
from filter import filter_tasks
from session import get_user_data, set_user_data, require_auth
from markupsafe import Markup
from reorder import reposition_updated_task

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.register_blueprint(auth_bp)

@app.route('/')
@require_auth
def index():
    """Render the main page with filtered and sorted tasks."""
    tasks = get_user_data('tasks', [])
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

    return render_template(
        'index.html',
        tasks=display_tasks,
        stats=summary_stats,
        filter_args=filter_args
    )

@app.route('/update', methods=['POST'])
@require_auth
def update_task():
    """Update a task based on form submission."""
    creds = get_session_creds(get_user_data('creds'))
    tasks = get_user_data('tasks', [])
    task = Task.from_form_submission(request.form)
    tasklist.upsert_task(creds, tasks, task)
    
    # if not task.parent_id and not task.completed:
        # TODO this isn't working as expected on the google list, need to debug
        # reposition_updated_task(creds, tasks, task)

    set_user_data('tasks', tasks)

    return redirect('/' + FilterArgs(request.args).to_url_params())

@app.route('/reload')
@require_auth
def reload_tasks():
    """Reload tasks from the API."""
    creds = get_session_creds(get_user_data('creds'))
    tasks = tasklist.from_api(creds)
    set_user_data('tasks', tasks)
    return redirect('/')

@app.context_processor
def add_to_context__render_template():
    def render_template_safe(template_name, **kwargs):
        return Markup(render_template(template_name, **kwargs))
    return dict(template=render_template_safe)

if __name__ == '__main__':
    app.run(debug=True, port=5001, ssl_context='adhoc')
