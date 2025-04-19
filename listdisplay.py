import sqlite3
from dataclasses import dataclass, field
from typing import Callable, List
from nicegui import app, ui

ui.page_title('Task List')

@dataclass
class Task:
    name: str
    completed: bool

@dataclass 
class TaskList:
    title: str
    on_change: Callable
    items: List[Task] = field(default_factory=list)

    def add(self,name: str, completed: bool = False) -> None:
        self.items.append(Task(name,completed))
        self.on_change()
    
    def remove(self,item: Task) -> None:
        self.items.remove(item)
        self.on_change()
        update_ui_tasklists()

con = sqlite3.connect("TaskBotDb.db") # database connection
cur = con.cursor() # cursor to traverse the db
tasklists: List[TaskList] = []
tasklists_to_remove: List[TaskList] = [] # used to store tasklists that will be deleted
curr_index = {'value':0} # used for the rotation function 
skipper: int = 1 # used for timing later, when it comes to autoscroller/rotation.    

@ui.refreshable
def todo_ui(tasklist):
    if not tasklist.items:
        tasklists_to_remove.append(tasklist)
        return
    with ui.card().classes('w-80 items-stretch'): 
        ui.label().bind_text_from(tasklist, 'title').classes('text-semibold text-2xl')
        # shows a progress bar for completed vs not completed 
        ui.linear_progress(sum(item.completed for item in tasklist.items) / len(tasklist.items), show_value=False)
        with ui.row().classes('justify-center w-full'):
            ui.label(f'Completed: {sum(item.completed for item in tasklist.items)}')
            ui.label(f'Remaining: {sum(not item.completed for item in tasklist.items)}')
        for item in tasklist.items:
            with ui.row():
                if item.completed:
                    ui.html('<s>' + item.name + '</s>').classes('flex-grow')
                else:
                    ui.label(item.name).classes('flex-grow')
                # delete button below for testing/troubleshooting 
                #ui.button(on_click=lambda task_list=tasklist, current_item=item: task_list.remove(current_item),icon='delete').props('flat fab-mini color=grey')


def update_from_db():
    cur.execute('''
        SELECT u.Username, t.TaskDescription, t.IsCompleted
        FROM Users u
        JOIN Tasks t ON u.Id = t.UserID
    ''')
    results = cur.fetchall()
    user_tasks = {}
    if results is not None:
        for username, task_description, is_completed in results:
            if username not in user_tasks:
                user_tasks[username] = []
            user_tasks[username].append(Task(task_description,bool(is_completed)))
    for username, tasks in user_tasks.items():
        userlist = TaskList(username,on_change=todo_ui.refresh)
        userlist.items.extend(tasks)
        tasklists.append(userlist)
    tasklists_container.refresh()


def update_ui_tasklists():
    global tasklists_to_remove
    for t in tasklists_to_remove:
        if t in tasklists:
            tasklists.remove(t)
    tasklists_to_remove = []

@ui.refreshable
def tasklists_container():
    if tasklists:
        with ui.column().style('height: 300px; overflow-y: auto;').props('id=scrollable_container'):
            todo_ui(tasklists[curr_index['value']])

def autoscroll():
    global skipper
    if skipper % 2 == 1:
        if tasklists:
            ui.run_javascript(f"""
            const container = document.getElementById('scrollable_container');
            if (container) {{
                const scrollHeight = container.scrollHeight;
                const clientHeight = container.clientHeight;
                const maxScrollTop = scrollHeight - clientHeight;
                let currentScrollTop = container.scrollTop;
                const scrollStep = 3; //higher = faster
                const scrollInterval = 20; //lower = faster

                const scrollDown = () => {{
                    currentScrollTop += scrollStep;
                    if (currentScrollTop >= maxScrollTop) {{
                        container.scrollTop = maxScrollTop;
                    }} else {{
                        container.scrollTop = currentScrollTop;
                        setTimeout(scrollDown, scrollInterval);
                    }}
                }};

                scrollDown();
            }}
            """)
    skipper = (skipper + 1) % 2

def rotate_tasklists():
    if tasklists:
        curr_index['value'] = (curr_index['value'] + 1) % len(tasklists)
        tasklists_container.refresh()

@ui.page('/trigger_refresh')
def trigger_refresh():
    print("Received external refresh trigger")
    tasklists.clear()
    update_from_db()
    tasklists_container.refresh()
    return 'UI refreshed'

@ui.page('/trigger_shutdown')
def trigger_shutdown():
    print("Received external shutdown trigger")
    app.shutdown


# generate the app and set up timers
update_from_db()
with ui.column() as container:
    tasklists_container()
ui.timer(5.0,autoscroll, immediate=False)
ui.timer(10.0, rotate_tasklists, immediate=False)  
if __name__ in {'__main__', '__mp_main__'}: 
    ui.run()