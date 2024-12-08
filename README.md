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

## TODO

- Add new task field
- show assigned on date, maybe auto-assign action button?
- add default 'due' date based on priority
- Add splitting tasks into subtasks
- delete task button
- repeating tasks using cron syntax (creates next upon completion)
- handle auth errors/need to reauth

## Devlog

Getting access to the api was a pain. Went to google cloud console and opened project. https://console.cloud.google.com/apis/api/tasks.googleapis.com/credentials?inv=1&invt=Abijtg&project=seraphic-scarab-433719-k7
Went to enabled APIs then Credentials then Web Task Client. Redirect URLs tried `http://localhost` with and without trailing slash, with and without http**s**. Finally worked with these. Not sure which of the four is necessary. Based on the URL's redirect_uri param it looks like it's `http://localhost:59158/` but you must remove the port number (since port seems random each time). But probalby need to include trailing slash.

Match syntax is only supported in python 3.10 and newer. Brew upgrade python3 didn't work. I have 3.8 in /usr/bin and now 3.13 in /usr/local/bin after brew upgrade. Fricking annoying.