import os
import shutil
import sys
# Not on python path on windows so can't import anything local
# assets_root.py
import os
import inspect
def noop():
    return
assets_root=os.path.dirname(inspect.getfile(noop))
# end assets_root.py
parent_assets_root=sys.argv[1]
parent_version=sys.argv[2]
print(f"Starting update from {parent_version} to {sys.argv[3]}")
def rm_allbut(path:str,save:list[str]):
    for item in os.listdir(path):
        if item not in save:
            full=os.path.join(path,item)
            if os.path.isdir(full):
                shutil.rmtree(full)
            else:
                os.remove(full)

def copytree_merge(src:str, dst:str, overwrite_files: bool = True):
    src_pth = os.path.abspath(src)
    dst_pth = os.path.abspath(dst)

    if not os.path.exists(src_pth):
        raise FileNotFoundError(f"Source directory does not exist: {src_pth}")

    if not os.path.isdir(src_pth):
        raise NotADirectoryError(f"Source is not a directory: {src_pth}")
    
    os.makedirs(dst_pth, exist_ok=True)

    for item in os.listdir(src_pth):
        src_item = os.path.join(src_pth, item)
        dst_item = os.path.join(dst_pth, item)

        if os.path.isdir(src_item):
            copytree_merge(src_item, dst_item)
        else:
            if not os.path.exists(dst_item) or overwrite_files:
                while True:
                    try:
                        shutil.copy2(src_item,dst_item)
                        break
                    except Exception as e:
                        print(dst_item)
                        print(e)
                    print("Retrying del")

rm_allbut(parent_assets_root,["python",".venv","update_temp"])
rm_allbut(os.path.dirname(parent_assets_root),["assets"])
copytree_merge(os.path.dirname(assets_root),os.path.dirname(parent_assets_root))
shutil.rmtree(assets_root)

# Pkgfix
import subprocess
import sys
import os

def compile_requirements(input_file='requirements.in', output_file='requirements.txt'):
    """Use pip-compile to generate a fully pinned requirements.txt"""
    print(f"Compiling {input_file} into {output_file}...")
    subprocess.check_call([sys.executable, "-m", "piptools", "compile", input_file, "-o", output_file])

def sync_requirements(output_file='requirements.txt'):
    """Use pip-sync to install exact packages and remove unneeded ones"""
    print(f"Syncing environment with {output_file}...")
    subprocess.check_call([sys.executable, "-m", "piptools", "sync", output_file])

def main():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pip-tools"])
    input_file = 'requirements.txt'
    output_file = 'requirements.pinned'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Create it with your unpinned dependencies.")
        sys.exit(1)

    compile_requirements(input_file, output_file)
    sync_requirements(output_file)
main()