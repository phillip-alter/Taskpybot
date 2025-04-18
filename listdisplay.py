import sqlite3
import asyncio
from dataclasses import dataclass, field
from typing import Callable, List
from nicegui import ui

'''
Todo:

At start:
1. Connect to database.
2. Pull each user and create a new tasklist for each user.
3. Pull each user's tasks and add them to their respective task list.
4. Disconnect from DB (if req'd)

When bot receives a command to add, remove, update, or clear:
1. Bot calls function in this file, passing in proper parameters for the user & task.
2. functions will add/remove/modify/clear 

When idle:
* List should constantly scroll up and down
    * Moderately slow pace.
    * Pause briefly when at bottom and top.
    * When user adds a new item, scroll to that user then resume scrolling up/down after brief pause
'''

con = sqlite3.connect("TaskBotDb.db")
cur = con.cursor()

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

tasklists: List[TaskList] = []

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
                ui.button(on_click=lambda task_list=tasklist, current_item=item: task_list.remove(current_item),icon='delete').props('flat fab-mini color=grey') #item=item: tasklist.remove(item), icon='delete').props('flat fab-mini color=grey')

tasklists_to_remove: List[TaskList] = []

def update_ui_tasklists():
    for t in tasklists_to_remove:
        if t in tasklists:
            tasklists.remove(t)
    tasklists_to_remove = []
    container.refresh()

@ui.refreshable
def tasklists_container():
    for t in tasklists:
        todo_ui(t)

# example tasks. unnecessary, but good for reference
todos = TaskList('My Weekend', on_change=todo_ui.refresh)
todos.add('Order pizza', completed=True)
todos.add('New NiceGUI Release')
todos.add('Clean the house') 
todos.add('Call mom')

todos2 = TaskList('Testing List 2', on_change=todo_ui.refresh)
todos2.add('Eat pizza')
todos2.add('Finish bot')
todos2.add('Clean the house....again')
todos2.add('call myself')

todos3 = TaskList('Testing List 3', on_change=todo_ui.refresh)
todos3.add('Eat pizza')
todos3.add('Finish bot')
todos3.add('Clean the house....again')
todos3.add('call myself')

todos4 = TaskList('Testing List 4', on_change=todo_ui.refresh)
todos4.add('Eat pizza')
todos4.add('Finish bot')
todos4.add('Clean the house....again')
todos4.add('call myself')

tasklists.extend([todos,todos2,todos3,todos4])

#handles the generation of the list
with ui.column() as container:
    tasklists_container()

if __name__ in {'__main__', '__mp_main__'}: 
    ui.run() 

