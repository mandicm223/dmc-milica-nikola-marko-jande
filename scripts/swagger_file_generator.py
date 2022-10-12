#!/usr/bin/env python
import json
import os
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError
from logger import log

load_dotenv()

region = os.getenv('AWS_REGION')

apigw = client('apigateway', region_name=region)
cf = client('cloudformation', region_name=region)
ecr = client('ecr', region_name=region)

environment = os.getenv('ENVIRONMENT')
app_name = os.getenv('APP_NAME')
api_version = os.getenv('API_VERSION')

prefix_name = f'{environment.lower()}-{app_name.lower()}'


def create_ecr_repo():
    """Creates ECR repository"""
    log.info(f'Checking is ECR repository with name swagger_ui already exist on AWS REGION {region}...')
    try:
        response = ecr.describe_repositories(repositoryNames=['swagger_ui'])
        for repo in response['repositories']:
            if repo['repositoryName'] == 'swagger_ui':
                log.info(f"ECR repository with name swagger_ui already created on AWS REGION {region}.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryNotFoundException':
            log.warning(f"ECR repository with name swagger_ui not found on AWS REGION {region}. Creating...")
            ecr.create_repository(repositoryName='swagger_ui')
            log.info(f"ECR repository with name swagger_ui created on AWS REGION {region}.")
        else:
            log.error(f"Error:{e}")
            raise SystemExit(1)


def get_api_id_from_stack_output():
    """Getting REST API id from stack output"""
    try:
        log.info(f'Getting Rest API ID from stack {prefix_name}-stack-backend output')
        response = cf.describe_stacks(
            StackName=f'{prefix_name}-stack-backend')
        for stack in response['Stacks']:
            for output in stack['Outputs']:
                if output['ExportName'] == f'{prefix_name}-api':
                    return output['OutputValue']
    except ClientError as e:
        log.error(f"Error:{e}")
        raise SystemExit(1)


def generate_swagger():
    """Customizing exported swagger definition"""
    rest_api_id = get_api_id_from_stack_output()
    log.info(f"Getting swagger export for RestAPI with Id: {rest_api_id}")
    try:
        response = apigw.get_export(
            restApiId=rest_api_id,
            stageName=environment.lower(),
            exportType='swagger')

        swagger = json.loads(response['body'].read())

        log.info(f"Generating the new swagger.json file")
        swagger['host'] = os.getenv('API_DOMAIN_NAME')
        swagger['info']['version'] = api_version.lower()
        swagger['basePath'] = swagger['basePath'] + f'/api/{api_version}'

        new_paths = dict()
        for key, value in swagger['paths'].items():
            new_key = key.split(api_version)[1]
            for k, v in value.items():
                parameters = value[k]['parameters']
                for p in parameters:
                    if p['name'] == 'x-apigw-api-id':
                        p['default'] = rest_api_id
            new_paths[new_key] = value

        swagger['paths'] = new_paths
        swagger.pop('x-amazon-apigateway-policy')
        swagger.pop('x-amazon-apigateway-endpoint-configuration')

        # Add example for on_project array field of POST,UPDATE project methods (none by default)
        for key, value in swagger['definitions']['ProjectCreate']['properties'].items():
            if key == "on_project":
                value['example'] = ["Jonh Doe", "Mike Lee"]
        for key, value in swagger['definitions']['ProjectUpdate']['properties'].items():
            if key == "on_project":
                value['example'] = ["Jonh Doe", "Mike Lee"]     
                   
        log.info("Saving the new swagger.json file in directory ~/docker")
        with open('docker/swagger.json', 'w') as f:
            json.dump(swagger, f, indent=4)

    except ClientError as e:
        log.error(f"Error:{e}")
        raise SystemExit(1)


if __name__ == '__main__':
    create_ecr_repo()
    generate_swagger()
