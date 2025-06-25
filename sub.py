import os
import shutil


def get_unique_destination(path):
    """Generate unique filename if destination exists"""
    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(path)
    counter = 1

    while True:
        new_path = f"{base} ({counter}){ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def main():
    # Get and clean directory path
    root = input("Enter the path to a directory: ").strip().strip('"')
    root = os.path.normpath(root)

    if not os.path.isdir(root):
        print(f"Error: Invalid directory path: {root}")
        return

    for dirpath, _, filenames in os.walk(root, topdown=False):
        if dirpath == root:
            continue

        for filename in filenames:
            source = os.path.join(dirpath, filename)
            dest = os.path.join(root, filename)

            try:
                # Handle paths with spaces by using raw string paths
                unique_dest = get_unique_destination(dest)
                shutil.move(source, unique_dest)
                print(f"Moved: '{source}' → '{unique_dest}'")
            except Exception as e:
                print(f"Error moving '{source}': {str(e)}")


if __name__ == "__main__":
    main()
