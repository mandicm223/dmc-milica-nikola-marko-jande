from boto3 import resource
from botocore.exceptions import ClientError
from logger.logger import log
import os

dynamodb = resource('dynamodb', region_name=os.getenv('AWS_REGION'))
table = dynamodb.Table(os.environ.get('DATABASE'))


def delete_project(event, context):
    if 'params' in event:
        project_id = event['params']['path']['project_id']
        log.info(f'Deleting record from DynamoDB, project_id: {project_id}')
        try:
            table.delete_item(Key={'project_id': project_id})
            response_string = f"Successfully deleted project with project_id: {project_id}"
            response = {
                "outcome:": response_string
            }
            log.info(f"Successfully deleted project with project_id: {project_id}")
            return response
        except ClientError as e:
            log.error(f'Error: {e}')
            raise SystemExit(1)
