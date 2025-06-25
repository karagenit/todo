# Todo Task Manager

A Flask web application that provides an enhanced interface for Google Tasks with additional features like custom metadata, advanced filtering, and task recommendations.

## Features

- **Google Tasks Integration**: Seamlessly syncs with your Google Tasks account
- **Multi-User Support**: Individual user sessions with OAuth authentication
- **Enhanced Task Metadata**: Track start dates, due dates, priority (1-3), difficulty (1-3), and time estimates
- **Smart Filtering**: Filter tasks by various criteria including dates and priority
- **Task Recommendations**: Get task suggestions based on available time and priorities
- **Subtask Support**: Create and manage hierarchical task structures
- **Repeating Tasks**: Support for recurring tasks with custom repeat patterns

## Setup

### Prerequisites
- Python 3.10 or newer
- Google Cloud Console project with Tasks API enabled
- OAuth credentials configured

### Installation

1. **Set up Python virtual environment:**
   ```bash
   python3 -m venv ~/python/venv
   source ~/python/venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib flask pytest
   ```

3. **Configure Google OAuth:**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Tasks API
   - Create OAuth 2.0 credentials (Web application)
   - Set redirect URI to `http://localhost:5001/oauth/callback`
   - Download credentials and save as `credentials.json` in the project root

4. **Set environment variables:**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   ```

## Usage

### Running the Application

1. **Activate virtual environment:**
   ```bash
   source ~/python/venv/bin/activate
   ```

2. **Start the application:**
   ```bash
   python3 app.py
   ```

3. **Access the application:**
   Open your browser to `https://localhost:5001`

### First Time Setup
- Visit the application URL
- You'll be redirected to Google OAuth for authentication
- Grant permissions to access your Google Tasks
- You'll be redirected back to the main interface

### Testing

Run the test suite:
```bash
pytest .
```

Run with coverage:
```bash
pytest --cov .
```

## Development

The application supports multiple users through session-based authentication. Each user's credentials and tasks are stored separately in their session.

### Key Components
- `app.py`: Main Flask application with routes
- `auth.py`: OAuth authentication handling
- `session.py`: Session management and user data storage
- `task.py`: Task model and form handling
- `tasklist.py`: Google Tasks API integration
- `filter.py`: Task filtering logic
- `sort.py`: Task sorting and recommendations