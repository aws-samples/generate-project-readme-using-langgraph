from langchain.prompts import PromptTemplate


def get_dir_prompt_template(parser) -> PromptTemplate:

    return PromptTemplate(
        template="""You are an intelligent AI assistant. Your task is to correctly provide the directory path in <dir></dir> tags that the human has asked you to read.
        Here is the question: 
        <ques>
        {ques}
        </ques>
        {format_instructions}
        """,
        input_variables=["ques"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )


def get_assessment_prompt_template(request) -> PromptTemplate:
    return PromptTemplate(template=request)
