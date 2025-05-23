import os
import sys
import socket
import select
import sqlite3
import asyncio
import random
import json
import requests
from pystyle import Center, Colors, Colorate

os.system(f"title Taskpybot v1.0.0")

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
    by Phillip Alter        (task-pie-bot)          https://github.com/phillip-alter/
""")))

con = sqlite3.connect("TaskBotDb.db")
cur = con.cursor()
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
        chat.send(f"CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership\n".encode("utf-8"))
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
                    print(lines)
                    for line in lines:
                        if "PING" in line:
                            pong_reply = f"PONG {line.split()[1]}\r\n"
                            chat.sendall(pong_reply.encode('utf-8'))
                            print("Pong sent!")
                        elif "PRIVMSG" in line:
                            parts = line.split()
                            mod_check = parts[0]
                            is_mod = False
                            if 'mod=1' in mod_check:
                                is_mod = True
                                print("user is a mod")
                            elif 'broadcaster' in mod_check:
                                is_mod = True
                                print("user is broadcaster")
                            else:
                                print("user is neither a broadcaster nor a mod")
                            user = parts[1].split('!')[0][1:]
                            user.strip()
                            message = " ".join(parts[4:])[1:]
                            print(f"<{user}> {message}")
                            if message.startswith("!"):
                                await handle_command(message,chat,user,is_mod)
                else:
                    await asyncio.sleep(0.1) 
            except socket.error as e:
                print(f"(monitor_commands) Socket error: {e}")
                break
            await asyncio.sleep(0.1) 
    except Exception as e:
        print(f"(monitor_commands) An error occurred: {e}")

def get_mods(chat):
    chat.send(f"PRIVMSG #{channel} :/names CeedTheMediocre\n".encode("utf-8"))


async def handle_command(command, chat, user,is_mod=False):
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
    elif command.startswith("!completetask "):
        task = command[len("!completetask "):]
        print(f"(handle_command) Attempting to complete '{task}' for {user}")
        result = complete_task(user,task)
        print(f"(handle_command) Result of the complete task is {result}")
        if result:
            chat.send(f"PRIVMSG #{channel} :Completing '{task}' from {user}'s list! Good job! \n".encode("utf-8"))
        else:
            chat.send(f"PRIVMSG #{channel} :Unable to complete '{task}' from {user}'s list. Did you check your capitalization and spelling? \n".encode("utf-8"))
    elif command.startswith("!cleartasks"):
        print(f"Clearing list for {user}")
        clear_tasks(user)
    elif command.startswith("!taskhelp"):
        chat.send(f"PRIVMSG #{channel} :Use !addtask <task> to add tasks. Use !removetask <task> to remove. Use !completetask <task> to complete. \n".encode("utf-8"))
    elif command.startswith("!deletetasks "):
        if is_mod:
            target = command[len("!deletetasks @"):]
            print(f"(handle_command) Deleting all tasks for {target}")
            clear_tasks(target)
            chat.send(f"PRIVMSG #{channel} :All tasks for {target} deleted.\n".encode("utf-8"))
        else:
            chat.send(f"PRIVMSG #{channel} :{user}, you do not have permission to use that command.\n".encode("utf-8"))
    elif command.startswith("!endstream"):
        if is_mod:
            clear_completed()
            chat.send(f"PRIVMSG #{channel} :All completed tasks for all users removed.\n".encode("utf-8"))
            notify_shutdown()
            sys.exit(0)
   
    
    

def get_user_id(user):
    cur.execute('''
        SELECT Id
        FROM Users
        WHERE Username = ?;
    ''',(user,))
    result = cur.fetchone()
    return result

def add_user(user):
    if get_user_id(user) is None:
        cur.execute('''
            INSERT INTO Users (Username)
            VALUES (?);
        ''', (user,))
        new_user_id = cur.lastrowid
        con.commit()
        return new_user_id
    else:
        print(f"User '{user}' already exists.")
        return get_user_id(user)[0]
    
def complete_task(user, task_description):
    user_id_result = get_user_id(user)
    if user_id_result is not None:
        user_id = user_id_result[0]
        cur.execute('''
            SELECT Id, IsCompleted
            FROM Tasks
            WHERE TaskDescription = ? AND UserID = ?;
        ''', (task_description, user_id))
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
            notify_ui()
            return True
        else:
            print(f"No task with description '{task_description}' found for user '{user}'.")
            return False
    else:
        print(f"Error: Could not find '{user}'.")
        return False

def remove_task(user, task_description):
    user_id_result = get_user_id(user)
    if user_id_result is not None:
        user_id = user_id_result[0]
        cur.execute('''
            DELETE FROM Tasks
            WHERE TaskDescription = ? AND UserID = ?;
        ''', (task_description, user_id))
        con.commit()
        print(f"Task '{task_description}' for user '{user}' has been removed.")
        notify_ui()
    else:
        print(f"Error: Could not find '{user}'.")

def clear_tasks(user):
    user_id_result = get_user_id(user)
    if user_id_result is not None:
        user_id = user_id_result[0]
        cur.execute('''
            SELECT TaskDescription
            FROM Tasks
            WHERE UserID = ?
        ''',(user_id,))
        results = cur.fetchall()
        if results is not None:
            for r in results:
                remove_task(user, r[0])
            con.commit()
            notify_ui()
    else:
        print(f"Error: could not find {user}")

def clear_completed():
    cur.execute('''
        DELETE FROM Tasks
        WHERE IsCompleted = 1
    ''',)
    con.commit()
    notify_ui()

def add_task(user, task_description):
    user_id_result = get_user_id(user)
    if user_id_result is not None:
        user_id = user_id_result[0]
        cur.execute('''
            INSERT INTO Tasks (UserID, TaskDescription, IsCompleted)
            VALUES (?, ?, 0);
        ''', (user_id, task_description))
        con.commit()
        print(f"Task '{task_description}' added for user '{user}' (ID: {user_id})")
        notify_ui()
    else:
        new_user_id = add_user(user)
        if new_user_id:
            add_task(user, task_description)
        else:
            print(f"Error: Could not add user '{user}', cannot add task.")

def notify_ui():
    try:
        response = requests.get("http://localhost:8080/trigger_refresh", timeout=2)
        print(f"(notify_ui) UI refresh triggered: {response.status_code}")
    except Exception as e:
        print(f"(notify_ui) Failed to contact UI: {e}")

def notify_shutdown():
    try:
        response = requests.get("http://localhost:8080/trigger_shutdown", timeout=2)
        print(f"(notify_ui) UI shutdown triggered: {response.status_code}")
    except Exception as e:
        print(f"(notify_ui) Failed to contact UI: {e}")

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