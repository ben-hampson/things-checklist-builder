from pathlib import Path
from collections import OrderedDict
from pasteboard import shortcuts_attachments
import re
import sys
from pprint import pprint

def text_to_dict(text: str) -> OrderedDict:
    """Convert text to OrderedDict."""
    lines = text.split('\n')
    
    full_list = OrderedDict()
    section = ""

    for i, line in enumerate(lines):
        # Packing List Title
        if i == 0:  
            continue

        # Section Heading
        if re.search(r'^\t\S*:', line):
            section = line
            full_list[section] = OrderedDict()
            continue

        # Task
        if re.search(r'^\t\t- .*', line):
            task = line
            full_list[section][task] = []

        # Task Note / Sub-task
        if re.search(r'^\t\t\t.*', line):
            subtask_or_note = line
            full_list[section][task].append(subtask_or_note)

    return full_list

def dict_to_things_list(input_dict: OrderedDict, title: str="TITLE") -> str:
    """Convert the OrderedDict into a Markdown text list.
    
    input_dict: An OrderedDict of sections and tasks.
    title: The desired Things project name. No trailing colon needed.
    return: A text list ready for Things Parser in Drafts 5.
    """
    md = str(title) + ":\n"
    
    for section in input_dict:
        md += section + "\n"
        for task in input_dict[section]:
            md += task + "\n"
            for subtask_or_note in input_dict[section][task]:
                md += subtask_or_note + "\n"
    
    return md

if __name__ == '__main__':
    """Use the Pyto shortcut 'Run Script' and set the files as 'attachments'."""
    # Currently the 'Run Script' shortcut isn't passing the args through properly.
    # So if no title arg is found, replace with 'NO-TITLE'. Then replace that title
    # back in the Shortcut.
    try:
        title = sys.argv[1]
    except IndexError:
        title = "NO-TITLE"
    files = shortcuts_attachments()

    tasklist_dicts = []

    # Put 'base.txt' or 'base.md' first
    for i, f in enumerate(files):
        if re.search(r"base.(txt|md)", f.get_suggested_name(), re.IGNORECASE):
            if i == 0:
                break
            base_file = files.pop(i)
            files.insert(0, base_file)

    # Convert tasklists into OrderedDicts + put in a list
    for f in files:
        with open(f.get_file_path(), encoding='utf-8') as file_1:
            tasklist_text = file_1.read()
        tasklist_dict = text_to_dict(tasklist_text)
        tasklist_dicts.append(tasklist_dict)

    # Combine OrderedDicts
    base_dict = OrderedDict(OrderedDict())
    for i, supp_dict in enumerate(tasklist_dicts):
        if i == 0:
            base_dict = supp_dict
            continue
        
        # Append tasks to the relevant section in the base_dict
        for section in supp_dict:
            for task in supp_dict[section]:
                if re.search(r'^\t\t- .*', task):  # If a task, append it to section.
                    try:
                        base_dict[section][task] = supp_dict[section][task]  # Append task + its subtasks and notes
                    except KeyError:
                        base_dict[section] = OrderedDict()
                        base_dict[section][task] = supp_dict[section][task]  # Append task + its subtasks and notes

    output = dict_to_things_list(base_dict, title)
    print(output)
