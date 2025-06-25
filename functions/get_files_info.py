import os

def get_files_info(working_directory, directory=None):
    try:
        if directory is None:
            directory = '.'
        
        # Calculate the full path to the directory we actually want to examine
        full_target_directory_path = os.path.join(working_directory, directory)

        # Check if the full path is a valid directory
        if not os.path.isdir(full_target_directory_path):
            return f'Error: "{directory}" is not a directory'
        
        # Security check using the full path
        if not os.path.abspath(full_target_directory_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
        contents = ""
        for file in os.listdir(full_target_directory_path):
            full_path = os.path.join(full_target_directory_path, file)
            file_size = os.path.getsize(full_path)
            is_dir = os.path.isdir(full_path)
            contents += f"- {file}: file_size={file_size} bytes, is_dir={is_dir}\n"

        return contents
        
    except Exception as e:
        return f"Error: {str(e)}"
