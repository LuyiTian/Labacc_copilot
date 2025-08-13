from datetime import datetime
from pathlib import Path

from langchain_core.prompts import PromptTemplate


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

def read_file(file_path):
    """Read the content of a file and return it as a string."""
    # Get the directory where this file is located
    current_dir = Path(__file__).parent
    full_path = current_dir / file_path
    with open(full_path, encoding='utf-8') as file:
        return file.read()

query_writer_instructions = PromptTemplate.from_template(read_file("prompts/query_writer_instructions.md"), template_format="jinja2")
web_searcher_instructions = PromptTemplate.from_template(read_file("prompts/web_searcher_instructions.md"), template_format="jinja2")
reflection_instructions = PromptTemplate.from_template(read_file("prompts/reflection_instructions.md"), template_format="jinja2")
answer_instructions = PromptTemplate.from_template(read_file("prompts/answer_instructions.md"), template_format="jinja2")
