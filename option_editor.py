# -*- coding: utf-8 -*-

import os
import sys
import time
import option


def cls():
    r = os.system("clear")
    if r == 1:
        os.system("cls")


class options:
    class lang:
        explain = "Language setting"
        child_option = None
        default = "ko"
        value_type = str
        value = option.lang

    class prefix:
        explain = "BOT Prefix"
        child_option = None
        default = ";"
        value_type = str
        value = option.prefix

    class music_dir:
        explain = "Music Indexing Folder"
        child_option = None
        default = "./data/music/"
        value_type = str
        value = option.music_dir

    class private_mode:
        explain = "Hide Music Info (only private bot can use it)"
        child_option = None
        default = 0
        value_type = int
        value = option.private_mode

    class save_guild_data:
        explain = "Save bot joined guilds"
        child_option = None
        default = 0
        value_type = int
        value = option.save_guild_data


def get_keys(target_class, get_all=False):
    result = []
    for k in dir(target_class):
        if get_all is False:
            if not k.startswith("__") and not k.startswith("explain"):
                result.append(k)
        elif get_all is True:
            if not k.startswith("__"):
                result.append(k)
    return result


def reset_options():
    print("=-" * 30)
    keys = get_keys(options, True)
    for key in keys:
        default = getattr(options, key).default
        old_value = getattr(options, key).value

        if default is not old_value:
            print(f"Try to change {key} to default value...")
            update(key, old_value, default)
        else:
            print(f"{key} is default value. skipping...")
    save_option(True)


def show_options():
    cls()
    print("=-" * 30)
    print("You can edit this options \n")
    print(get_keys(options))
    print("=-" * 30)

    do = input("Edit What? : ")
    show_details(do)


def show_details(name):
    cls()
    name = name.lstrip().lower()
    allow_keys = get_keys(options)
    print("=-" * 30)
    if name in allow_keys:
        print(f"{name}: {getattr(options, name).explain}")
        detail_keys = get_keys(getattr(options, name))
        for key in detail_keys:
            print(f" - {key}")

        next_key = input("Check What? : ")
        show_child(name, next_key)
    else:
        if name == "exit":
            print("Good Bye")
            sys.exit(0)
        elif name == "back":
            show_options()

        print("Wrong Key!")
        show_options()


def show_child(name, child_key):
    cls()
    child_key = child_key.lstrip().lower()
    allow_keys = get_keys(getattr(options, name))
    print("=-" * 30)
    if child_key in allow_keys:
        worker = getattr(getattr(options, name), child_key)

        print(f"{name} - {child_key}")
        print(f" -> {worker}")
        if child_key == "value" and worker is not None:
            print("=-" * 30)
            while True:
                edit_ask = input("Edit this value? (yes/no) : ")
                edit_ask = edit_ask.lstrip().lower()
                if edit_ask == "yes":
                    edit_child(name, child_key)
                elif edit_ask == "no":
                    break
                else:
                    print("Please say 'yes' or 'no'")

        show_details(name)
    else:
        if child_key == "exit":
            print("Good Bye")
            sys.exit(0)
        elif child_key == "back":
            show_details(child_key)

        print("Wrong Key!")
        show_options()


def edit_child(name, child_key):
    cls()
    value_type = getattr(options, name).value_type
    old_value = getattr(options, name).value

    print("=-" * 30)
    print(f"Editing: {name}")
    print(f"Before Value: {old_value}")
    print("=-" * 30)

    new_value = input("New Value? : ")
    if not isinstance(new_value, value_type):
        print("Wrong Type...")
        show_child(name, child_key)

    update(name, old_value, new_value)
    save_option()


def update(name, old_value, new_value):
    cls()
    print("Finding...")
    for item in before:
        if item.lstrip().lower().startswith(name):
            address = before.index(item)
            print(f"Found! {address} line")
            print("Updating...")
            tmp = before[address].split(" ")[-1].replace("\n", '').replace('"', '')
            try:
                int(new_value)
                tmp = f'{name} = {tmp.replace(str(old_value), str(new_value))}\n'
            except ValueError:
                tmp = f'{name} = "{tmp.replace(str(old_value), str(new_value))}"\n'
            before[address] = tmp
            print("Updated!")


def save_option(reset=False):
    if reset is False:
        bk_time = time.strftime("%Y-%m-%d %HH %MM", time.localtime(time.time()))
        try:
            with open(f"./backup/option_{bk_time}.py", "w") as bk_f:
                bk_f.writelines(before)
        except FileNotFoundError:
            os.mkdir("./backup")
            with open(f"./backup/option_{bk_time}.py", "w") as bk_f:
                bk_f.writelines(before)
        with open(f"./backup/option_last_backup.py", "w") as bk_f:
            bk_f.writelines(before)

    with open("option.py", "w") as save_f:
        save_f.writelines(before)
    print("=-" * 30)
    print("Saved!")
    sys.exit(0)


if __name__ == "__main__":
    with open("option.py", "r") as be_f:
        before = be_f.readlines()

    try:
        if sys.argv[1].lstrip().lower() == "reset":
            print("reset option...")
            reset_options()
            sys.exit(0)
    except IndexError:
        pass

    show_options()
