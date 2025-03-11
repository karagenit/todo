import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]


def main():
  """Shows basic usage of the Tasks API.
  Prints the title and ID of the first 10 task lists.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES # access_type="offline", prompt="consent" not valid params for this function, thanks a lot claude
      )
      creds = flow.run_local_server(port=0, prompt="consent")
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("tasks", "v1", credentials=creds)

    # Call the Tasks API
    results = service.tasks().list(tasklist="MDk5NzIwMDMyNTExNzU4MzkzMjI6MDow", showCompleted=False, maxResults=100).execute()
    items = results.get("items", [])

    if not items:
      print("No tasks found.")
      return

    print("Tasks:")
    print(f"Number of tasks: {len(items)}")
    for item in items:
      print(f"{item['title']} ({item['id']})")
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()