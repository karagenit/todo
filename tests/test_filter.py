from filter import filter_tasks
from task import Task

def test_empty_search():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks(tasks, "")
    assert result == tasks

def test_null_search():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks(tasks, None)
    assert result == tasks

def test_title_match():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks(tasks, "groceries")
    assert len(result) == 1
    assert result[0].title == "Buy groceries"

def test_description_match():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks(tasks, "milk")
    assert len(result) == 1
    assert result[0].description == "Get milk and bread"

def test_case_insensitive():
    tasks = [
        Task("Buy GROCERIES", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks(tasks, "groceries")
    assert len(result) == 1
    assert result[0].title == "Buy GROCERIES"

def test_no_matches():
    tasks = [
        Task("Buy groceries", "Get milk and bread"),
        Task("Call mom", "Weekly check-in")
    ]
    result = filter_tasks(tasks, "xyz")
    assert len(result) == 0
