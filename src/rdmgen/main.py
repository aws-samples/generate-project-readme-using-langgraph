import os.path
import tempfile
from random import randint

import typer
from git import Repo
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain_core.messages import HumanMessage

from .agent_components.graph import graph
from .constants import LANGGRAPH_RECURSION_LIMIT

cache = InMemoryCache()
cache.clear()
set_llm_cache(cache)

app = typer.Typer()


@app.command()
def generate(
    repo_path: str = typer.Argument(
        ...,
        help="Relative path of the local clone of the respository or the full GitHub URL to generate README.md file for.",
    ),
    output_path: str = typer.Option(
        None,
        "--out",
        help="Output directory for the readme file. If empty, README.md is written to the same directory.",
    ),
    write_graph_diagram: bool = typer.Option(
        False,
        "--diagram",
        help="Flag to write png image with graph diagram. Defaults to False",
    ),
):

    # base case
    # if local & no output path -> same directory
    target_dir = repo_path
    readme_output_path = repo_path
    output_dir_message = "Write the file to that same path."

    # if (remote | local) & output path -> ouput path
    if output_path:
        readme_output_path = output_path
        output_dir_message = f"Write the file to this directory: {readme_output_path}."

    message = {
        "messages": [
            HumanMessage(
                content=f"Generate a README.md for the files in this directory: '{target_dir}'. {output_dir_message}"
            )
        ]
    }

    if repo_path.startswith("https://github.com/") or repo_path.startswith(
        "git@github.com:"
    ):
        with tempfile.TemporaryDirectory() as temp_dir:

            Repo.clone_from(repo_path, temp_dir)
            target_dir = temp_dir

            # if remote & no output path -> current directory
            if not output_path:
                readme_output_path = os.path.abspath(".")
                output_dir_message = (
                    f"Write the file to this directory: {readme_output_path}."
                )

            message = {
                "messages": [
                    HumanMessage(
                        content=f"Generate a README.md for the files in this directory: '{target_dir}'. {output_dir_message}"
                    )
                ]
            }

            state = invoke_graph(message)

    else:
        state = invoke_graph(message)

    if write_graph_diagram:
        write_png_graph(readme_output_path)


def invoke_graph(message):
    state = graph.invoke(
        message,
        config={
            "recursion_limit": LANGGRAPH_RECURSION_LIMIT,
            "configurable": {
                "thread_id": randint(1, 9999),
            },
        },
    )

    return state


def write_png_graph(path, output_filename="graph_diagram.png"):
    os.makedirs(path, exist_ok=True)

    png_data = graph.get_graph(xray=True).draw_mermaid_png()
    
    png_filepath = os.path.join(path, output_filename)
    with open(png_filepath, "wb") as png:
        png.write(png_data)
    return True


if __name__ == "__main__":
    app()
