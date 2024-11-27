from auth import get_creds
from tasks import get_tasks

creds = get_creds()
tasks = get_tasks(creds)

while True:
    user_input = input("> ")
    if user_input == "list":
        for task in tasks:
            if 'priority' in task:
                print(f"{task['title']} ({task['priority']})")
            else:
                print(task['title'])
    else:  # Default case
        print("Unknown command")
