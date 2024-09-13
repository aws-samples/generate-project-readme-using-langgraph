import os
from aws_cdk import Stack, aws_s3 as s3, aws_lambda as lambda_, aws_stepfunctions as sfn, aws_stepfunctions_tasks as tasks, aws_dynamodb as dynamodb, aws_sagemaker as sagemaker, aws_emr_serverless as emr_serverless
from constructs import Construct

class SensorExtractionStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stack_name: str,
        raw_bucket_name: str,
        intermediate_bucket_name: str,
        scene_metadata_table_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 buckets
        raw_bucket = s3.Bucket(
            self,
            "RawBucket",
            bucket_name=raw_bucket_name,
            removal_policy=self.removal_policy.DESTROY,
        )

        intermediate_bucket = s3.Bucket(
            self,
            "IntermediateBucket",
            bucket_name=intermediate_bucket_name,
            removal_policy=self.removal_policy.DESTROY,
        )

        # Create DynamoDB table
        scene_metadata_table = dynamodb.Table(
            self,
            "SceneMetadataTable",
            table_name=scene_metadata_table_name,
            partition_key=dynamodb.Attribute(
                name="scene_id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=self.removal_policy.DESTROY,
        )

        # Define Lambda functions
        extract_sensor_data_images_lambda = lambda_.Function(
            self,
            "ExtractSensorDataImagesLambda",
            code=lambda_.Code.from_asset("./scripts/extract_sensor_data_images.py"),
            handler="extract_sensor_data_images.handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={
                "RAW_BUCKET_NAME": raw_bucket.bucket_name,
                "INTERMEDIATE_BUCKET_NAME": intermediate_bucket.bucket_name,
            },
        )

        extract_sensor_data_parquet_lambda = lambda_.Function(
            self,
            "ExtractSensorDataParquetLambda",
            code=lambda_.Code.from_asset("./scripts/extract_sensor_data_parquet.py"),
            handler="extract_sensor_data_parquet.handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={
                "RAW_BUCKET_NAME": raw_bucket.bucket_name,
                "INTERMEDIATE_BUCKET_NAME": intermediate_bucket.bucket_name,
            },
        )

        # Grant Lambda permissions to access S3 buckets
        raw_bucket.grant_read(extract_sensor_data_images_lambda)
        raw_bucket.grant_read(extract_sensor_data_parquet_lambda)
        intermediate_bucket.grant_write(extract_sensor_data_images_lambda)
        intermediate_bucket.grant_write(extract_sensor_data_parquet_lambda)

        # Define SageMaker Processing Jobs
        object_detection_job = sagemaker.CfnProcessingJob(
            self,
            "ObjectDetectionJob",
            app_specification=sagemaker.CfnProcessingJob.AppSpecificationProperty(
                image_uri="yolov5-object-detection:latest",
                container_entrypoint=[
                    "python",
                    "object_detection.py",
                    "--input_bucket",
                    intermediate_bucket.bucket_name,
                    "--input_prefix",
                    "images/",
                    "--output_bucket",
                    intermediate_bucket.bucket_name,
                    "--output_prefix",
                    "object_detection/",
                ],
            ),
            role_arn="arn:aws:iam::123456789012:role/SageMakerRole",
            instance_count=1,
            instance_type="ml.m5.large",
            resource_config=sagemaker.CfnProcessingJob.ResourceConfigProperty(
                instance_count=1, instance_type="ml.m5.large"
            ),
        )

        lane_detection_job = sagemaker.CfnProcessingJob(
            self,
            "LaneDetectionJob",
            app_specification=sagemaker.CfnProcessingJob.AppSpecificationProperty(
                image_uri="yolov5-lane-detection:latest",
                container_entrypoint=[
                    "python",
                    "lane_detection.py",
                    "--input_bucket",
                    intermediate_bucket.bucket_name,
                    "--input_prefix",
                    "parquet/",
                    "--output_bucket",
                    intermediate_bucket.bucket_name,
                    "--output_prefix",
                    "lane_detection/",
                ],
            ),
            role_arn="arn:aws:iam::123456789012:role/SageMakerRole",
            instance_count=1,
            instance_type="ml.m5.large",
            resource_config=sagemaker.CfnProcessingJob.ResourceConfigProperty(
                instance_count=1, instance_type="ml.m5.large"
            ),
        )

        # Define EMR Serverless Job
        scene_detection_job = emr_serverless.CfnApplication(
            self,
            "SceneDetectionJob",
            release_label="emr-6.3.0",
            execution_role_arn="arn:aws:iam::123456789012:role/EMRServerlessRole",
            job_driver=emr_serverless.CfnApplication.JobDriverProperty(
                spark_submit_job_driver=emr_serverless.CfnApplication.SparkSubmitJobDriverProperty(
                    entry_point="s3://emr-serverless-scripts/scene_detection.py",
                    entry_point_arguments=[
                        "--input_bucket",
                        intermediate_bucket.bucket_name,
                        "--input_prefix",
                        "object_detection/,lane_detection/",
                        "--output_bucket",
                        intermediate_bucket.bucket_name,
                        "--output_prefix",
                        "scene_detection/",
                        "--metadata_table",
                        scene_metadata_table.table_name,
                    ],
                )
            ),
            maximum_timeout_minutes=60,
        )

        # Define Step Function
        extract_sensor_data_images_task = tasks.LambdaInvoke(
            self,
            "ExtractSensorDataImagesTask",
            lambda_function=extract_sensor_data_images_lambda,
            payload_response_only=True,
        )

        extract_sensor_data_parquet_task = tasks.LambdaInvoke(
            self,
            "ExtractSensorDataParquetTask",
            lambda_function=extract_sensor_data_parquet_lambda,
            payload_response_only=True,
        )

        object_detection_task = tasks.SageMakerProcessingJobTask(
            self,
            "ObjectDetectionTask",
            processing_job=object_detection_job,
            payload_response_only=True,
        )

        lane_detection_task = tasks.SageMakerProcessingJobTask(
            self,
            "LaneDetectionTask",
            processing_job=lane_detection_job,
            payload_response_only=True,
        )

        scene_detection_task = tasks.EmrServerlessTask(
            self,
            "SceneDetectionTask",
            application=scene_detection_job,
            payload_response_only=True,
        )

        step_function_definition = sfn.Chain.start(
            sfn.Parallel(
                extract_sensor_data_images_task,
                extract_sensor_data_parquet_task,
            )
        ).next(
            sfn.Parallel(
                object_detection_task,
                lane_detection_task,
            )
        ).next(
            scene_detection_task
        )

        step_function = sfn.StateMachine(
            self,
            "SensorExtractionStepFunction",
            definition=step_function_definition,
            state_machine_name=stack_name,
        )

        self.step_function_arn = step_function.state_machine_arn