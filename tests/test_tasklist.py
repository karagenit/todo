import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, date
import json

from tasklist import upsert_task, update_task, insert_task, delete_task
from task import Task
import api

TEST_CREDS = {"token": "test_token"}

@pytest.fixture
def task():
    return Task(title="Task 0")

@pytest.fixture
def tasks():
    return [
        Task(id="task1", title="Task 1", description="Notes 1"),
        Task(id="task2", title="Task 2", description="Notes 2"),
        Task(id="task3", title="Task 3", description="Notes 3")
    ]

@pytest.fixture
def mock_api(monkeypatch):
    mock_api = MagicMock()
    mock_api.insert_task.return_value = {"id": "newtask"}
    monkeypatch.setattr(api, 'insert_task', mock_api.insert_task)
    monkeypatch.setattr(api, 'move_task', mock_api.move_task)
    monkeypatch.setattr(api, 'patch_task', mock_api.patch_task)
    monkeypatch.setattr(api, 'delete_task', mock_api.delete_task)
    return mock_api

def test_upsert_task__new_task(mock_api, tasks, task):    
    upsert_task(TEST_CREDS, tasks, task)
    mock_api.insert_task.assert_called_once_with(TEST_CREDS, task)
    assert len(tasks) == 4
    assert any(t.id == "newtask" for t in tasks)
    
def test_upsert_task__new_subtask(mock_api, tasks, task):
    task.parent_id = tasks[0].id
    upsert_task(TEST_CREDS, tasks, task)
    mock_api.insert_task.assert_called_once_with(TEST_CREDS, task)
    mock_api.move_task.assert_called_once_with(TEST_CREDS, "newtask", tasks[0].id, None)
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