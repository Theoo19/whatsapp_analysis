from os import listdir
from constants import Directory


def get_int_input(min_value, max_value, message="> "):
    while True:
        n = input(message)
        if n.isnumeric():
            n = int(n)
            if min_value <= n <= max_value:
                return n
            print(f"Please enter a number between {min_value} and {max_value}")
        else:
            print("Please enter a number.")


def get_choice_from_list(choices, message):
    print(message)
    for i, choice in enumerate(choices):
        print(f"[{i}] - {choices}")
    index = get_int_input(0, len(choices) - 1)
    return choices[index]


def get_chat_filename():
    files = list(file for file in listdir(Directory.folder_chats) if file.endswith(".txt"))
    return get_choice_from_list(files, "Choose one of the chat files by its index:")
