import json
import re
import sys
from colorama import Fore

# This script takes in a go.mod file, parses it and
# stores writes it to a json file.

def read_go_mod(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None

    module_name_match = re.search(r'module\s+([^\s]+)', content)
    go_version_match = re.search(r'go\s+([^\s]+)', content)
    require_statements = re.findall(r'require\s+\(([\s\S]*?)\)', content)

    if module_name_match:
        module_name = module_name_match.group(1)
    else:
        module_name = None

    if go_version_match:
        go_version = go_version_match.group(1)
    else:
        go_version = None

    dependencies = {}
    if require_statements:
        # This will iterate through multiple require blocks in the go.mod file.

        for require_content in require_statements:
            dependency_lines = require_content.strip().split('\n')
            for line in dependency_lines:
                line = line.strip()
                if line and not line.startswith("//"):
                    parts = line.split()
                    if len(parts) >= 2:
                        dep_name = parts[0]
                        dep_version = parts[1]
                        dependencies[dep_name] = dep_version
    else:
        require_statements = re.findall(r'require\s+([^\s]+)\s+([^\s]+)', content)
        for statement in require_statements:
            dependencies[statement[0]] = statement[1]

    return {
        'module_name': module_name,
        'go_version': go_version,
        'dependencies': dependencies
    }


def main():
    file_path = sys.argv[1]
    module_info = read_go_mod(file_path)
    depfilename: str = sys.argv[2]
    depdict = {}
    try:
        with open(depfilename, 'r') as depfile:
            depcontent = depfile.read()
            depdict = json.loads(depcontent)
            depfile.close()

    except FileNotFoundError:
        print("deps.json not found... Creating...")
        depdict = {}

    if module_info:
        depdict[module_info['module_name']] = module_info['dependencies']
        with open(depfilename, 'w+') as depfile:
            json.dump(depdict, depfile, indent=4)
            depfile.close()

        print(Fore.WHITE + "Processing module:", Fore.GREEN + module_info['module_name'])

if __name__ == "__main__":
    main()
