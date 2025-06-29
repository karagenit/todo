from datetime import datetime, date, timedelta
import pytest
from task import Task
from werkzeug.datastructures import MultiDict

def test_from_api_response():
    # Arrange
    api_response = {
        'id': 'task123',
        'title': 'Test Task',
        'notes': 'Task description\n#P:2\n#D:2024-01-15\n#S:2024-01-10\n#RS:* * * 3 C',
        'completed': '',
        'status': 'needsAction',
        'parent': 'parent123',
        'due': '2024-01-20T10:00:00.000Z'
    }

    # Act
    task = Task.from_api_response(api_response)

    # Assert
    assert task.id == api_response['id']
    assert task.title == api_response['title']
    assert task.description == 'Task description'
    assert task.priority == 2
    assert task.due_date == datetime.strptime('2024-01-15', '%Y-%m-%d').date()
    assert task.start_date == datetime.strptime('2024-01-10', '%Y-%m-%d').date()
    assert task.repeat_start == '* * * 3 C'
    assert task.status == 'needsAction'
    assert task.parent_id == 'parent123'
    assert task.completed == ''
    assert task.assigned_date == datetime.strptime('2024-01-20', '%Y-%m-%d').date()

# Previously repeat was just stored as "#R:" but then we differentiated into repeat_start and repeat_due. But if a task still has legacy repeat data we should treat it like repeat_start
def test_from_api_response__legacy_repeat():
    api_response = {
        'id': 'task123',
        'title': 'Test Task',
        'notes': '#R:* * * 3 C',
        'completed': '',
        'status': 'needsAction',
        'due': '2024-01-20T10:00:00.000Z'
    }
    task = Task.from_api_response(api_response)
    assert task.repeat_start == '* * * 3 C'

def test_from_form_submission():
    # Arrange - flask uses MultiDict for form data
    form_data = MultiDict([
        ('task_id', 'task123'),
        ('title', 'Test Task'),
        ('description', 'Task description'),
        ('priority', '2'),
        ('start_date', '3024-01-10'), # must be in the future or it will get cleared
        ('due_date', '2024-01-15'),
        ('assigned_date', '2024-01-20'),
        ('repeat-start-dom', '*'),
        ('repeat-start-moy', '*'),
        ('repeat-start-dow', '*'),
        ('repeat-start-days', '3'),
        ('repeat-start-from', 'C'),
        ('parent_id', 'parent123'),
        ('action_complete', 'false'),
        ('action_tomorrow', 'false')
    ])

    # Act
    task = Task.from_form_submission(form_data)

    # Assert
    assert task.id == 'task123'
    assert task.title == 'Test Task'
    assert task.description == 'Task description'
    assert task.priority == 2
    assert task.start_date == date(3024, 1, 10)
    assert task.due_date == date(2024, 1, 15)
    assert task.assigned_date == date(2024, 1, 20)
    assert task.repeat_start == '* * * 3 C'
    assert task.parent_id == 'parent123'
    assert task.completed == ''
    assert task.status == 'needsAction'

def test_from_form_submission_clears_past_start_date():
    form_data = MultiDict([
        ('title', 'Test Task'),
        ('start_date', '2024-01-1')
    ])
    task = Task.from_form_submission(form_data)
    assert task.title == 'Test Task'
    assert task.start_date == ''

def test_from_form_submission_complete_action():
    form_data = MultiDict([
        ('title', 'Test Task'),
        ('action_complete', 'true')
    ])
    task = Task.from_form_submission(form_data)
    assert task.status == 'completed'
    assert task.assigned_date == datetime.now().date() # could fail if run at midnight
    assert task.completed == datetime.now().date().strftime('%Y-%m-%dT%H:%M:%SZ')

def test_from_form_submission_complete_action_assigned_date():
    form_data = MultiDict([
        ('title', 'Test Task'),
        ('action_complete', 'true'),
        ('assigned_date', '2025-01-01')
    ])
    task = Task.from_form_submission(form_data)
    assert task.status == 'completed'
    assert task.assigned_date == date(2025, 1, 1)
    assert task.completed == date(2025, 1, 1).strftime('%Y-%m-%dT%H:%M:%SZ')

def test_from_form_submission_skip_task():
    form_data = MultiDict([
        ('title', 'Test Task'),
        ('action_tomorrow', 'true')
    ])
    task = Task.from_form_submission(form_data)
    assert task.start_date == datetime.now().date() + timedelta(days=1)

# TODO it doesn't actually do this currently
# def test_from_form_submission_invalid_repeat():
#     form_data = MultiDict([
#         ('title', 'Test Task'),
#         ('repeat', 'invalid')
#     ])
#     task = Task.from_form_submission(form_data)
#     assert task.repeat == ''

def test_to_api_format():
    task = Task(
        title='Test Task',
        description='Task description',
        priority=2,
        due_date=date(2024, 1, 15),
        start_date=date(2024, 1, 10),
        assigned_date=date(2024, 1, 20),
        repeat_start='* * * 3 C'
    )
    
    api_format = task.to_api_format()
        
    assert api_format['title'] == 'Test Task'
    assert api_format['notes'] == (
        'Task description\n'
        '#P:2\n'
        '#S:2024-01-10\n'
        '#D:2024-01-15\n'
        '#RS:* * * 3 C'
    )
    assert api_format['completed'] == ''
    assert api_format['status'] == 'needsAction'
    assert api_format['due'] == '2024-01-20T00:00:00Z'
