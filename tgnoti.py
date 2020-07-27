#!/usr/bin/env python3

import json
import os.path
import requests
import socket
import sys

def get_config_file_path(config_file_path):
    if config_file_path is None:
        prog_name = "tgnotipy"
        config_file_name = "config.json"
        try:
            # If the xdg module is available, try use the xdg config path...
            from xdg import BaseDirectory
            config_path = BaseDirectory.save_config_path(prog_name)
        except ModuleNotFoundError:
            # ...otherwise, use the location of this script.
            config_path = os.path.dirname(os.path.realpath(__file__))
        config_file_path = os.path.join(config_path, config_file_name)

    return config_file_path

def checked_get_request(full_url, data=None):
    try:
        if data is None:
            res = requests.get(full_url)
        else:
            res = requests.get(full_url, data=data)
    except:
        raise TGException("Request failed critically (no internet?)")
    if res.status_code != 200:
        raise TGException("Request failed with status code {}"
                .format(res.status_code))
    return res

class TGException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class TGNotifier:
    def __init__(self, api_key, config_file_path, registered_chats={}):
        self.config_file_path = config_file_path
        self.api_key = api_key
        self.bot_url = "https://api.telegram.org/bot{}".format(self.api_key)
        self.last_update_id = 0
        # maps chat_ids to readable names
        self.registered_chats = registered_chats

        self.report_results = False

    @staticmethod
    def create(config_file_path=None):
        config_file_path = get_config_file_path(config_file_path)
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        if 'api_key' not in config.keys():
            raise TGException("Incomplete config file!")
        if 'registered_chats' not in config.keys():
            raise TGException("Incomplete config file!")
        api_key = config["api_key"]
        registered_chats = config["registered_chats"]
        return TGNotifier(api_key, config_file_path, registered_chats)

    def store_config(self):
        data = {
                'api_key': self.api_key,
                'registered_chats': self.registered_chats,
            }
        with open(self.config_file_path, 'w') as config_file:
            json.dump(data, config_file, indent=2, separators=(',', ': '))

    def get(self, method, data=None):
        full_url = self.bot_url + '/' + method
        res = checked_get_request(full_url, data)
        return res.json()

    def post(self, method, data=None):
        full_url = self.bot_url + '/' + method
        try:
            if data is None:
                res = requests.post(full_url)
            else:
                res = requests.post(full_url, data=data)
        except:
            raise TGException("Request failed critically (no internet?)")
        if res.status_code != 200:
            raise TGException("Request failed with status code {}{}"
                    .format(res.status_code, " (illformed message?)" if res.status_code == 400 else ""))
        return res.json()

    def send_msg(self, chat_id, msg, notify=True):
        payload = {
                'chat_id': chat_id,
                'text': msg,
                'parse_mode': 'markdown',
                'disable_notification': notify,
            }
        self.post("sendMessage", data=payload)

    def send_host_msg(self, chat_id, msg, notify=True):
        hostname = socket.gethostname()
        new_msg = '{msg}\n_from_ `{hostname}`'.format(msg=msg, hostname=hostname)
        self.send_msg(chat_id, new_msg, notify)

    def broadcast(self, msg, with_host=True, notify=False):
        num_success = 0
        num_failure = 0
        for chat_id, name in self.registered_chats.items():
            try:
                if with_host:
                    self.send_host_msg(chat_id, msg, notify)
                else:
                    self.send_msg(chat_id, msg, notify)
            except TGException as e:
                if self.report_results:
                    print("Failed to send message to {}!".format(name), file=sys.stderr)
                    print("Reason: {}".format(e, file=sys.stderr))
                num_failure += 1
            else:
                num_success += 1
        if num_failure > 0:
            if self.report_results:
                print("Done sending messages, {} successful, {} failed."
                    .format(num_success, num_failure), file=sys.stderr)
        else:
            if self.report_results:
                print("Done sending {} message{}."
                    .format(num_success, "s" if num_success != 1 else ""), file=sys.stderr)
        return num_failure

    def add_recent_chats(self):
        new_chats = self.get_recent_chats()
        self.registered_chats.update(new_chats)
        return new_chats

    def get_updates(self, limit=100, timeout=0, allowed_updates=['messages']):
        payload = {
                'offset': self.last_update_id + 1,
                'limit': limit,
                'timeout': timeout,
                'allowed_updates': ['message'],
            }
        data = self.get("getUpdates", payload)
        results = data["result"]

        new_last_update_id = self.last_update_id
        for upd in results:
            curr_id = upd['update_id']
            new_last_update_id = max(new_last_update_id, curr_id)

        self.last_update_id = new_last_update_id

        # Mark these updates as received to the server
        payload['offset'] = new_last_update_id + 1
        self.get("getUpdates", payload)

        return results

    def download_photo_from_msg(self, msg, path):
        photo_sizes = msg.get("photo", None)
        assert photo_sizes is not None
        height = -1
        width = -1
        file_id = None
        for ps in photo_sizes:
            if ps["width"] > width:
                file_id = ps["file_id"]
                width = ps["width"]
                height = ps["height"]

        file_obj = self.get("getFile", {"file_id": file_id})["result"]
        file_path = file_obj["file_path"]
        ext = os.path.splitext(file_path)[1]
        dl_url = "https://api.telegram.org/file/bot{token}/{file_path}".format(token=self.api_key, file_path=file_path)
        r = checked_get_request(dl_url)
        full_path = path + ext
        with open(full_path, "wb") as outfile:
            outfile.write(r.content)
        return full_path

    def get_recent_chats(self):
        updates = self.get_updates(allowed_updates=['message'])
        recent_chats = dict()

        for upd in updates:
            msg = upd['message']
            chat = msg['chat']
            chat_id = chat['id']
            chat_name = "{} {} (@{})".format(
                    chat.get('first_name', '<no first name>'),
                    chat.get('last_name', '<no last name>'),
                    chat.get('username', '<no username>'),
                )
            recent_chats[chat_id] = chat_name

        return recent_chats


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Telegram Bot Notifier')
    parser.add_argument('msg', metavar='MSG', nargs='*',
                    help='the message to send')
    parser.add_argument('-c', '--config', metavar='CFG', default=None,
                    help='use the given config instead of one at the default location')
    parser.add_argument('-n', '--newconfig', metavar='API_KEY', default=None,
                    help='create a new config with this telegram bot api key')
    parser.add_argument('-f', '--find', action='store_true',
                    help='instead of giving a notification, search and add recent chats')
    parser.add_argument('--clear', action='store_true',
                    help='instead of giving a notification, clear the list of registered chats')
    parser.add_argument('--chats', action='store_true',
                    help='instead of giving a notification, print the list of registered chats')
    parser.add_argument('-m', '--mute', action='store_true',
                    help='give a muted notification')
    parser.add_argument('-s', '--stats', action='store_true',
                    help='print sending statistics')
    args = parser.parse_args()

    config_file_path = get_config_file_path(args.config)

    if args.newconfig is not None:
        api_key = args.newconfig
        tgn = TGNotifier(api_key, config_file_path)
        tgn.store_config()
        print("New config created at '{}'.".format(config_file_path), file=sys.stderr)
        exit(0)

    if not os.path.isfile(config_file_path):
        print("Error: No config file found! Consider creating one with '--newconfig <API_KEY>'.", file=sys.stderr)
        exit(1)

    tgn = TGNotifier.create(config_file_path)
    tgn.report_results = args.stats

    if args.find:
        new_chats = tgn.add_recent_chats()
        num = len(new_chats.keys())
        if num == 0:
            print("Found no chats!", file=sys.stderr)
            exit(0)
        elif num == 1:
            print("Found 1 chat:", file=sys.stderr)
        else:
            print("Found {} chats:".format(num), file=sys.stderr)
        for chat_id, name in new_chats.items():
            print("  {}: {}".format(chat_id, name), file=sys.stderr)
        tgn.store_config()
        print("Updated chats were written to config file at '{}'"
                .format(config_file_path), file=sys.stderr)
        exit(0)

    if args.chats:
        chats = tgn.registered_chats
        print("Currently registered chats:", file=sys.stderr)
        for chat_id, name in chats.items():
            print("  {}: {}".format(chat_id, name), file=sys.stderr)
        exit(0)

    if args.clear:
        tgn.registered_chats = {}
        tgn.store_config()
        print("Updated chats were written to config file at '{}'"
                .format(config_file_path), file=sys.stderr)
        exit(0)



    msg = "\n".join(args.msg)
    tgn.broadcast(msg, with_host=True, notify=(not args.mute))


if __name__ == "__main__":
    main()
