import os
import shutil

def get_unique_destination(path):
    """
    Generates a unique filename if the destination already exists.
    Example: file.txt → file (1).txt, file (2).txt, etc.
    """
    if not os.path.exists(path):
        return path
    
    base, extension = os.path.splitext(path)
    counter = 1
    
    while True:
        new_path = f"{base} ({counter}){extension}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def main():
    # Get directory path from user
    root = input("Enter the path to a directory: ").strip()
    root = os.path.normpath(root)  # Normalize path (fix slashes)
    
    # Validate directory exists
    if not os.path.isdir(root):
        print("Error: Invalid directory path")
        return
    
    # Walk through all subdirectories
    for dirpath, _, filenames in os.walk(root):
        # Skip the root directory itself
        if dirpath == root:
            continue
        
        # Process each file in subdirectories
        for filename in filenames:
            source_path = os.path.join(dirpath, filename)
            dest_path = os.path.join(root, filename)
            
            try:
                # Generate unique destination if needed
                unique_dest = get_unique_destination(dest_path)
                shutil.move(source_path, unique_dest)
                print(f"Moved: {source_path} → {unique_dest}")
            except Exception as e:
                print(f"Error moving {source_path}: {str(e)}")

if __name__ == "__main__":
    main()