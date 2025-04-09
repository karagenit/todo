import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date
import json

from tasklist import upsert_task, update_task, insert_task, delete_task
from task import Task
import api

TEST_CREDS = {"token": "test_token"}
MOCK_API_PATCH_RESP = {"id": "newtask"}

def mock_task():
    return Task(id="task0", title="Task 0")

def mock_tasklist():
    return [
        Task(id="task1", title="Task 1", description="Notes 1"),
        Task(id="task2", title="Task 2", description="Notes 2"),
        Task(id="task3", title="Task 3", description="Notes 3")
    ]

@patch('api.insert_task')
def test_upsert_task__new_task(mock_insert_task):
    mock_insert_task.return_value = MOCK_API_PATCH_RESP
    tasks = mock_tasklist()
    new_task = mock_task()
    new_task.id = ''
    
    upsert_task(TEST_CREDS, tasks, new_task)
    
    mock_insert_task.assert_called_once_with(TEST_CREDS, new_task)
    assert len(tasks) == 4
    assert any(t.id == "newtask" for t in tasks)
      
@patch('api.insert_task')
@patch('api.move_task')
def test_upsert_task__new_subtask(mock_move_task, mock_insert_task):
    mock_insert_task.return_value = MOCK_API_PATCH_RESP
    tasks = mock_tasklist()
    new_task = mock_task()
    new_task.id = ''
    new_task.parent_id = tasks[0].id

    upsert_task(TEST_CREDS, tasks, new_task)

    mock_insert_task.assert_called_once_with(TEST_CREDS, new_task)
    mock_move_task.assert_called_once_with(TEST_CREDS, "newtask", tasks[0].id, None)
    assert len(tasks) == 4
    assert tasks[3].parent_id == tasks[0].id

def test_upsert_task__edit_task():
    return

def test_upsert_task__complete_task():
    return

def test_upsert_task__complete_repeat_start():
    return

def test_upsert_task__complete_repeat_due():
    return

def test_upsert_task__delete_task():
    return