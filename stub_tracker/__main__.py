"""List all functions and methods missing a stub annotation.

This module acts is a script (and library, i guess) for showing which methods and functions
of a library still need to be stubbed

TODO:
    * better output formatting
    * unit testing
    * optionally output percentage of methods/functions covered
    * actually check the ast to make sure stubs are legit. currently it just checks existance
"""

import ast
import os
import sys
from typing import Dict, List, TextIO, Tuple

from . import VERSION

HELP_TEXT = """
stub-tracker {version} (c) proxi 2020, mit license

usage: stub_tracker <source_root> <stub_root> [--help]

required arguments:
    source_root: the directory containing the *.py source files to be stubbed
    stub_root:   the directory containing the *.pyi stub files

options:
    --help:      print this help text and exit
""".format(version=VERSION)


def find_missing_methods(
    src_classes: List[ast.ClassDef],
    stub_classes: List[ast.ClassDef],
    filename: str
) -> List[str]:
    """Diff the ClassDef asts, and return a list of the missing names.

    args:
        src_classes (List[ast.ClassDef]):  a list of ast ClassDef nodes for the python source
        stub_classes (List[ast.ClassDef]): a list of ast ClassDef nodes for the stub files

    returns:
        List[str]: a list of methods in src_classes that are not in stub_classes (not stubbed)
            the methods are formatted as {filename}:{class_name}.{method_name}
    """
    missing_methods: List[str] = []

    # dict mapping class_name -> [method_names]
    stub_class_method_names: Dict[str, List[str]] = {}
    for cls in stub_classes:
        method_list: List[str] = []
        for el in cls.body:
            if isinstance(el, ast.FunctionDef):
                method_list.append(el.name)
        stub_class_method_names[cls.name] = method_list

    for cls in src_classes:
        for el in cls.body:
            if not isinstance(el, ast.FunctionDef):
                continue
            if el.name not in stub_class_method_names.get(cls.name, []):
                missing_methods.append(f'{filename}:{cls.name}.{el.name}')

    return missing_methods


def find_all_missing(sources: Dict[str, Tuple[TextIO, TextIO]]) -> List[str]:
    """Find all methods and functions from `sources` that are missing stubs.

    args:
        sources (Dict[str, Tuple[TextIO, TextIO]]): mapping of a filename to a tuple.
            the first tuple element is a file-like object containing the python source,
            and the second tuple element is a file-like object containing the stub source.
            the sources are not closed anywhere in this function.
            if they need to be closed, you must close them manually.

    returns:
        List[str]: a list of strings representing the missing methods/functions in the form:
            'filename.py:ClassName.method_name' or 'filename.py:function_name'
    """
    not_found: List[str] = []
    for src_file, src_code in sources.items():
        source_tree = ast.parse(src_code[0].read())
        stub_tree = ast.parse(src_code[1].read())
        src_code[0].close()
        src_code[1].close()

        # grab classes from both
        src_classes = [cls for cls in source_tree.body if isinstance(cls, ast.ClassDef)]
        src_funcs = [cls for cls in source_tree.body if isinstance(cls, ast.FunctionDef)]
        stub_classes = [cls for cls in stub_tree.body if isinstance(cls, ast.ClassDef)]
        stub_funcs = [cls for cls in stub_tree.body if isinstance(cls, ast.FunctionDef)]

        # append the ones that don't exist
        not_found += find_missing_methods(src_classes, stub_classes, src_file)
        stub_func_names: List[str] = list(map(lambda x: x.name, stub_funcs))
        for func in src_funcs:
            if func.name not in stub_func_names:
                not_found.append(f'{src_file}:{func.name}')
    return not_found


def run(source_root: str, stub_root: str) -> List[str]:
    """Return all the missing methods/functions.

    Acts as the main entry point of the script, just returns the result instead of printing.

    args:
        source_root (str): the directory containing the *.py source files to be stubbed
        strub_root (str):  the directory containing the *.pyi stub files
    """
    source_ios: Dict[str, Tuple[TextIO, TextIO]] = {}
    # only gets stubs that have an associated source file
    # we don't care about stubs that are for non-existant source
    for dirpath, dirnames, filenames in os.walk(source_root):
        dirpath = os.sep.join(dirpath.split(os.sep)[1:])
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            if not fullpath.endswith('.py'):
                continue
            source_ios[fullpath] = (open(os.path.join(source_root, fullpath)),
                                    open(os.path.join(stub_root, fullpath + 'i')))

    return find_all_missing(source_ios)


if __name__ == '__main__':
    if '--help' in sys.argv or len(sys.argv) != 3:
        print(HELP_TEXT, file=sys.stderr)
        exit(1)

    not_found = run(sys.argv[1], sys.argv[2])

    for el in not_found:
        print(el)
