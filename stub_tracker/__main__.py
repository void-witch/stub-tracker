"""List all functions and methods missing a stub annotation."""

import ast
import os
import sys
from typing import Any, Dict, List, Tuple


def _eprint(*s: Any) -> None: print(*s, file=sys.stderr)  # noqa


def _get_file(filename: str) -> str:
    try:
        with open(filename) as f:
            return f.read()
    except FileNotFoundError:
        return ''


def _get_methods(
    src_classes: List[ast.ClassDef],
    stub_classes: List[ast.ClassDef],
    filename: str
) -> List[str]:
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


# read sources
# read stubs
# combine into dict (filename -> tuple(src_code, src_stub))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        _eprint('please specify source root and stub root')
        exit(1)
    source_root = sys.argv[1]
    stub_root = sys.argv[2]
    sources: Dict[str, Tuple[str, str]] = {}
    # only gets stubs that have an associated source file
    # we don't care about stubs that are for non-existant source
    for dirpath, dirnames, filenames in os.walk(source_root):
        dirpath = os.sep.join(dirpath.split(os.sep)[1:])
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            if not fullpath.endswith('.py'):
                continue
            with open(os.path.join(source_root, fullpath)) as source:
                sources[fullpath] = (source.read(),
                                     _get_file(os.path.join(stub_root, fullpath + 'i')))

    not_found: List[str] = []
    for src_file, src_code in sources.items():
        print(src_code)
        source_tree = ast.parse(src_code[0])
        stub_tree = ast.parse(src_code[1])

        # grab classes from both
        src_classes = [cls for cls in source_tree.body if isinstance(cls, ast.ClassDef)]
        src_funcs = [cls for cls in source_tree.body if isinstance(cls, ast.FunctionDef)]
        stub_classes = [cls for cls in stub_tree.body if isinstance(cls, ast.ClassDef)]
        stub_funcs = [cls for cls in stub_tree.body if isinstance(cls, ast.FunctionDef)]

        # append the ones that don't exist
        not_found += _get_methods(src_classes, stub_classes, src_file)
        stub_func_names: List[str] = list(map(lambda x: x.name, stub_funcs))
        for func in src_funcs:
            if func.name not in stub_func_names:
                not_found.append(f'{src_file}:{func.name}')

    for el in not_found:
        print(el)
