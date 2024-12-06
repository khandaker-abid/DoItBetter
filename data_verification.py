import os
import platform
import subprocess

# Creates a wrapper class of a directory: contains its path and size
class Item:
    def __init__(self, size, path):
        self.size = size
        self.path = path

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.size == other.size and self.path == other.path
        return False

    def __hash__(self):
        return hash((self.size, self.path))

    def __lt__(self, other):
        return self.path < other.path

# gets all the directories and wraps them into an Item instance. Returns the set of these Item instances (directories)
def get_dir_objects(directory):
    dirs = set()
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            size = get_size(item_path)
            if size is None:
                size = 0  # Assign a default size of 0 if the size cannot be determined
            dirs.add(Item(path=item_path, size=size))
    return dirs

# Gets the size of a given directory in bytes
def get_size(directory):
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output(['powershell', '-Command', f"(Get-ChildItem -Recurse '{directory}' | Measure-Object -Property Length -Sum).Sum"], stderr=subprocess.DEVNULL)
            b = int(result.strip())
            return b
        except subprocess.CalledProcessError:
            return None
    if platform.system() == "Darwin":
        try:
            result = subprocess.check_output(['du', '-sb', directory], stderr=subprocess.DEVNULL)
            b = int(result.split()[0].strip())
            return b
        except subprocess.CalledProcessError:
            return None
    return None

# main method, needs to be modulized or whatever. basically gets 2 input dirs,
# and if a dir is in one and not the other
# it puts it in set of mismatched dirs, increments a mismatch counter
# and gets the difference in bytes. At the end, it prints the mismatched set if its non empty
def main():
    path1 = input("INPUT DIR1: ")
    path2 = input("INPUT DIR2: ")
    dirs1 = get_dir_objects(path1)
    dirs2 = get_dir_objects(path2)

    # Filter out any Items with size == None and sort by size
    dirs1_list = sorted([d for d in dirs1 if d.size is not None], key=lambda x: x.size)
    dirs2_list = sorted([d for d in dirs2 if d.size is not None], key=lambda x: x.size)

    # contains a bug i think: the code will show all mismatches after one mismatch because the order of the
    # arrays will be altered
    mismatch_set = set()
    mismatch_count = 0
    mismatch_bytes = 0
    for file1, file2 in zip(dirs1_list, dirs2_list):
        if not file1 == file2:
            mismatch_count += 1
            mismatch_set.add(file1)
            mismatch_bytes += abs(file2.size - file1.size)

    if mismatch_count != 0:
        print("MISSING FILES: ")
        for file in mismatch_set:
            print(file.path)
        print("Total files missing and bytes: ", mismatch_count, mismatch_bytes)
    else:
        print("All subdirectories have the same size and no errors have been found!")
        for dir1, dir2 in zip(dirs1_list, dirs2_list):
            print(dir1.path)
            print(dir2.path)
 
if __name__ == "__main__":
    main()

