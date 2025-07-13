import pytest
from unittest.mock import Mock, patch
from task import Task
from reorder import reposition_updated_task

def create_test_task(task_id, title, priority=1):
    """Create a test task with minimal required fields."""
    task = Task()
    task.id = task_id
    task.title = title
    task.priority = priority
    task.assigned_date = ''
    task.due_date = ''
    task.start_date = ''
    task.completed = False
    task.status = 'needsAction'
    return task

@patch('reorder.api.move_task')
def test_reordering_main_example(mock_move_task):
    """Test the reordering logic with the example from the user description."""
    # Create test tasks
    # Sorted order should be: 1, 2, 3, 4, 5 (by priority/date logic)
    task1 = create_test_task("1", "Task 1", priority=3)  # High priority
    task2 = create_test_task("2", "Task 2", priority=3)
    task3 = create_test_task("3", "Task 3", priority=2)  # Medium priority
    task4 = create_test_task("4", "Task 4", priority=2)  # This is our updated task
    task5 = create_test_task("5", "Task 5", priority=1)  # Low priority
    
    # Google-sorted tasks array (current order): [1, 2, 5, 3]
    # Note: task 4 is not in the array yet (it's being updated)
    tasks = [task1, task2, task5, task3]
    
    # Mock credentials
    mock_creds = Mock()
    
    # Reposition task 4
    reposition_updated_task(mock_creds, tasks, task4)
    
    # Expected result: task 4 should be inserted before task 5
    # Final order: [1, 2, 4, 5, 3]
    actual_order = [t.id for t in tasks]
    expected_order = ['1', '2', '4', '5', '3']
    assert actual_order == expected_order
    
    # Verify API call was made with correct parameters
    mock_move_task.assert_called_once_with(mock_creds, "4", None, "2")

@patch('reorder.api.move_task')
def test_insert_at_beginning(mock_move_task):
    """Test inserting a task at the beginning."""
    task1 = create_test_task("1", "Task 1", priority=1)  # Low priority
    task2 = create_test_task("2", "Task 2", priority=1)
    task3 = create_test_task("3", "Task 3", priority=3)  # High priority - should go first
    
    tasks = [task1, task2]
    reposition_updated_task(Mock(), tasks, task3)
    
    actual_order = [t.id for t in tasks]
    expected_order = ['3', '1', '2']
    assert actual_order == expected_order

@patch('reorder.api.move_task')
def test_insert_at_end(mock_move_task):
    """Test inserting a task at the end."""
    task1 = create_test_task("1", "Task 1", priority=3)  # High priority
    task2 = create_test_task("2", "Task 2", priority=3)
    task3 = create_test_task("3", "Task 3", priority=1)  # Low priority - should go last
    
    tasks = [task1, task2]
    reposition_updated_task(Mock(), tasks, task3)
    
    actual_order = [t.id for t in tasks]
    expected_order = ['1', '2', '3']
    assert actual_order == expected_order

@patch('reorder.api.move_task')
def test_insert_into_empty_list(mock_move_task):
    """Test inserting a task into an empty list."""
    task1 = create_test_task("1", "Task 1", priority=2)
    tasks = []
    
    reposition_updated_task(Mock(), tasks, task1)
    
    assert len(tasks) == 1
    assert tasks[0].id == "1"

@patch('reorder.api.move_task')
def test_replace_existing_task(mock_move_task):
    """Test repositioning when the task already exists in the list."""
    task1 = create_test_task("1", "Task 1", priority=3)
    task2 = create_test_task("2", "Task 2", priority=1)  # Lower priority
    task3 = create_test_task("3", "Task 3", priority=2)
    
    # Initial order with task2 in wrong position
    tasks = [task1, task2, task3]
    
    # Update task2's priority to be higher
    updated_task2 = create_test_task("2", "Task 2", priority=3)
    reposition_updated_task(Mock(), tasks, updated_task2)
    
    # Task 2 should now be repositioned based on its new priority
    actual_order = [t.id for t in tasks]
    # Since both task1 and updated_task2 have priority 3, they should stay in order
    # but task2 should come before task3
    expected_order = ['1', '2', '3']
    assert actual_order == expected_order