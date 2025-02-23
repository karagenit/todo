from datetime import datetime, timedelta
from repeat import validate_repeat

class Task:
    def __init__(self):
        self.title = ''
        self.description = ''
        self.priority = 0
        self.due_date = '' # Date obj
        self.start_date = '' # Date obj
        self.assigned_date = '' # Date obj
        self.repeat = ''
        self.notes = ''
        # TODO get rid of this field? It's API only so we could just generate it in to_api_format
        self.completed = '' # String, full-length date of when completed
        self.status = 'needsAction'
        self.id = ''
        self.parent_id = ''

    # Getters used in the html template
    def start_date_str(self):
        return self.start_date.strftime('%Y-%m-%d') if self.start_date else ''

    def due_date_str(self):
        return self.due_date.strftime('%Y-%m-%d') if self.due_date else ''
        
    def assigned_date_str(self):
        return self.assigned_date.strftime('%Y-%m-%d') if self.assigned_date else ''

    def assigned_date_longstr(self):
        return self.assigned_date.strftime('%Y-%m-%dT%H:%M:%SZ') if self.assigned_date else ''

    @classmethod
    def from_api_response(cls, response_data):
        task = cls()
        task.id = response_data.get('id', '')
        task.title = response_data.get('title', '')
        task.notes = response_data.get('notes', '')
        task.completed = response_data.get('completed', '') # TODO instead of defaults here, just use the default from __init__
        task.status = response_data.get('status', '')
        task.parent_id = response_data.get('parent', '')
        
        # Parse notes for special fields
        desc_fields = [line.strip() for line in task.notes.splitlines() if line.strip().startswith('#')]
        
        for field in desc_fields:
            try:
                if field.startswith('#P:'):
                    task.priority = int(field[3:].strip())
                elif field.startswith('#D:'):
                    date_str = field[3:].strip()
                    task.due_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                elif field.startswith('#S:'):
                    date_str = field[3:].strip()
                    task.start_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                elif field.startswith('#R:'):
                    task.repeat = field[3:].strip()
            except ValueError:
                pass
                
        # Set description excluding special fields
        task.description = '\n'.join([line.strip() for line in task.notes.splitlines() 
                                    if not line.strip().startswith('#')])
        
        # Handle assigned date
        due_str = response_data.get('due', '')
        task.assigned_date = datetime.strptime(due_str, '%Y-%m-%dT%H:%M:%S.%fZ').date() if due_str else ''
        
        return task

    @classmethod
    def from_form_submission(cls, form_data):
        task = cls()
        task.id = form_data.get('task_id')
        task.title = form_data.get('title')
        task.description = form_data.get('description', '')
        task.priority = form_data.get('priority', type=int, default=0)
        # TODO cleanup
        task.repeat = form_data.get('repeat', '')
        task.parent_id = form_data.get('parent_id')

        start_date_str = form_data.get('start_date', '')
        due_date_str = form_data.get('due_date', '')
        assigned_date_str = form_data.get('assigned_date', '')
        
        # Date field parsing
        task.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else ''
        task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else ''
        task.assigned_date = datetime.strptime(assigned_date_str, '%Y-%m-%d').date() if assigned_date_str else ''

        do_complete_task = form_data.get('action_complete') == 'true'
        do_skip_task = form_data.get('action_tomorrow') == 'true'

        # Clear start dates from the past
        if task.start_date and task.start_date <= datetime.now().date() and not do_complete_task:
            task.start_date = ''     
   
        # Handle tomorrow action
        if do_skip_task:
            task.start_date = datetime.now().date() + timedelta(days=1)
        
        # Handle completion
        if do_complete_task:
            # When completing, assign it to today (if there isn't already an assigned date) so the completed task appears on the calendar (for ego)
            task.assigned_date = task.assigned_date or datetime.now().date()
            task.completed = task.assigned_date_longstr()
            task.status = 'completed'

        # Handle repeat validation
        if not validate_repeat(task.repeat):
            task.repeat = ''
        
        return task

    def to_api_format(self):
        notes = self.description + "\n"
        if self.priority is not None:
            notes += f"#P:{self.priority}\n"
        if self.start_date:
            notes += f"#S:{self.start_date_str()}\n"
        if self.due_date:
            notes += f"#D:{self.due_date_str()}\n"
        if self.repeat:
            notes += f"#R:{self.repeat}\n"
        
        task = {
            'title': self.title,
            'notes': notes.strip(),
            'completed': self.completed,
            'status': self.status,
            'due': self.assigned_date_longstr()
        }
        
        return task
