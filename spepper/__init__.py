import builtins
import copy
import inspect
import io
import sys

import __main__
import pycodestyle


# override the pepper module, such that its functions cannot be used
sys.modules["spepper"] = "spepper"


def generate_pycodestyle_report(path: str) -> str:
    """
    Generates a pycodestyle report for the given path.

    Args:
        path : str
            The path to the file to generate a report for.

    Returns
        report : str
            The pycodestyle report.
            If there are no errors, this will be an empty string.
    """
    # Redirect stdout to a buffer
    stdout = sys.stdout
    sys.stdout = io.StringIO()

    style_guide = pycodestyle.StyleGuide()
    style_guide.check_files([path])

    # Capture the output from stdout
    report_output = sys.stdout.getvalue()

    # Restore stdout
    sys.stdout = stdout
    return report_output


def simulate_syntaxerror(path: str, line: str, desc: str) -> None:
    """
    Simulates a SyntaxError for the given path, line, and description.
    The SyntaxError will be printed to the console, but cannot be catched.

    Args:
        path : str
            The path to the file that contains the SyntaxError.

        line : int
            The line number of the SyntaxError.

        desc : str
            The description of the SyntaxError.

    Returns:
        None | Exit code 1
            This function will exit the program.
    """
    print(f'  File "{path}", line {line}')
    with open(path, "r") as f:
        lines = f.readlines()

        line = lines[line - 1].strip()
        print(f"   {line}\n")

    print(f"SyntaxError: {desc}")
    exit(1)


def pepper(path):
    """
    Raises a SyntaxError if the given path contains a pycodestyle issue.

    Args:
        path : str
            The path to the file to check for pycodestyle issues.

    Returns:
        None | Exit code 1
            If there is a pycodestyle issue, it will exit the program.
    """
    report = generate_pycodestyle_report(path)

    if report:
        report = report.split("\n")[0]
        line = int(report.split(":")[1])
        desc = report.split(":")[3].strip()

        simulate_syntaxerror(path, line, desc)


def pepper_module(module):
    """
    Raises a SyntaxError if the module's file contains a pycodestyle issue.
    Tries to ignore the python standard library.

    Args:
        module : module
            The module to check for pycodestyle issues.

    Returns:
        None | Exit code 1
            If there is a pycodestyle issue, it will exit the program.

    """
    try:
        path = inspect.getfile(module)

        # check for python standard library
        # "python" in the path might be a bit too general
        if "python" in path:
            return

        pepper(path)

    except TypeError:
        return


# check the main file
path = __main__.__file__
pepper(path)

# check all already imported modules
for k, v in sys.modules.items():
    if k == "pepper":
        continue

    pepper_module(v)


# capture the original __import__ function to avoid recursion
import_copy = copy.copy(builtins.__import__)


# custom __import__ function
def peppered_import(name, *args, **kwargs):
    """
    Is a version of the standard __import__ function,
    that checks the imported module for pycodestyle issues.

    Args:
        name : str
            The name of the module to import.

        *args : list
            The arguments for the standard __import__ function.

        **kwargs : dict
            The keyword arguments for the standard __import__ function.

    Returns:
        module : module
            The imported module.
    """
    module = import_copy(name, *args, **kwargs)
    pepper_module(module)
    return module


# override the __import__ function
builtins.__import__ = peppered_import
