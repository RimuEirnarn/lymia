from os import walk
from os.path import join

def catch():
    """catch some file"""
    known_files = []
    for root, _, files in walk('.'):
        for file in files:
            if file.endswith('.py'):
                known_files.append(join(root, file))
    return known_files

def readln(file: str):
    """Read lines in a file"""
    with open(file, encoding='utf-8') as f:
        return len(f.readlines())

def main():
    """main"""
    files = catch()
    total = 0
    for file in files:
        length = readln(file)
        total += length
        print(f"{file} -> has {length} lines")
    print(f"This project has {total} lines")

if __name__ == '__main__':
    main()
