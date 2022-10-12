from boto3 import resource
from botocore.exceptions import ClientError
from logger.logger import log
import os

dynamodb = resource('dynamodb', region_name=os.getenv('AWS_REGION'))
table = dynamodb.Table(os.environ.get('DATABASE'))


def get_project(event, context):
    if 'params' in event:
        project_id = event['params']['path']['project_id']
        log.info(f'Grabbing item from DynamoDB for project_id: {project_id}')
        try:
            response = table.get_item(Key={'project_id': project_id})
            if response['Item']:
                log.info(f"Successfully retrieved project with project_id: {project_id}")
                return response['Item']
            else:
                log.error(f'There are no items for project_id: {project_id} in DynamoDB')
                return {'message': f'There are no items for project_id: {project_id} in DynamoDB'}
        except ClientError as e:
            log.error(f'Error: {e}')
            raise SystemExit(1)
    else:
        log.info('Grabbing all items from DynamoDB')
        try:
            response = table.scan(Select='ALL_ATTRIBUTES', ReturnConsumedCapacity='INDEXES', ConsistentRead=True)
            log.info('All items from DynamoDB successfully retrieved')
            return {'Projects': response['Items']}
        except ClientError as e:
            log.error(f'Error: {e}')
            raise SystemExit(1)
