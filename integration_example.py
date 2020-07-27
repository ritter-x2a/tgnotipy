#!/usr/bin/env python3

from tgnoti import TGNotifier

def receive_photo(tgn, path):
    updates = tgn.get_updates()
    for upd in updates:
        if upd["message"].get("photo", None) is not None:
            tgn.download_photo_from_msg(upd["message"], path)
            print("download completed")
            break

def main():
    config_file_path = None
    # config_file_path = "/path/to/config"
    tgn = TGNotifier.create(config_file_path)

    # print out the message statistics
    tgn.report_results = True

    tgn.broadcast("starting something", with_host=True, notify=False)

    tgn.broadcast("here is some code:\n```\nprint(\"Hello World\")```\n", with_host=False)

    tgn.broadcast("finished something")

    print("Done sending some messages.")


    print("receiving some messages for 5 seconds")
    updates = tgn.get_updates(timeout=5)
    for upd in updates:
        print(upd["message"]["text"])
    print("Done receiving some messages.")

    # receive_photo(tgn, "test")


if __name__ == "__main__":
    main()
