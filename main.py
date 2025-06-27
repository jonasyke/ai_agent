import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    args = sys.argv[1:]
    verbose = "--verbose" in sys.argv
    user_prompt = " ".join(args)
    model_name = "gemini-2.0-flash-001"

    if verbose:
        args.remove("--verbose")

    if not args:
        print("Error: No user prompt provided.")
        sys.exit(1)


    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
""" 

  
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Retrieves the content of a specified file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to retrieve, relative to the working directory.",
                ),
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Executes a Python file and returns its output, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the Python file to execute, relative to the working directory.",
                ),
            },
        ),
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes content to a specified file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to write to, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content to write to the file.",
                ),
            },
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file,
        ]
    )

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]
    
    def call_function(function_call_part, verbose=False):
        function_name = function_call_part.name
        args = function_call_part.args

        if verbose:
            print(f"Calling function: {function_name}({args})")
        
        else:
           print(f" - Calling function: {function_name}") 

        function_map = {
            "get_files_info": get_files_info,
            "get_file_content": get_file_content,
            "run_python_file": run_python_file,
            "write_file": write_file,
        }

        if function_name not in function_map:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"},
                        
                    )
                ]
            )
        
        function_call = function_map[function_name]

        args["working_directory"] = "./calculator"

        function_result = function_call(**args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ]
        )

    attempts = 20
    while attempts >= 0:

        response = client.models.generate_content(
            model = model_name,
            contents = messages,
            config= types.GenerateContentConfig(tools=[available_functions], system_instruction=system_prompt),
        )
        for candidate in response.candidates:
            messages.append(candidate.content)

        if response.function_calls:
            for function_call in response.function_calls:
                # Instead of just printing, actually call the function
                function_call_result = call_function(function_call, verbose=verbose)
                messages.append(function_call_result)
                
                # Check if the result has the expected structure
                if not function_call_result.parts[0].function_response.response:
                    raise Exception("Function call failed to return proper response")
                
                # If verbose, print the result
                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")

        attempts -= 1
        if not response.function_calls:
            print(f"Final response:\n{response.text}")
            break

if __name__ == "__main__":
    main()