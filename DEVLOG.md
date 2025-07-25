## Metadata Format

Appended to the description of tasks we're tracking to store some additional info for our app that google tasks doesn't store.

```
V: Format Version Number (01)
S: Start On Date, formatted DDMMYY (no slashes included) (task can be completed on or after this date)
D: Due On Date, formatted DDMMYY (task must be completed before or on this date)
P: Priority 1-3 (Low, Medium, High)
D: Difficulty 1-3 (Easy, Medium, Hard)
T: Time in Minutes
```

## Recommendation System

1. Filter tasks to only show those where Start is today or earlier than today
2. (Optional) let the user select how much time they have, only show tasks that have a Time less than or equal to the user selection
3. For each difficulty (Easy, Medium, Hard) select one task sorting first by Due date then by Priority (?)

(?) not sure if it's more important to sort by Due date, Priority, or some combination of the two.

## TODO

- Auto-assigning tasks by priority and due dates
- Support due date repeating
- handle auth errors/need to reauth
- saving empty taks works but probalby fails on api
- today button doesn't make save button appear
- allow editing subtask title
- adjust comment box height dynamically
- allow searching for tasks; deduplicate tasks
- clear date button
- zero P tasks should appear before tasks with a due date in the past...
- use assigned date in place of start date too (hide tasks assigned in the future)
- deleting tasks still creates repeating task
- button: complete task w/o repeating
- skip to next repetition w/o completing
- dedupe - X possible duplicates found etc.

- Pylint files
- test plans for files, reorganize lots of test coverage
- move requires_auth decorator into auth.py (and tests)
- get rid of _oauth_flows and just store in session
- fetch default tasklist ID dynamically instead of hardcoding it in api.py and reauth.py

- bug: first oauth attempt after a while, has an old session cookie it tries to auth from but fails. need to retry auth. not sure how to fix
- bug: complete a repeating task with "repeat 1 day after due" that was due a month ago, will create a second task that's due a month ago as well (1 day after) - the next due date calculation should use max(last due date, current date) to avoid this
- feature: allow completing from google UIs. Add "#Completed" attribute. Fetch completed tasks from API and look for ones without "#Completed" tag. Handle repeat etc. for those, then add "#Completed" to them. 

## Devlog

Getting access to the api was a pain. Went to google cloud console and opened project. https://console.cloud.google.com/apis/api/tasks.googleapis.com/credentials?inv=1&invt=Abijtg&project=seraphic-scarab-433719-k7
Went to enabled APIs then Credentials then Web Task Client. Redirect URLs tried `http://localhost` with and without trailing slash, with and without http**s**. Finally worked with these. Not sure which of the four is necessary. Based on the URL's redirect_uri param it looks like it's `http://localhost:59158/` but you must remove the port number (since port seems random each time). But probalby need to include trailing slash.

Match syntax is only supported in python 3.10 and newer. Brew upgrade python3 didn't work. I have 3.8 in /usr/bin and now 3.13 in /usr/local/bin after brew upgrade. Fricking annoying.

## uh

Jan 31

all the sudden the script fails with 'google' couldnot be found. the module is installed with pip. no idea why it can't be found. pip3 can't install stuff due to it being a 'managed environment'. gotta create a virtual environment???

    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz

    caleb@Calebs-MacBook-Pro todo % python3 -m venv /Users/caleb/python/venv  
caleb@Calebs-MacBook-Pro todo % source /Users/caleb/python/venv/bin/activate
(venv) caleb@Calebs-MacBook-Pro todo % python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

## Repeating

- `*` any value
- `,` list of values
- `-` range of values
- `/` step values

1. Day of Month [1-31]
2. Month of Year [1-12]
3. Day of Week [0-6] sun-sat
4. Days Since [0-999] 
5. Last Start [S] or Completion [C]

Separate repeat fields for start and due? Most cases will just be start - ie start this after a certain interval but then just treat it as a p2/p3 whatever. But some cases things might have a specific due date that repeats as well.

## Multi-User Refactor

This repository is a google tasks wrapper with a custom UI and some extra features for tasks, like greater control of repeating logic and adding both start-after and due-before dates. Right now, the web app is only designed for one user at a time. When the app is started, get_creds in api.py is used to get the API token for that one user. Instead, we want to refactor this project to support multiple users at the same time. Instead of passing around the creds from get_creds, we should store a given user's creds as a session variable. Similarly we should not store one global 'tasks' tasklist, but should store each user's tasklist separately as a session variable. 

Come up with a step-by-step plan to complete this refactor. At a minimum, we should do the following:
1. Create a new git branch for this feature
2. Guard each route in app.py with a check for session[creds]
3. In the event that a user is missing session[creds], redirect to /auth
4. Create a new route for /auth which gets a user's API token, similar to how get_creds works
  a. This new flow should not read/write any files containing the token, just keep them in memory
  b. This route should also reload session[tasks] as well
  b. Once complete, this should now redirect back to '/'
5. Update any uses of 'creds' in app.py to use session[creds] instead
6. Update any uses of 'tasks' in app.py to use session[tasks] instead
7. Create a test plan, including test coverage for app.py that covers these changes

# Multi-User Session Test Plan

## Test Scenarios

### 1. Authentication Flow Tests
- **Test 1.1**: New user visits `/` → redirected to `/auth` → completes OAuth → redirected to `/`
- **Test 1.2**: User with expired session visits `/` → redirected to `/auth`
- **Test 1.3**: User visits `/auth` directly → completes OAuth → redirected to `/`
- **Test 1.4**: Authentication failure handling → session cleared → error message

### 2. Session Management Tests
- **Test 2.1**: Session persists across page refreshes
- **Test 2.2**: Session expires after browser closure (session cookies)
- **Test 2.3**: Multiple users in different browsers have isolated sessions
- **Test 2.4**: User can re-authenticate after session expiry

### 3. Multi-User Isolation Tests
- **Test 3.1**: User A's tasks not visible to User B
- **Test 3.2**: User A's task updates don't affect User B's view
- **Test 3.3**: Concurrent task operations by different users
- **Test 3.4**: Each user sees their own summary statistics

### 4. Route Protection Tests
- **Test 4.1**: `/` requires authentication
- **Test 4.2**: `/update` requires authentication
- **Test 4.3**: `/reload` requires authentication
- **Test 4.4**: `/auth` accessible without authentication

### 5. Credential Refresh Tests
- **Test 5.1**: Expired credentials automatically refresh
- **Test 5.2**: Invalid refresh token triggers re-authentication
- **Test 5.3**: Network errors during credential refresh

### 6. Data Consistency Tests
- **Test 6.1**: Task updates persist in session
- **Test 6.2**: Reload functionality updates session tasks
- **Test 6.3**: Filter operations work with session data
- **Test 6.4**: Task hierarchy (parent/child) maintained per user

## Automated Test Implementation

### Unit Tests (test_app.py)
1. Test `require_auth` decorator
2. Test session credential conversion functions
3. Test route responses with/without authentication
4. Test error handling in auth flow

### Integration Tests
1. Test complete authentication flow
2. Test multi-user task isolation
3. Test session persistence
4. Test credential refresh scenarios

## Manual Testing Checklist

### Setup
- [ ] Start application with `python app.py`
- [ ] Open multiple browser windows (different users)
- [ ] Ensure `credentials.json` exists

### Test Execution
- [ ] Test 1: New user authentication flow
- [ ] Test 2: Multiple users simultaneously
- [ ] Test 3: Session expiry handling
- [ ] Test 4: Task operations per user
- [ ] Test 5: Reload functionality
- [ ] Test 6: Error scenarios

### Expected Outcomes
- Each user maintains isolated task lists
- Authentication redirects work correctly
- No cross-user data leakage
- Session management functions properly
- All routes protected appropriately

## July 15, 2025

Discovered a critical issue with task ordering. The Google Tasks API documentation doesn't clearly explain what order tasks are returned in. Initially assumed it was by position field (which would match the Google Tasks UI ordering), but debugging revealed that the API actually returns tasks in order of last updated datetime, not position. This was causing sorting inconsistencies where tasks appeared in different orders in our app versus the Google Tasks UI.

Fixed by explicitly sorting the items array by position field in `from_api()` before converting to Task objects. This ensures our app maintains the same task order as the Google Tasks UI, regardless of when tasks were last updated.

The confusion arose because the first few tasks happened to have positions that matched their last-updated order, making it appear the API was returning them in position order when it was actually coincidental.