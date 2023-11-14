import os
import shlex
import shutil
import subprocess
import sys


def _page(text: str):
    """
    Display text in a terminal pager.
    Respects the PAGER environment variable if set.

    :param text: Text to display.
    """
    pager_cmd = shlex.split(os.environ.get("PAGER") or "less -r")
    subprocess.run(pager_cmd, input=text.encode("utf-8"))


def autoprint(text: str):
    """
    Print text to stdout.
    If the text is longer than the terminal height, it will be piped to a pager.
    """
    if sys.stdout.isatty():
        nlines = len(text.splitlines())
        _, term_lines = shutil.get_terminal_size()
        if nlines > term_lines:
            return _page(text)

    print(text)
