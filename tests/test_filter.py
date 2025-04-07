from filter import filter_tasks_by_text, filter_tasks_by_children, filter_tasks_by_start
from task import Task
from datetime import date, timedelta

def test_by_text__empty_search():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks_by_text(tasks, "")
    assert result == tasks

def test_by_text__null_search():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks_by_text(tasks, None)
    assert result == tasks

def test_by_text__title_match():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks_by_text(tasks, "groceries")
    assert len(result) == 1
    assert result[0].title == "Buy groceries"

def test_by_text__description_match():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks_by_text(tasks, "milk")
    assert len(result) == 1
    assert result[0].description == "Get milk and bread"

def test_by_text__case_insensitive():
    tasks = [
        Task("Buy GROCERIES", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks_by_text(tasks, "groceries")
    assert len(result) == 1
    assert result[0].title == "Buy GROCERIES"

def test_by_text__no_matches():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks_by_text(tasks, "xyz")
    assert len(result) == 0

def test_by_children__hide_children():
    tasks = [
        Task("Parent task", "Main task"),
        Task("Child task", "Sub task", parent_id=1)
    ]
    result = filter_tasks_by_children(tasks, True)
    assert len(result) == 1
    assert result[0].title == "Parent task"

def test_by_children__show_children():
    tasks = [
        Task("Parent task", "Main task"),
        Task("Child task", "Sub task", parent_id=1)
    ]
    result = filter_tasks_by_children(tasks, False)
    assert result == tasks

def test_by_start__show_future():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    tasks = [
        Task("Current task", "Do today", start_date=today),
        Task("Future task", "Do tomorrow", start_date=tomorrow)
    ]
    result = filter_tasks_by_start(tasks, False)
    assert len(result) == 1
    assert result[0].title == "Current task"

def test_by_start__show_all():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    tasks = [
        Task("Current task", "Do today", start_date=today),
        Task("Future task", "Do tomorrow", start_date=tomorrow)
    ]
    result = filter_tasks_by_start(tasks, True)
    assert result == tasks

def test_by_start__no_start_date():
    today = date.today()
    tasks = [
        Task("No date task", "Do whenever"),
        Task("Current task", "Do today", start_date=today)
    ]
    result = filter_tasks_by_start(tasks, False)
    assert len(result) == 2
