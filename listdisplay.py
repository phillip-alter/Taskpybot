import sqlite3
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

# Example code used on the NiceGUI website:

@ui.refreshable
def todo_ui():
    if not todos.items:
        ''' this code shows a "List is empty" when there are no items.
        '   instead, we should set it up to delete the task list if the 
        '   user removes the last item from their list (or when the 
        '    admin/mod clears all completed lists at end of stream)
        '''
        ui.label('List is empty.').classes('mx-auto')
        return
    # shows a progress bar for completed vs not completed 
    ui.linear_progress(sum(item.completed for item in todos.items) / len(todos.items), show_value=False)
    # shows a row for "completed/reamining". This is acceptable but I'm unsure if I would use it
    with ui.row().classes('justify-center w-full'):
        ui.label(f'Completed: {sum(item.completed for item in todos.items)}')
        ui.label(f'Remaining: {sum(not item.completed for item in todos.items)}')
    # for each task in 'todos' (a tasklist obj)
    for item in todos.items:
        # create a new row with the class 'items-center' 
        with ui.row().classes('items-center'):
            #create a checkbox; unnecessary for our use
            ui.checkbox(value=item.completed, on_change=todo_ui.refresh).bind_value(item, 'completed') \
                .mark(f'checkbox-{item.name.lower().replace(" ", "-")}')
            #write the name next 
            ui.input(value=item.name).classes('flex-grow').bind_value(item, 'name')
            #delete button. again, unnecessary 
            ui.button(on_click=lambda item=item: todos.remove(item), icon='delete').props('flat fab-mini color=grey')

# example tasks. unnecessary, but good for reference
todos = TaskList('My Weekend', on_change=todo_ui.refresh)
todos.add('Order pizza', completed=True)
todos.add('New NiceGUI Release')
todos.add('Clean the house')
todos.add('Call mom')


#handles the generation of the list
with ui.card().classes('w-80 items-stretch'): #w-80 = width 80%? 
    ui.label().bind_text_from(todos, 'title').classes('text-semibold text-2xl')
    todo_ui() # calls the 
    add_input = ui.input('New item').classes('mx-12').mark('new-item')
    add_input.on('keydown.enter', lambda: todos.add(add_input.value))
    add_input.on('keydown.enter', lambda: add_input.set_value(''))

if __name__ in {'__main__', '__mp_main__'}:
    ui.run()

