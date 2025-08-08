from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

def read_file(file_path):
    """Read the content of a file and return it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

query_writer_instructions = PromptTemplate.from_template(read_file("deep_research/prompts/query_writer_instructions.md"), template_format="jinja2")
web_searcher_instructions = PromptTemplate.from_template(read_file("deep_research/prompts/web_searcher_instructions.md"), template_format="jinja2")
reflection_instructions = PromptTemplate.from_template(read_file("deep_research/prompts/reflection_instructions.md"), template_format="jinja2")
answer_instructions = PromptTemplate.from_template(read_file("deep_research/prompts/answer_instructions.md"), template_format="jinja2")
