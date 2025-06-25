import os

def get_file_content(working_directory, file_path):
    try:
        # Calculate the full path to the file we actually want to examine
        full_file_path = os.path.join(working_directory, file_path)

        if not os.path.abspath(full_file_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(full_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        MAX_CHARS = 10000
        with open(full_file_path, 'r') as f:
            content = f.read(MAX_CHARS)
            if f.read(1) != '':
                return content + f"[...File \"{file_path}\" truncated at {MAX_CHARS} characters...]"
            return content

    except Exception as e:
        return f"Error: {str(e)}"
