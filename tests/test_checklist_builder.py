"""How do I get tests to work if the interpreter doesn't have the pasteboard module?"""

import sys
from unittest.mock import Mock
from collections import OrderedDict
sys.modules["pasteboard"] = Mock()
from things_list_merger.list_merger import text_to_dict
from pathlib import Path

def test_task_with_subtasks_and_notes():
    """A task with subtasks and notes should be handled right."""
    folder = Path(__file__).parent.joinpath("lists/")
    files = [folder.joinpath("base.txt")]

    for f in files:
        with open(f, encoding="utf-8") as file_1:
            input_text = file_1.read()

    result = text_to_dict(input_text)

    expected = OrderedDict(
        [
            (
                "\tPreparation:",
                OrderedDict(
                    [
                        ("\t\t- Download airline app", []),
                        ("\t\t- COVID checks", []),
                        ("\t\t- Gift for host", []),
                    ]
                ),
            ),
            (
                "\tSuitcase:",
                OrderedDict([("\t\t- Clothes", []), ("\t\t- Toiletries", [])]),
            ),
            ("\tBackpack:", OrderedDict([("\t\t- Passport", [])])),
        ]
    )

    assert result == expected
