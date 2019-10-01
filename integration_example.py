#!/usr/bin/env python3

from tgnoti import TGNotifier

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


if __name__ == "__main__":
    main()
