import boto3
from botocore.config import Config
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_aws import ChatBedrock

from ..agent_components.tools import tools
from ..constants import MODEL_ID_BEDROCK, READ_TIMEOUT_BEDROCK
from .callback_handler import RealTimeFileCallbackHandler

handler = RealTimeFileCallbackHandler("output.log")
config = Config(read_timeout=READ_TIMEOUT_BEDROCK)
bedrock_runtime = boto3.client(
    "bedrock-runtime", region_name="us-east-1", config=config
)

##### Define the model ############

llm = ChatBedrock(
    client=bedrock_runtime,
    model_id=MODEL_ID_BEDROCK,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    model_kwargs={
        "temperature": 0.0,
        "stop_sequences": ["\n\nHuman"],
        "max_tokens": 4096,
    },
)


llm = llm.bind_tools(tools)
