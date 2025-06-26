import os
import subprocess

def run_python_file(working_directory, file_path):
    full_file_path = os.path.join(working_directory, file_path)
    try:
        if os.path.commonpath([os.path.abspath(full_file_path), os.path.abspath(working_directory)]) != os.path.abspath(working_directory):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.exists(full_file_path):
            return f'Error: File "{file_path}" not found.'
        
        if not full_file_path.endswith('.py'):
            return f'Error: File "{file_path}" is not a Python file.'
        
        result = subprocess.run(
            ['python3', file_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory
        )

        output = ""
        if result.stdout.strip():
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr.strip():
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"Process exited with code {result.returncode}"

        return output.strip() or "No output produced."

    except Exception as e:
        return f"Error: executing Python file: {e}"

