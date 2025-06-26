import flet as ft
import sqlite3 as sq

class ToDoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.colors.BLACK
        self.page.window_width = 550
        self.page.window_height = 650
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = 'To Do App'
        self.view = 'all'
        self.task = ''
        self.db_execute("CREATE TABLE IF NOT EXISTS tasks(name, status)")
        self.results = self.db_execute('SELECT * FROM tasks')
        self.main_page()
    
    def db_execute(self, query, params = []):
        with sq.connect('tasksToDoApp.db') as con:
            cur = con.cursor()
            cur.execute(query, params)
            con.commit()
            return cur.fetchall()
    
    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label

        if is_checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE name = ?', params=[label])
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE name = ?', params=[label])

        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=[self.view])
        
        self.update_tasks_list()
    
    def tabs_changed(self, e):
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "incomplete"')
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = "complete"')
            self.view = 'complete'

        self.update_tasks_list()
    
    def tasks_container(self):
        return ft.Container(
            height=self.page.height * 0.8,
            content = ft.Column(
                controls = [
                        ft.Checkbox(label=res[0],on_change = self.checked, value = True if res[1] == 'complete' else False)
                        for res in self.results if res
                            ]
                        )
                    )
    
    def grab_value(self, e):
        self.task = e.control.value
        print(self.task)
    
    def addTask(self, e, new_task):
        name = self.task
        status = 'incomplete'
        
        if name:
            self.db_execute(query='INSERT INTO tasks VALUES(?, ?)', params=[name, status])
            new_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_tasks_list()
    
    def update_tasks_list(self):
        tasks = self.tasks_container()
        self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()
    
    def main_page(self):
        new_task = ft.TextField(hint_text = 'Write a new task to do!', expand = True, on_change= self.grab_value)
        input_bar = ft.Row(controls=[
            new_task, 
            ft.FloatingActionButton(icon=ft.icons.ADD, on_click = lambda e: self.addTask(e, new_task))
            ]
        )
        
        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[ft.Tab(text='All tasks!'),
                  ft.Tab(text='Doing!'),
                  ft.Tab(text='Done!')
                  ]
        )
        
        tasks = self.tasks_container()
        
        self.page.add(input_bar, tabs, tasks)

ft.app(target = ToDoApp)