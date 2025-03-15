from datetime import datetime
import pytest
from task import Task

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
