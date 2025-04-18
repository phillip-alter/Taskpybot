# Taskpybot
A Twitch bot that has a task list. Chatters can add, remove, and complete tasks from their own personal list.

Originally based on Kichi779's Twitch Chat Bot. Please visit https://github.com/Kichi779/Twitch-Chat-Bot for the original.

## Setting up
1. Edit the settings.json.
    * Replace your_channel_name with your channel's name.
    * Replace 60 with your desired interval. This is 60 seconds by default.
    * Add your oauth token. If you don't have one, visit www.twitchtokengenerator.com on a new account to get one.
2. Edit messages.txt and replace with whatever random messages you want the bot to send in your chat. 
    * The bot will choose a random message from this list and send it every (interval) amount of seconds.
3. Run install.bat
    * This runs pip to install any packages you may not have.
4. Run run.bat
    * This is the actual bot. This tracks the bot's output, anything coming into it, and any errors.

## Commands
* To add a task, type "!addtask \<task description>".
* To remove a task, type "!addtask \<task description>". 
* To mark or unmark a task as completed, type "!completetask \<task description>".
* IMPORTANT NOTE: The task descriptions are CASE SENSITIVE. A task named "Task" and a task named "TAsk" are two different tasks!
