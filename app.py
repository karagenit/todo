from auth import get_creds
from tasks import get_tasks

creds = get_creds()
tasks = get_tasks(creds)

while True:
    user_input = input("> ")
    if user_input == "list":
        for task in tasks:
            print(f"{task['title']} ({task['priority']})")
    elif user_input == "today":
        sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 0), reverse=True)
        for task in sorted_tasks[:3]:
            print(f"{task['title']} ({task['priority']})")
    else:  # Default case
        print("Unknown command")
