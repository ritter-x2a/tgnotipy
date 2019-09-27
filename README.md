# tgnotipy
A telegram chat bot for issuing general purpose notifications from a PC.

Ever had a long-running task on some (possibly remote) machine after whose completion you wanted to be notified so that you could do something with the machine or the produced data?

This project provides you with the tools to avoid repeatedly logging into the machine to see whether the task is already done yet by causing a [Telegram chat bot](https://core.telegram.org/bots) to conveniently send you a message once it's done.

## Prerequesits
You need to have a [Telegram](https://telegram.org/) account as well as an [API key for a chat bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot) (from now on referenced as `<API_KEY>`).
Also, you need to install the required modules, that is `requests` (for convenient http interaction) and `pyxdg` (for finding a place for the config file, strictly speaking not necessary if you always provide the `--config <CFG>` argument, if neither the module is available nor a `--config` is specified, the location of the tgnoti.py script will be used). This can be done as follows via pip:
```
pip install -r requirements.txt
```


## Setup
First, create a config file for your API key on your system:
```
./tgnoti.py --newconfig <API_KEY>
```
The config file is a simple, human-readable and editable json file.
By default, the config file will be placed in a subfolder of your `XDG_CONFIG_BASE` folder (or the folder that contains the tgnoti.py script if the `pyxdg` module is not available). You can use the `--config <CFG>` command line argument to override this choice. (In this case, the `--config <CFG>` argument has to be provided in every future use of the script!)

Then, write a message to your telegram bot from every account that should be notified.
Next, make all these accounts known to your installation:
```
./tgnoti.py --find
```
This command will provide a list with all found chats that will be notified. You can repeat this step at any time to add new chats.
The currently registered chats can be listed with the `--chats` argument and cleared with the `--clear` argument.
The registered chats are stored in the config file, more fine-grained management can be done by editing them in there.

Lastly, try it out:
```
./tgnoti.py "Hello World!"
```
This should send messages to all registered chats. You can send messages without ringing notification with the `--mute` flag.

Optionally: Add convenient shell bindings (e.g. to your `.zshrc`):
```
TGNOTIPY=/path/to/tgnoti.py
function tgn { $TGNOTIPY "Start executing" "\`\`\`" "$*" "\`\`\`"; $* ; $TGNOTIPY "Done executing" "\`\`\`" "$*" "\`\`\`" "return code: \`$?\`" }
```


## Ideas
Python scripts could use the tgnoti.py module to give more fine-grained information about progress.

