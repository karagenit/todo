# todo
Google Tasks Interface

## Roadmap

- [ ] Setup google task api access
- [ ] Simple ruby script to list My Tasks
- [ ] Simple ruby script to edit tasks
- [ ] Ruby script to add metadata to task description
- [ ] Ruby script to fetch top 3 tasks to do right now
- [ ] Web interface...

## Metadata Format

Appended to the description of tasks we're tracking to store some additional info for our app that google tasks doesn't store.

```
## VV SS/SS/SS DD/DD/DD P D TTT
V: Format Version Number (01)
S: Start On Date, formatted DDMMYY (no slashes included) (task can be completed on or after this date)
D: Due On Date, formatted DDMMYY (task must be completed before or on this date)
P: Priority 1-3 (Low, Medium, High)
D: Difficulty 1-3 (Easy, Medium, Hard)
T: Time in Minutes

e.g.
##0101092301102322060
Version 01, Starts 01/09/23, Due 01/10/23, Medium Priority, Medium Difficulty, Takes 60 Minutes
```

## Recommendation System

1. Filter tasks to only show those where Start is today or earlier than today
2. (Optional) let the user select how much time they have, only show tasks that have a Time less than or equal to the user selection
3. For each difficulty (Easy, Medium, Hard) select one task sorting first by Due date then by Priority (?)

(?) not sure if it's more important to sort by Due date, Priority, or some combination of the two.
