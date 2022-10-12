from boto3 import resource
from botocore.exceptions import ClientError
from logger.logger import log
import os

dynamodb = resource('dynamodb', region_name=os.getenv('AWS_REGION'))
table = dynamodb.Table(os.environ.get('DATABASE'))


def update_project(event, context):
    if 'params' in event:
        project_id = {"project_id": f"{event['params']['path']['project_id']}"}   
        log.info(f'Changing DynamoDB record with project_id: {project_id}')
        try:
            update_expression= "SET"
            expression_attribute_names = {}
            expression_attribute_values= {}
            body = event['body']
            accepted_attributes= ["project_name", "description", "internal", "on_project"]
            
            for key, value in body.items():
                if key in accepted_attributes:
                    update_expression += f' #{key} = :{key},' 
                    expression_attribute_names[f'#{key}'] = key
                    expression_attribute_values[f':{key}'] = value
                else:
                    log.error(f'Error: non-existent attribute in UPDATE method body for {project_id}')
                    raise SystemExit(1)
                    
            log.info(f'Project with id {project_id} sucessfully updated.')
            
            # Remove comma at the end of expression         
            update_expression = update_expression[:-1]
            
            return table.update_item(Key=project_id,
                                     UpdateExpression=update_expression,
                                     ExpressionAttributeNames=expression_attribute_names,
                                     ExpressionAttributeValues=expression_attribute_values,
                                     ReturnValues="ALL_NEW"
                                     )

        except ClientError as e:
            log.error(f'Error: {e}')
            raise SystemExit(1)
