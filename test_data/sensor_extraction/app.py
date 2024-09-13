import os
from aws_cdk import App, CfnOutput, Environment
from sensor_extraction.stack import SensorExtractionStack

SENSOR_EXTRACTION_STACK_NAME = os.environ.get("SENSOR_EXTRACTION_STACK_NAME")
RAW_BUCKET_NAME = os.environ.get("RAW_BUCKET_NAME")
INTERMEDIATE_BUCKET_NAME = os.environ.get("INTERMEDIATE_BUCKET_NAME")
SCENE_METADATA_TABLE_NAME = os.environ.get("SCENE_METADATA_TABLE_NAME")

app = App()

env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION"),
)

sensor_extraction_stack = SensorExtractionStack(
    app,
    "SensorExtractionStack",
    stack_name=SENSOR_EXTRACTION_STACK_NAME,
    raw_bucket_name=RAW_BUCKET_NAME,
    intermediate_bucket_name=INTERMEDIATE_BUCKET_NAME,
    scene_metadata_table_name=SCENE_METADATA_TABLE_NAME,
    env=env,
)

CfnOutput(
    scope=sensor_extraction_stack,
    id="StepFunctionArn",
    value=sensor_extraction_stack.step_function_arn,
    description="Step Function ARN",
)

app.synth()