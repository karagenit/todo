from datetime import datetime, date
import pytest
from task import Task
from werkzeug.datastructures import MultiDict

def test_from_api_response():
    # Arrange
    api_response = {
        'id': 'task123',
        'title': 'Test Task',
        'notes': 'Task description\n#P:2\n#D:2024-01-15\n#S:2024-01-10\n#R:* * * 3 C',
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
    assert task.repeat == '* * * 3 C'
    assert task.status == 'needsAction'
    assert task.parent_id == 'parent123'
    assert task.completed == ''
    assert task.assigned_date == datetime.strptime('2024-01-20', '%Y-%m-%d').date()

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
        ('repeat', '* * * 3 C'),
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
    assert task.repeat == '* * * 3 C'
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
    # Arrange
    form_data = MultiDict([
        ('title', 'Test Task'),
        ('action_complete', 'true')
    ])

    # Act
    task = Task.from_form_submission(form_data)

    # Assert
    assert task.title == 'Test Task'
    assert task.status == 'completed'
    assert task.assigned_date == datetime.now().date() # could fail if run at midnight
    assert task.completed == datetime.now().date().strftime('%Y-%m-%dT%H:%M:%SZ')


# TODO test clears old start date, complete works, skip works, invalid repeat works
