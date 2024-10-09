import os
import shutil

def delete_empty_text_files(directory):
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Check if the file is a text file and if it is empty
        if os.path.isfile(file_path) and filename.endswith('.txt'):
            if os.path.getsize(file_path) == 0:
                print(f"Deleting empty file: {file_path}")
                os.remove(file_path)
def list_files_in_directory(directory):
    # Create an empty list to store the base file names without extensions
    base_file_list = []
    
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Check if the file path is a file (not a directory)
        if os.path.isfile(file_path):
            # Extract the base file name without the extension and append it to the list
            base_name = os.path.splitext(filename)[0]
            base_file_list.append(base_name)
    
    return base_file_list
def move_matched_files(source_directory, target_directory, destination_directory):
    # Get the list of base file names in the source directory
    source_files = list_files_in_directory(source_directory)
    
    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    # Iterate over all files in the target directory
    for filename in os.listdir(target_directory):
        # Construct the full file path
        file_path = os.path.join(target_directory, filename)
        # Extract the base file name without the extension
        base_name = os.path.splitext(filename)[0]
        # Check if the file path is a file (not a directory) and if the base file name is in the source files
        if os.path.isfile(file_path) and base_name in source_files:
            # Move the file to the destination directory
            shutil.move(file_path, os.path.join(destination_directory, filename))
            print(f"Moved: {file_path} to {os.path.join(destination_directory, filename)}")

# Specify the directory to check for empty text files
txt_directory = 'D:/L I C E N T A/Simulare/Training images/LabelsBaterii/obj_train_data/PozeBaterii'
img_directory = 'D:/L I C E N T A/Simulare/Training images/PozeBaterii'
dest_directory = 'D:/L I C E N T A/Simulare/Training images/Saved'

# Call the function to delete empty text files
move_matched_files(txt_directory, img_directory, dest_directory)