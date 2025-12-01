import boto3
import logging
from botocore.exceptions import ClientError

# Create a session that uses the OneLogin/CLI profile "dev"
# This assumes you've already done something like:
#   aws sso login --profile dev
session = boto3.Session(profile_name="dev")


def upload_file_to_s3(file_name, bucket_name):

    # You can also route S3 through the same session if desired:
    s3_client = session.client("s3")
    try:
        s3_key = file_name.replace("/tmp/", "output_report/")
        s3_client.upload_file(file_name, bucket_name, s3_key)
        logging.info("File uploaded to %s with key %s", bucket_name, file_name)
    except ClientError as error:
        logging.error(error)
        return False
    return True
def get_parameter_value(parameter_name, region_name, secure: False):
    # Use the session/profile "dev" for SSM
    ssm_client = session.client(service_name="ssm",
                                region_name=region_name)

    try:
        # Retrieve the parameter value from Parameter Store
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=secure,
        )
        parameter_value = response["Parameter"]["Value"]
        return parameter_value
    except ssm_client.exceptions.ParameterNotFound as error:
        logging.error(f"Parameter '{parameter_name}' not found.")
        raise error
    except Exception as exception:
        logging.error(
            f"Error occurred while getting parameter '{parameter_name}':\
                  {exception}"
        )
        raise exception
def get_secret_value(secret_name, region_name):
    # Use the same session/profile "dev" for Secrets Manager
    secret_client = session.client(service_name="secretsmanager",
                                   region_name=region_name)
    try:
        # Retrieve the secret
        get_secret_response = secret_client.get_secret_value(SecretId=secret_name)
        secret_value = get_secret_response["SecretString"]
        return secret_value
    except secret_client.exceptions.InvalidParameterException as error:
        logging.error(f"Parameter '{secret_value}' not found.")
        raise error
