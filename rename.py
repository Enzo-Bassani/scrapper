import os


def rename_files(directory):
    """
    Renames all files ending with '.file' to end with '.html'
    in the given directory and its subdirectories.
    """
    eba = os.walk(directory)
    for root, dirs, files in eba:
        for file in files:
            if file.endswith('.file'):
                new_name = file[:-4] + 'html'
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)
                print(f"Renaming {old_path} to {new_path}")
                os.rename(old_path, new_path)


# Example usage
directory = '/home/enzo/scrapper/https:'
rename_files(directory)
