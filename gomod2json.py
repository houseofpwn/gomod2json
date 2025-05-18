import json
import re
import sys


def read_go_mod(file_path):
    """
    Reads a go.mod file and extracts module information.

    Args:
        file_path (str): The path to the go.mod file.

    Returns:
        dict: A dictionary containing module information, or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()

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
            for require_content in require_statements:
                #require_content = require_statements[0]
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

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
    file_path = sys.argv[1]
    module_info = read_go_mod(file_path)
    depfilename = "deps.json"
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
            json.dump(depdict, depfile)
            depfile.close()


        print("Module Name:", module_info['module_name'])
        print("Go Version:", module_info['go_version'])
        print("Dependencies:")
        for name, version in module_info['dependencies'].items():
            print(f"  {name}: {version}")




if __name__ == "__main__":
    main()
