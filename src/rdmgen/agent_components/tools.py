import os

from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_core.tools import tool


@tool
def read_files_batch_tool(directory):
    """
    Read all files in a given directory.
    Args:
        directory (str): path to directory
    Returns:
        combined_contents (str): the combined contents of all files.
        Each file is wrapped between xml tags with their corresponding name.
    """
    combined_contents = ""

    for filename in os.listdir(directory):
        # if you have a specific usecase you can define the files you dont want to read.
        if filename.startswith(".") or (
            filename.lower() in ["pyproject.toml", "poetry.lock"]
        ):
            continue
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                contents = file.read()
                file_contents_wrapped = f"<{filename}>{contents}</{filename}>"
                combined_contents += file_contents_wrapped
    return combined_contents


@tool
def human_input_tool(ai_message) -> str:
    """
    Use this tool when you require human input of feedback from your actions or thoughts.
    Args:
        ai_message (str): the action or thought to which you require feedback.
    Returns:
        str: human input.
    """
    print("############## Human Feedback ###############")

    print("\nInsert your feedback. Press Enter + q to end.\n")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "q":
            break
        contents.append(line)

    print("\n############################################")

    return


#     return "\n".join(contents)


@tool
def breather(thought):
    """
    Useful when you are asked to think iteratively or step-by-step, allows you take a break between steps.

    Simple function you can use when you are asked to think iteratively.
    Can ONLY be used before an action of type: "Final Answer".
    Args:
        thought (str): "I will take a breather"
        returns (str): "Focus on your current step, you are extremely smart and you got this"
    """
    return "Focus on your current step, you are extremely smart and you got this"


# write_file = WriteFileTool().as_tool()

list_directory = FileManagementToolkit(selected_tools=["list_directory"]).get_tools()
read_file = FileManagementToolkit(selected_tools=["read_file"]).get_tools()
write_file = FileManagementToolkit(selected_tools=["write_file"]).get_tools()

# tools = [breather, human_input_tool, write_file, read_files_batch_tool]
tools = list_directory + read_file + write_file + [breather, read_files_batch_tool]
