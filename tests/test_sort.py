import pytest
from datetime import datetime, timedelta
from sort import should_display_task, task_sort_key, get_sorted_tasks

def test_should_display_task_no_dates():
    task = {'title': 'Test Task', 'priority': 1}
    assert should_display_task(task) == True

def test_should_display_task_future_start():
    future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    task = {'title': 'Future Task', 'start_date': future_date}
    assert should_display_task(task) == False

def test_should_display_task_past_start():
    past_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    task = {'title': 'Past Task', 'start_date': past_date}
    assert should_display_task(task) == True

def test_should_display_task_with_parent():
    task = {'title': 'Child Task', 'parent': 'Parent Task'}
    assert should_display_task(task) == False

def test_task_sort_key_priority_only():
    tasks = [
        {'title': 'High Priority', 'priority': 3},
        {'title': 'Low Priority', 'priority': 0},
        {'title': 'Medium Priority', 'priority': 2}
    ]
    sorted_keys = [task_sort_key(task) for task in tasks]
    # P0 comes first, then P3 P2 P1 because P0 needs to be triaged still
    assert sorted_keys[1] < sorted_keys[0]
    assert sorted_keys[0] < sorted_keys[2]

def test_task_sort_key_with_due_date():
    start_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
    task = {'title': 'Due Task', 'due_date': due_date, 'start_date': start_date, 'priority': 2}
    sort_key = task_sort_key(task)
    assert sort_key.startswith(due_date)

def test_task_sort_key_with_assigned_date():
    due_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    assigned_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    task = {'title': 'Assigned Task', 'assigned_date': assigned_date, 'due_date': due_date, 'priority': 2}
    sort_key = task_sort_key(task)
    assert sort_key.startswith(assigned_date)

def test_task_sort_key_priority_tiebreaker():
    today = datetime.now().strftime('%Y-%m-%d')
    tasks = [
        {'title': 'Task 1', 'due_date': today, 'priority': 3},
        {'title': 'Task 2', 'due_date': today, 'priority': 2}
    ]
    key1 = task_sort_key(tasks[0])
    key2 = task_sort_key(tasks[1])
    assert key1 < key2

def test_task_sort_key_priority_fallback():
    tasks = [
        {'title': 'Task 1', 'priority': 3},
        {'title': 'Task 2', 'priority': 2},
        {'title': 'Task 3', 'priority': 1}
    ]
    
    today = datetime.now()
    expected_dates = [
        (today + timedelta(days=7)).strftime('%Y-%m-%d'),
        (today + timedelta(days=14)).strftime('%Y-%m-%d'),
        (today + timedelta(days=30)).strftime('%Y-%m-%d')
    ]
    
    keys = [task_sort_key(task) for task in tasks]
    
    # Check that each key starts with the expected implied date based on priority
    for i, key in enumerate(keys):
        assert key.startswith(expected_dates[i])
    

def test_get_sorted_tasks():
    tasks = [
        {'title': 'High Priority', 'priority': 3},
        {'title': 'Low Priority', 'priority': 0},
        {'title': 'Medium Priority', 'priority': 2},
        {'title': 'Future Task', 'start_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')},
        {'title': 'Child Task', 'parent': 'Parent Task'}
    ]
    sorted_tasks = get_sorted_tasks(tasks)
    assert len(sorted_tasks) == 3  # Only tasks without parent and not in future
    assert sorted_tasks[0]['priority'] == 0
    assert sorted_tasks[1]['priority'] == 3
    assert sorted_tasks[2]['priority'] == 2

def test_get_sorted_tasks_empty():
    assert get_sorted_tasks([]) == []
