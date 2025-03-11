from task import Task
import api
from typing import Dict, List

def from_api(creds) -> List[Task]:
    return from_api_response(api.get_tasks(creds))

def from_api_response(results: Dict) -> List[Task]:
    items = results.get("items", [])
    return [Task.from_api_response(item) for item in items]
    # TODO eventually iterate over the cursor token to get more than 100 results