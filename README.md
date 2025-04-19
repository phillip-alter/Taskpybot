# Taskpybot: Your Twitch Task Management Bot

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Taskpybot is a Twitch bot designed to enhance viewer engagement by allowing chatters to manage their own personal task lists directly within your channel's chat. Viewers can easily add, remove, and mark tasks as complete, fostering a sense of organization and interaction within your community.

**This project is a derivative of the excellent [Twitch Chat Bot](https://github.com/Kichi779/Twitch-Chat-Bot) by Kichi779.** I extend my most sincere gratitude to Kichi779 for providing the foundational codebase.

## License

This derivative project, Taskpybot, and the original Twitch Chat Bot project are both licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). A copy of the license is included in this repository.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Significant Changes

This project builds upon the original Twitch Chat Bot with significant modifications to introduce the task list functionality. For a detailed understanding of the changes, please refer to the commit history and specific file modifications within this repository. 

## Setup Instructions

Follow these steps to get Taskpybot up and running:

1.  **Configure Settings:**
    * Locate the `settings.json` file and open it in a text editor.
    * Replace `"your_channel_name"` with your Twitch channel's name (e.g., `"my_awesome_channel"`).
    * Adjust the `"interval"` value (currently `60`) to your desired bot message interval in seconds. This determines how often the bot will send a random message. Recommended times are between 1800 and 3600 seconds -- 30 minutes to one hour. Any quicker and it feels like your bot is spamming your channel!
    * Obtain your Twitch OAuth token by visiting [www.twitchtokengenerator.com](https://www.twitchtokengenerator.com) using a new Twitch account. Paste this token into the appropriate field in `settings.json`.

2.  **Customize Chat Messages:**
    * Open the `messages.txt` file.
    * Replace the existing placeholder messages with your own engaging and relevant messages for your chat. Each message should be on a new line. The bot will randomly select and send one of these messages at the configured interval.

3.  **Install Dependencies:**
    * Run the `install.bat` script. This command uses `pip` to install any necessary Python packages that your system might be missing.

4.  **Run the Bot and Web Interface:**
    * Execute the `run.bat` script. This will simultaneously start both Taskpybot and the NiceGUI web application.
    * **Bot Output:** The command prompt window will display the bot's activity, including incoming Twitch chat messages and any error messages encountered, offering real-time insights into its operation.
    * **Web Interface:** The NiceGUI web interface will be accessible in your web browser at `http://localhost:8080`. This interface outputs the task lists for each user. 
    * **Note:** When first running the web application, there will be no users or tasks. The database is empty. You may have to connect the bot to your channel, add a task yourself, and reset the web application in order to have it displayed. Afterwards, the web application should update automatically.

5. **Add the webapp to your stream:**
    * Add a new browser source to your broadcasting software.
    * When asked for a link, use `http://localhost:8080`. 

## Chat Commands

Viewers can interact with Taskpybot using the following chat commands:

* **`!addtask <task description>`**: Adds a new task with the specified description to your personal task list.
    * **Example:** `!addtask Remember to water the plants`
* **`!removetask <task description>`**: Removes the task with the exact matching description from your personal task list.
    * **Example:** `!removetask Remember to water the plants`
* **`!completetask <task description>`**: Marks the task with the exact matching description as completed (or unmarks it if it's already completed) in your personal task list.
    * **Example:** `!completetask Walk the dog`
* **`!cleartasks`**: Removes **all** tasks from the user's task list. 
* **`!deletetasks <username>`**: **Moderator Only.** Removes all tasks for the specified `<username>`. This command is intended for use when a user abuses the task system.
* **`!endstream`**: **Moderator Only (Optional).** Clears all **completed** tasks for **all** users and then initiates a shutdown of both the bot and the web application. This is typically used at the end of a stream.

**Important Note:** Task descriptions are **case-sensitive**. Ensure that the description you use in commands like `!removetask` and `!completetask` exactly matches the case of the task you want to modify. `"Task"` and `"task"` are treated as different entries.

---

Thank you for using Taskpybot! If you encounter any issues or have suggestions, please feel free to open an issue on this repository.