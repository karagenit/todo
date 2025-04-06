from filter import filter_tasks_by_text
from task import Task

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
