from datetime import datetime, timedelta, date
from repeat_validation import validate_repeat

class Task:
    def __init__(self, title: str = '', description: str = '', priority: int = 0, due_date: date = None, id: str = '', deleted = False, status: str = 'needsAction', completed: str = '',
                 start_date: date = None, assigned_date: date = None, repeat_start: str = '', repeat_due: str = '', parent_id: str = ''):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.start_date = start_date
        self.assigned_date = assigned_date
        self.repeat_start = repeat_start
        self.repeat_due = repeat_due
        self.notes = ''
        # TODO get rid of this field? It's API only so we could just generate it in to_api_format
        self.completed = completed # String, full-length date of when completed
        self.status = status
        self.id = id
        self.parent_id = parent_id
        self.children = []
        self.deleted = deleted

    # Getters used in the html template
    def start_date_str(self):
        return self.start_date.strftime('%Y-%m-%d') if self.start_date else ''

    def due_date_str(self):
        return self.due_date.strftime('%Y-%m-%d') if self.due_date else ''
        
    def assigned_date_str(self):
        return self.assigned_date.strftime('%Y-%m-%d') if self.assigned_date else ''

    def assigned_date_longstr(self):
        return self.assigned_date.strftime('%Y-%m-%dT%H:%M:%SZ') if self.assigned_date else ''

    def repeat_start_fields(self):
        return self.repeat_start.split() if self.repeat_start else []
    
    def repeat_start_dom(self):
        fields = self.repeat_start_fields()
        return fields[0] if len(fields) > 0 else ''

    def repeat_start_moy(self):
        fields = self.repeat_start_fields()
        return fields[1] if len(fields) > 1 else ''

    def repeat_start_dow(self):
        fields = self.repeat_start_fields()
        return fields[2] if len(fields) > 2 else ''

    def repeat_start_days(self):
        fields = self.repeat_start_fields()
        return fields[3] if len(fields) > 3 else ''

    def repeat_start_from(self):
        fields = self.repeat_start_fields()
        return fields[4] if len(fields) > 4 else ''

    def repeat_due_fields(self):
        return self.repeat_due.split() if self.repeat_due else []
    
    def repeat_due_dom(self):
        fields = self.repeat_due_fields()
        return fields[0] if len(fields) > 0 else ''

    def repeat_due_moy(self):
        fields = self.repeat_due_fields()
        return fields[1] if len(fields) > 1 else ''

    def repeat_due_dow(self):
        fields = self.repeat_due_fields()
        return fields[2] if len(fields) > 2 else ''

    def repeat_due_days(self):
        fields = self.repeat_due_fields()
        return fields[3] if len(fields) > 3 else ''

    def repeat_due_from(self):
        fields = self.repeat_due_fields()
        return fields[4] if len(fields) > 4 else ''
    
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
                    task.repeat_start = field[3:].strip() # legacy import for old repeat fields
                elif field.startswith('#RS:'):
                    task.repeat_start = field[4:].strip()
                elif field.startswith('#RD:'):
                    task.repeat_due = field[4:].strip()
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
        do_delete_task = form_data.get('action_delete') == 'true'

        # Clear start dates from the past
        if task.start_date and task.start_date <= datetime.now().date() and not do_complete_task:
            task.start_date = '' # TODO maybe don't clear if it's a repeating task? Might need the start date for repeating basis
   
        # Handle tomorrow action
        if do_skip_task:
            task.start_date = datetime.now().date() + timedelta(days=1)

        if do_delete_task:
            task.deleted = True
        
        # Handle completion
        if do_complete_task:
            # When completing, assign it to today (if there isn't already an assigned date) so the completed task appears on the calendar (for ego)
            task.assigned_date = task.assigned_date or datetime.now().date()
            task.completed = task.assigned_date_longstr()
            task.status = 'completed'

        repeat_start_dom = form_data.get('repeat-start-dom', '')
        repeat_start_moy = form_data.get('repeat-start-moy', '')
        repeat_start_dow = form_data.get('repeat-start-dow', '')
        repeat_start_days = form_data.get('repeat-start-days', '')
        repeat_start_from = form_data.get('repeat-start-from', '')
        task.repeat_start = f"{repeat_start_dom} {repeat_start_moy} {repeat_start_dow} {repeat_start_days} {repeat_start_from}"
        if not validate_repeat(task.repeat_start):
            task.repeat_start = ''        

        repeat_due_dom = form_data.get('repeat-due-dom', '')
        repeat_due_moy = form_data.get('repeat-due-moy', '')
        repeat_due_dow = form_data.get('repeat-due-dow', '')
        repeat_due_days = form_data.get('repeat-due-days', '')
        repeat_due_from = form_data.get('repeat-due-from', '')
        task.repeat_due = f"{repeat_due_dom} {repeat_due_moy} {repeat_due_dow} {repeat_due_days} {repeat_due_from}"
        if not validate_repeat(task.repeat_due):
            task.repeat_due = ''

        return task

    def to_api_format(self):
        notes = self.description + "\n"
        if self.priority is not None:
            notes += f"#P:{self.priority}\n"
        if self.start_date:
            notes += f"#S:{self.start_date_str()}\n"
        if self.due_date:
            notes += f"#D:{self.due_date_str()}\n"
        if self.repeat_start:
            notes += f"#RS:{self.repeat_start}\n"
        if self.repeat_due:
            notes += f"#RD:{self.repeat_due}\n"  
              
        task = {
            'title': self.title,
            'notes': notes.strip(),
            'completed': self.completed,
            'status': self.status,
            'due': self.assigned_date_longstr()
        }
        
        return task

    def to_dict(self):
        """Convert Task to dictionary for session storage"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'repeat_start': self.repeat_start,
            'repeat_due': self.repeat_due,
            'notes': self.notes,
            'completed': self.completed,
            'status': self.status,
            'parent_id': self.parent_id,
            'children': [child.to_dict() if hasattr(child, 'to_dict') else child for child in self.children],
            'deleted': self.deleted
        }

    @classmethod
    def from_dict(cls, data):
        """Create Task from dictionary (for session deserialization)"""
        task = cls()
        task.id = data.get('id', '')
        task.title = data.get('title', '')
        task.description = data.get('description', '')
        task.priority = data.get('priority', 0)
        
        # Handle date fields
        if data.get('due_date'):
            task.due_date = datetime.fromisoformat(data['due_date']).date()
        if data.get('start_date'):
            task.start_date = datetime.fromisoformat(data['start_date']).date()
        if data.get('assigned_date'):
            task.assigned_date = datetime.fromisoformat(data['assigned_date']).date()
            
        task.repeat_start = data.get('repeat_start', '')
        task.repeat_due = data.get('repeat_due', '')
        task.notes = data.get('notes', '')
        task.completed = data.get('completed', '')
        task.status = data.get('status', 'needsAction')
        task.parent_id = data.get('parent_id', '')
        task.deleted = data.get('deleted', False)
        
        # Handle children
        children_data = data.get('children', [])
        task.children = [cls.from_dict(child) if isinstance(child, dict) else child for child in children_data]
        
        return task
