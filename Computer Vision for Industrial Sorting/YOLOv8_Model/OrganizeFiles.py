import os

def rename_files_in_folder(folder_path, prefix):
    # Get list of all files in the folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    # Sort the files to ensure consistent ordering
    files.sort()
    
    # Rename each file
    for index, filename in enumerate(files):
        # Get the file extension
        file_extension = os.path.splitext(filename)[1]
        # Generate the new file name
        new_name = f"{prefix}_{index + 1}{file_extension}"
        # Get full file paths
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_name)
        # Rename the file
        os.rename(src, dst)
        print(f"Renamed '{filename}' to '{new_name}'")

# Set the folder path and prefix
folder_path = 'D:/L I C E N T A/Simulare/Scripts/YOLOv8_Model_Detection/code/data/images/val' 
prefix = 'ImgForDatasetVal'

# Rename files
rename_files_in_folder(folder_path, prefix)