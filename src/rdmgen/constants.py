# Amazon Bedrock read_timeout, helpful for large respositories (since large API calls to Bedrock are expected)
READ_TIMEOUT_BEDROCK = 1000

# Amazon Bedrock model to use
# documentation link as of the 6th of September 2024:
# https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html
MODEL_ID_BEDROCK = "anthropic.claude-3-sonnet-20240229-v1:0"

# Debugging mode in lang-graph -> verbose stdout
ENABLE_LANGGRAPH_DEBUG_MODE = False

# Increasing the recursion limit would help for large repositories (since more super-steps [graph iterations] are expected)
# More details: https://langchain-ai.github.io/langgraph/concepts/low_level/#recursion-limit
LANGGRAPH_RECURSION_LIMIT = 20
