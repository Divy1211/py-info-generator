import json, regex, sys, os

# settings, BASE_DIR & OUT_DIR are absolute paths
IGNORED_DIRS = [".git", ".idea", "venv"]
IGNORED_FILES = []
BASE_DIR = "C:/Users/LENOVO PC/My Stuff/AoE/CS/AoE2SP/AoE2ScenarioParser/AoE2ScenarioParser"
OUT_DIR = "C:/Users/LENOVO PC/My Stuff/AoE/CS/AoE2SP/docs"


BASE_DIR = BASE_DIR.replace("/", "\\")
OUT_DIR = OUT_DIR.replace("/", "\\")

if not os.path.exists(BASE_DIR):
    raise NotADirectoryError(f"Directory: {BASE_DIR} not found, BASE_DIR must be a valid directory")

if not os.path.exists(OUT_DIR):
    raise NotADirectoryError(f"Directory: {OUT_DIR} not found, OUT_DIR must be a valid directory")

# regex for parsing.
_doc_string = r'(?:\s*"""(.*?)""")?'
_type_hint = r'(?::\s*([^\n]+?))?'
_open = r'(?:(?:\[\n)|(?:{\n))'
_close = r'(?:(?:\n\s*\])|(?:\n\s*\}))'
_list_or_dict = _open + r'.*' + _close
_indent = r'(?:\n\s{4})'
_inside_parenthesis = r'\((.*?)\)'
_return_type = r'(?:\s+->\s+(.*?))?:'

pattern_class_info = r'(\w+)' + r'(?:' + _inside_parenthesis + r')?:' + _doc_string
pattern_class_split = r'class\s+(?=\w+(?:\(.*?\))?:(?:\s*""".*?""")?)'
pattern_vars = r'(\w+)' + _type_hint + r'(?:\s*=\s*(' + _list_or_dict + r'|.*?))?'
pattern_class_attrs = _indent + pattern_vars + r'(?=\n)' + _doc_string
pattern_functions = r'(?:' + _indent + r'(@.+?))?' + _indent + r'def\s+(\w+)' + _inside_parenthesis + _return_type + _doc_string
pattern_attrs = r'(?<=\n\s*)(?:self.)' + r'(\w+)' + r'(?::\s*([^\n]+?))?' + r'(?:\s*=\s*(' + _list_or_dict + r'|.*))?' + r'\n' + _doc_string

pattern_loose_functions = r'(?<=\n)' + r'def\s+(\w+)' + _inside_parenthesis + _return_type + _doc_string
pattern_loose_vars = r'(?<=\n)' + pattern_vars + r'\n' + _doc_string

pattern_param_split = r'(?:(?<=\[(?:,|.)*?\]),|(?<=,[^\[\]]*),|(?<!(\[|\]).*),)'

def cprint(*args, colour = "white", **kwargs):
    _colour = {
        'end': '\033[0m',
        'black': '\033[30m',
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_black": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
    }

    string = _colour[colour]+' '.join(map(str, args))+_colour["end"]
    print(string, **kwargs)

def generate_file_info(path):

    cprint("🔃 Generating file info for file:", colour="bright_yellow", end=" ")
    cprint(f"{path}", colour="bright_blue", end="")
    sys.stdout.flush()

    file_info = {
        "filename": path.removeprefix(BASE_DIR+"\\"),
        "classes": {},
        "functions": {},
        "variables": {}
    }

    with open(path, encoding="utf-8") as file:
        code = file.read()

    # parse info about each class
    for _class in regex.split(pattern_class_split, code, flags=regex.DOTALL)[1:]:
        class_desc = {
            "name": "",
            "parents": [],
            "docstring": "",

            "class_attrs": {},
            "class_methods": {},

            "methods": {},
            "static_methods": {},

            "attrs": {},
            "properties": {},
            "setters": {},
            "deleters": {}
        }


        # parse general class info
        class_info = regex.match(pattern_class_info, _class, regex.DOTALL)
        class_desc["name"] = class_info.group(1)
        if class_info.group(2):
            class_desc["parents"] = list(map(lambda x: x.strip(), class_info.group(2).split(",")))
        if class_info.group(3):
            # class_desc["docstring"] = regex.sub(r'(?<=\n)\s{4}', ' ', class_info.group(3)).strip()
            class_desc["docstring"] = class_info.group(3).strip()


        # parse info about class attributes
        for class_attr in regex.finditer(pattern_class_attrs, _class, regex.DOTALL):
            class_desc["class_attrs"][class_attr.group(1)] = {
                "name": class_attr.group(1),
                "type": class_attr.group(2),
                "value": class_attr.group(3),
                "docstring": class_attr.group(4)
            }


        # parse info about functions
        function_type = {
            "@property": "properties",
            "@classmethod": "class_methods",
            "@staticmethod": "static_methods",
            "setter": "setters",
            "deleter": "deleters"
        }
        for function in regex.finditer(pattern_functions, _class, regex.DOTALL):
            ftype = function_type[function.group(1).split(".")[-1]] if function.group(1) else "methods"

            # parse info about function params
            params = {}
            proto = regex.split(pattern_param_split, function.group(3))
            for param in map(lambda x: x.strip(), filter(lambda x: x is not None, proto)):
                param_info = regex.match(pattern_vars, param, regex.DOTALL)
                if param_info:
                    params[param_info.group(1)] = {
                        "name": param_info.group(1),
                        "type": param_info.group(2),
                        "value": param_info.group(3)
                    }

            class_desc[ftype][function.group(2)] = {
                "name": function.group(2),
                "params": params,
                "return_type": function.group(4),
                "docstring": function.group(5) if function.group(5) else ""
            }


        # parse info about class instance attributes
        for attr in regex.finditer(pattern_attrs, _class):
            if attr.group(1) not in class_desc["attrs"]:
                class_desc["attrs"][attr.group(1)] = {
                    "name": attr.group(1),
                    "type": attr.group(2),
                    "value": attr.group(3),
                    "docstring": attr.group(4)
                }

        file_info["classes"][class_info.group(1)] = class_desc


    # parse info about variables outside a class in the file
    for var in regex.finditer(pattern_loose_vars, code):
        if var.group(1) not in file_info["variables"]:
            file_info["variables"][var.group(1)] = {
                "name": var.group(1),
                "type": var.group(2),
                "value": var.group(3),
                "docstring": var.group(4)
            }


    # parse info about functions outside a class in the file
    for function in regex.finditer(pattern_loose_functions, code):

        # parse info about function params
        params = {}
        proto = regex.split(pattern_param_split, function.group(2))
        for param in map(lambda x: x.strip(), filter(lambda x: x is not None, proto)):
            param_info = regex.match(pattern_vars, param, regex.DOTALL)
            if param_info:
                params[param_info.group(1)] = {
                    "name": param_info.group(1),
                    "type": param_info.group(2),
                    "value": param_info.group(3)
                }

        file_info["functions"][function.group(1)] = {
            "name": function.group(1),
            "params": params,
            "return_type": function.group(3),
            "docstring": function.group(4) if function.group(4) else ""
        }


    cprint("\r✔ Generated file info for file:", colour="bright_green", end=" ")
    cprint(f"{path}", colour="bright_blue")
    return file_info

def ignored(name):
    return any(map(lambda x: x in name, IGNORED_DIRS + IGNORED_FILES))

for root, dirs, files in os.walk(BASE_DIR):
    for file in files:
        if not ignored(root+"\\"+file) and file.endswith(".py"):
            inside_dir = root.removeprefix(BASE_DIR).removeprefix("\\")
            inside_dir = inside_dir.replace("\\", ".")+"." if inside_dir else inside_dir

            file_info = generate_file_info(root+"\\"+file)

            with open(OUT_DIR+"\\"+inside_dir+file+".json", "w") as to_file:
                json.dump(file_info, to_file, indent=4)
