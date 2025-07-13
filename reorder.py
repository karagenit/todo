from sort import get_sorted_tasks
import api

def reposition_updated_task(creds, tasks, updated_task):
    """
    Reposition an updated task within the tasks array to maintain proper sort order
    while preserving Google's original ordering for other tasks.
    
    Args:
        creds: Google API credentials
        tasks: List of tasks in Google's sort order
        updated_task: The task that was just updated and needs repositioning
    
    Returns:
        None (modifies tasks array in place and calls API to reorder)
    """
    # First, remove the updated task from the tasks array
    tasks[:] = [task for task in tasks if task.id != updated_task.id]
    
    # Calculate the sorted order for all tasks including the updated one
    all_tasks = tasks + [updated_task]
    sorted_tasks = get_sorted_tasks(all_tasks)
    
    # Find the position of our updated task in the sorted order
    updated_task_index = next((i for i, task in enumerate(sorted_tasks) if task.id == updated_task.id), -1)
    
    if updated_task_index == -1:
        # Should not happen, but fallback to appending at end
        tasks.append(updated_task)
        return
    
    # Find the correct insertion point in the original tasks array
    # We need to find the first task in the tasks array that should come after
    # our updated task according to the sorted order
    insertion_index = len(tasks)  # Default to end of array
    
    for i, task in enumerate(tasks):
        # Find this task's position in the sorted order
        task_sorted_index = next((j for j, sorted_task in enumerate(sorted_tasks) if sorted_task.id == task.id), -1)
        
        # If this task should come after our updated task in sorted order,
        # insert our updated task before it
        if task_sorted_index > updated_task_index:
            insertion_index = i
            break
    
    # Insert the updated task at the correct position
    tasks.insert(insertion_index, updated_task)
    
    # Call API to reorder the task in Google Tasks
    # Find the task that should come immediately before our updated task
    previous_task_id = None
    if insertion_index > 0:
        previous_task_id = tasks[insertion_index - 1].id
    
    # Move the task in Google Tasks API
    api.move_task(creds, updated_task.id, None, previous_task_id)