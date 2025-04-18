import os
import socket
import select
import sqlite3
import asyncio
import random
import json
from colorama import Fore
from pystyle import Center, Colors, Colorate

os.system(f"title Taskpybot v0.1")

con = sqlite3.connect("TaskBotDb.db")
cur = con.cursor()

print(Colorate.Vertical(Colors.blue_to_purple, Center.XCenter("""
$$$$$$$$\                  $$\                           $$\                  $$\     
\__$$  __|                 $$ |                          $$ |                 $$ |    
   $$ | $$$$$$\   $$$$$$$\ $$ |  $$\  $$$$$$\  $$\   $$\ $$$$$$$\   $$$$$$\ $$$$$$\   
   $$ | \____$$\ $$  _____|$$ | $$  |$$  __$$\ $$ |  $$ |$$  __$$\ $$  __$$\\_$$  _|  
   $$ | $$$$$$$ |\$$$$$$\  $$$$$$  / $$ /  $$ |$$ |  $$ |$$ |  $$ |$$ /  $$ | $$ |    
   $$ |$$  __$$ | \____$$\ $$  _$$<  $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ | $$ |$$\ 
   $$ |\$$$$$$$ |$$$$$$$  |$$ | \$$\ $$$$$$$  |\$$$$$$$ |$$$$$$$  |\$$$$$$  | \$$$$  |
   \__| \_______|\_______/ \__|  \__|$$  ____/  \____$$ |\_______/  \______/   \____/ 
                                     $$ |      $$\   $$ |                             
                                     $$ |      \$$$$$$  |                             
                                     \__|       \______/                              
    by Phillip Alter                               https://github.com/phillip-alter/
""")))

server = "irc.chat.twitch.tv"
port = 6667
with open("settings.json","r") as file:
    x = json.load(file)
channel = x["channel"]
interval = int(x["interval"])
oauth = x["oauth"]
messages = []
with open("messages.txt", "r") as file:
    messages = file.readlines()
botname = "CeedyBot"

async def connect_to_chat():
    chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    chat.setblocking(False)
    try:
        chat.connect_ex((server, port))
        while True:
            await asyncio.sleep(0.1) 
            ready = select.select([], [chat], [])
            if ready[1]:
                break
            elif not ready[0] and not ready[1]:
                print("(connect_to_chat) Connection timeout")
                return None
        chat.send(f"PASS {oauth}\n".encode("utf-8"))
        chat.send(f"NICK {botname}\n".encode("utf-8"))
        chat.send(f"JOIN #{channel}\n".encode("utf-8"))
        await asyncio.sleep(1)
        print(f"(connect_to_chat) Successfully connected to #{channel}")
        return chat
    except socket.error as e:
        print(f"(connect_to_chat) Error connecting: {e}")
        return None

async def post_message(chat): 
    index = 0
    while True:
        message = messages[index % len(messages)].strip()
        try:
            chat.send(f"PRIVMSG #{channel} :{message}\n".encode("utf-8"))
            print(f"(post_message) {message}")
            index = random.randint(0,4)
        except socket.error as e:
            print(f"(post_message) Error sending message: {e}")
            break
        await asyncio.sleep(interval)

async def monitor_commands(chat):
    if not chat:
        print("(monitor_commands) not connected to chat")
        return
    try:
        while True:
            try:
                ready = select.select([chat], [], [], 0.1)
                if ready[0]:
                    data = chat.recv(2048).decode('utf-8')
                    if not data:
                        print("(monitor_commands) Connection closed by server.")
                        break
                    lines = data.strip().split('\n')
                    for line in lines:
                        if "PRIVMSG" in line:
                            parts = line.split()
                            user = parts[0].split('!')[0][1:]
                            user.strip()
                            message = " ".join(parts[3:])[1:]
                            print(f"<{user}> {message}")
                            if message.startswith("!"):
                                await handle_command(message,chat,user)
                else:
                    await asyncio.sleep(0.1) 
            except socket.error as e:
                print(f"(monitor_commands) Socket error: {e}")
                break
            await asyncio.sleep(0.1) 
    except Exception as e:
        print(f"(monitor_commands) An error occurred: {e}")

async def handle_command(command, chat, user):
    if command.startswith("!addtask "):
        task = command[len("!addtask "):]
        chat.send(f"PRIVMSG #{channel} :Adding '{task}' to {user}'s list \n".encode("utf-8"))
        print(f"(handle_command) responding to {command}")
        add_task(user,task)
    elif command.startswith("!removetask "):
        task = command[len("!removetask "):]
        chat.send(f"PRIVMSG #{channel} :Removing '{task}' from {user}'s list \n".encode("utf-8"))
        print(f"(handle_command) Removing {task} from {user}'s list\n")
        remove_task(user,task)
    elif command.startswith("!completetask"):
        task = command[len("!completetask "):]
        chat.send(f"PRIVMSG #{channel} :Completing '{task}' from {user}'s list! Good job! \n".encode("utf-8"))
        print(f"(handle_command) Completing '{task}' for {user}")
        complete_task(user,task)
    elif command.startswith("!help"):
        chat.send(f"PRIVMSG #{channel} :Use !addtask <task> to add tasks. Use !removetask <task> to remove. Use !completetask <task> to complete. \n".encode("utf-8"))
    elif command.startswith("!discord"):
        chat.send(f"PRIVMSG #{channel} :@{user} https://discord.gg/z5aqkzkkBy \n".encode("utf-8"))

def get_user_id(user):
    cur.execute('''
        SELECT Id
        FROM Users
        WHERE Username = ?;
    ''',(user,))
    result = cur.fetchone()
    return result

def get_tasklist_id(user):
    user_id_result = get_user_id(user)
    if user_id_result:
        user_id = user_id_result[0]
        cur.execute('''
            SELECT TaskListID
            FROM Users
            WHERE Id = ?
        ''', (user_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            print(f"Error: Could not find TaskListID for user '{user}'.")
            return None
    else:
        print(f"Error: User '{user}' not found.")
        return None

def add_user(user):
    if get_user_id(user) is None:
        cur.execute('''
            INSERT INTO Users (Username)
            VALUES (?);
        ''', (user,))
        new_user_id = cur.lastrowid
        cur.execute('''
            INSERT INTO TaskList (UserID)
            VALUES (?);
        ''', (new_user_id,))
        con.commit()
        return new_user_id
    else:
        print(f"User '{user}' already exists.")
        return get_user_id(user)[0]
    
def complete_task(user, task_description):
    tasklist_id = get_tasklist_id(user)
    if tasklist_id is not None:
        cur.execute('''
            SELECT Id, IsCompleted
            FROM Tasks
            WHERE TaskDescription = ? AND TaskListID = ?;
        ''', (task_description, tasklist_id))
        task_info = cur.fetchone()
        if task_info:
            task_id = task_info[0]
            current_completion_status = task_info[1]
            new_completion_status = 1 if current_completion_status == 0 else 0
            cur.execute('''
                UPDATE Tasks
                SET IsCompleted = ?
                WHERE Id = ?;
            ''', (new_completion_status, task_id))
            con.commit()
            print(f"Task '{task_description}' for user '{user}' completion status updated to {new_completion_status}.")
        else:
            print(f"No task with description '{task_description}' found for user '{user}'.")
    else:
        print(f"Error: Could not find task list for user '{user}'.")

def remove_task(user, task_description):
    tasklist_id = get_tasklist_id(user)
    if tasklist_id is not None:
        cur.execute('''
            DELETE FROM Tasks
            WHERE TaskDescription = ? AND TaskListID = ?;
        ''', (task_description, tasklist_id))
        con.commit()
        if cur.rowcount > 0:
            print(f"Task '{task_description}' for user '{user}' has been removed.")
        else:
            print(f"No task with description '{task_description}' found for user '{user}'.")
    else:
        print(f"Error: Could not find task list for user '{user}'.")

def add_task(user, task_description):
    user_id_result = get_user_id(user)
    if user_id_result is not None:
        user_id = user_id_result[0]
        cur.execute('''
            SELECT TaskListID
            FROM Users
            WHERE Id = ?;
        ''', (user_id,))
        result = cur.fetchone()
        if result:
            task_list_id = result[0]
            cur.execute('''
                INSERT INTO Tasks (TaskListID, TaskDescription, IsCompleted)
                VALUES (?, ?, 0);
            ''', (task_list_id, task_description))
            con.commit()
            print(f"Task '{task_description}' added for user '{user}' (ID: {user_id})")
        else:
            print(f"Error: Could not retrieve TaskListID for user '{user}'.")
    else:
        new_user_id = add_user(user)
        if new_user_id:
            add_task(user, task_description)
        else:
            print(f"Error: Could not add user '{user}', cannot add task.")

async def main():
    chat = await connect_to_chat()
    if chat:
        await asyncio.gather(
            post_message(chat),
            monitor_commands(chat),
        )
        print("(main) Connection lost.")
        await asyncio.sleep(3)
    
if __name__ == "__main__":
    asyncio.run(main())