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
    by Phillip Alter                                        
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
        chat.send(f"PRIVMSG #{channel} :Adding {task} to {user}'s list \n".encode("utf-8"))
        print(f"(handle_command) responding to {command}")
    elif command.startswith("!removetask "):
        task = command[len("!removetask "):]
        chat.send(f"PRIVMSG #{channel} :Removing {task} from {user}'s list \n".encode("utf-8"))
        print(f"(handle_command) Removing {task} from {user}'s list\n")
    elif command.startswith("!completetask"):
        task = command[len("!completetask "):]
        chat.send(f"PRIVMSG #{channel} :Completing {task} from {user}'s list! Good job! \n".encode("utf-8"))
        print(f"(handle_command) Completing {task} for {user}")
    elif command.startswith("!help"):
        chat.send(f"PRIVMSG #{channel} :Use !addtask <task> or !at <task> to add tasks. Use !removetask <task> or !rt <task> to remove. Use !completetask <task> or !ct <task> to complete. \n".encode("utf-8"))

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