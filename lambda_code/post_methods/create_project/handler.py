import os
from boto3 import resource
from botocore.exceptions import ClientError
from logger.logger import log
import uuid

dynamodb = resource('dynamodb', region_name=os.getenv('AWS_REGION'))
table = dynamodb.Table(os.environ.get('DATABASE'))


def create_project(event, context):
    try:
        project_id = str(uuid.uuid4())
        project_name = event['project_name']
        description = event['description']
        internal = event['internal']
        on_project = event['on_project']
        table.put_item(Item={"project_id": project_id, "project_name": project_name, "description": description,
                             "internal": internal, "on_project": on_project})

        response = {
            "outcome: ": "project successfully added",
            "project id: ": project_id,
            "project name: ": project_name,
            "description: ": description,
            "internal:": internal,
            "on_project: ": on_project
        }
        log.info(
            f'Project with id {project_id} successfully created. Project name: {project_name}. On project: {on_project}')
        return response
    except ClientError as e:
        log.error(f'Error:{e}')
        raise SystemExit(1)
