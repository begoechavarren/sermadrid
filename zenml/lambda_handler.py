import json
import logging
import os
import sys

# Setup basic logging immediately
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Log initial startup information
logger.info("=== Lambda Handler Starting ===")
logger.info(f"Python Version: {sys.version}")
logger.info(f"Current Directory: {os.getcwd()}")
logger.info(f"Directory Contents: {os.listdir()}")
logger.info(f"PYTHONPATH: {sys.path}")
logger.info(f"Environment Variables: {dict(os.environ)}")


def init_zenml():
    """Initialize ZenML configuration"""
    try:
        logger.info("Attempting to import ZenML...")
        from zenml.client import Client

        logger.info("ZenML import successful")

        logger.info("Initializing ZenML client...")
        client = Client()

        # Get stack name from environment variable
        stack_name = os.getenv("ZENML_STACK_NAME", "sermadrid")
        logger.info(f"Looking for stack: {stack_name}")

        try:
            stack = client.get_stack(stack_name)
            logger.info(f"Found stack: {stack.name}")

            logger.info("Activating stack...")
            client.activate_stack(stack.name)
            logger.info(f"Successfully activated stack: {stack.name}")
        except Exception as stack_error:
            logger.error(
                f"Failed to get/activate stack '{stack_name}': {str(stack_error)}"
            )
            raise

        # Verify active stack
        active_stack = client.active_stack
        if not active_stack:
            logger.error("No active ZenML stack found")
            raise RuntimeError("No active ZenML stack found")

        logger.info(f"Using ZenML stack: {active_stack.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize ZenML: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        logger.info("=== Handler Function Called ===")
        logger.info(f"Event: {json.dumps(event)}")

        # Initialize ZenML
        init_zenml()

        # Only import pipeline after ZenML is initialized
        logger.info("Importing feature engineering pipeline...")
        from pipelines.feature_engineering import feature_engineering

        logger.info("Starting pipeline execution...")
        pipeline = feature_engineering()
        pipeline_run = pipeline.run()

        logger.info("Pipeline execution completed successfully")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Success", "pipelineRunId": str(pipeline_run.id)}
            ),
        }

    except Exception as e:
        logger.error(f"Error in handler: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
