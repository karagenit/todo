# Running Python & Testing
- Use venv with python by running the following:
  - `python3 -m venv /Users/caleb/python/venv`
  - `source /Users/caleb/python/venv/bin/activate`
- Use `python3 <script>` to run a python script
- To test the repo, run `pytest .` after activating venv

# OAuth Implementation
- The app uses Google OAuth for authentication with a regular Flow instead of InstalledAppFlow
- OAuth redirect URL is set to `http://localhost:5001/oauth/callback`
- OAuth flows are temporarily stored in memory using the state parameter as key
- Session only stores the OAuth state, not the entire flow object (for serialization compatibility)