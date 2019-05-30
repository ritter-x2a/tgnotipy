# tgnotipy
A telegram chat bot for issuing general purpose notifications from a PC.

Ever had a long-running task on some (possibly remote) machine after whose completion you wanted to be notified so that you could do something with the machine or the produced data?

This project provides you with the tools to avoid repeatedly logging into the machine to see whether the task is already done yet by causing a [Telegram chat bot](https://core.telegram.org/bots) to conveniently send you a message once its done.

## Prerequesits
You need to have a [Telegram](https://telegram.org/) account as well as an [API key for a chat bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot) (from now on referenced as `<API_KEY>`).

## Setup
First, create a config file for your API key on your system:
```
./tgnoti.py --newconfig <API_KEY>
```
By default, the config file will be placed in a subfolder of your `XDG_CONFIG_BASE` folder. You can use the `--config <CFG>` command line argument to override this choice. (in this case, the `--config <CFG>` argument has to be provided in every future use of the script!)

Then, write a message to your telegram bot from every account that should be notified.
Next, make all these accounts known to your installation:
```
./tgnoti.py --find
```
This command will provide a list with all found chats that will be notified. You can repeat this step at any time to add new chats.
These chats are stored in the config file, you can manage them there.

Lastly, try it out:
```
./tgnoti.py "Hello World!"
```
This should send messages to all registered chats.

Optionally: Add convenient shell bindings (e.g. to your .zshrc):
```
TGNOTIPY=/path/to/tgnoti.py
function tgn { $TGNOTIPY "Start executing" "\`\`\`" "$*" "\`\`\`"; $* ; $TGNOTIPY "Done executing" "\`\`\`" "$*" "\`\`\`" "return code: \`$?\`" }
```


## Ideas
Python scripts could use the tgnoti.py module to give more fine grained information about progress.

