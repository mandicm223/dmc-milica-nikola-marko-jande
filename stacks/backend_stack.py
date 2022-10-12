from dotenv import load_dotenv
import os
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_ec2 as ec2,
    aws_apigateway as apigw,
    RemovalPolicy, Stack)
from base_constructs.functions import LambdaIntegation
from base_constructs.api import RestAPI
from base_constructs.function_layer import LambdaLayer

from constructs import Construct

load_dotenv()

environment = os.getenv('ENVIRONMENT')
app_name = os.getenv('APP_NAME')


class CdkBackend(Stack):
    def __init__(self, scope: Construct, construct_id: str, endpoint_id=ec2.InterfaceVpcEndpoint, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        prefix_name = f'{environment.lower()}-{app_name.lower()}'

        if 'API_DESCRIPTION' in os.environ:
            self.backed_api = RestAPI(self, "BackedRESTAPI", api_name=f'{prefix_name}-api',
                                      api_endpoint_id=endpoint_id, description=os.getenv('API_DESCRIPTION'))
        if 'API_DESCRIPTION' not in os.environ:
            self.backed_api = RestAPI(self, "BackedRESTAPI", api_name=f'{prefix_name}-api',
                                      api_endpoint_id=endpoint_id)

        # Define your DynamoDB database ==> Example ==>
        self.db_table = dynamodb.Table(self, 'BackedDynamoDBExample', table_name=f'{prefix_name}-dynamodb',
                                       point_in_time_recovery=True,
                                       removal_policy=RemovalPolicy.DESTROY,
                                       partition_key=dynamodb.Attribute(
                                           name='project_id',
                                           type=dynamodb.AttributeType.STRING
                                       ))

        # Add a layer(custom dependency) for your Lambda functions ==> Example ==>
        self.fn_sample_layer = LambdaLayer(self, "BackendLambdaLayer",
                                           layer_name=f'{prefix_name}-lambda-layer',
                                           source_dir='./lambda_layer',
                                           runtime='python3.9',
                                           description='Backed API Lambda Layer')

        # Define lambda functions that will process your API requests and return responses ==> Example ==>
        self.fn_sample_create_project = LambdaIntegation(self, "PostMethodsExample",
                                                         func_name=f'{prefix_name}-create-project',
                                                         description='Create a new project',
                                                         source_dir='lambda_code/post_methods/create_project',
                                                         layers=[self.fn_sample_layer.lambda_layer],
                                                         handler='handler.create_project',
                                                         runtime='python3.9',
                                                         func_environment={
                                                             'DATABASE': self.db_table.table_name
                                                         })
        self.db_table.grant_read_write_data(self.fn_sample_create_project.function)

        self.fn_sample_get_project = LambdaIntegation(self, 'GetMethodsExample',
                                                      func_name=f'{prefix_name}-list-project',
                                                      description='List all projects or by project_id',
                                                      source_dir='lambda_code/get_methods/get_project',
                                                      layers=[self.fn_sample_layer.lambda_layer],
                                                      handler='handler.get_project',
                                                      runtime="python3.9",
                                                      func_environment={
                                                          'DATABASE': self.db_table.table_name
                                                      })
        self.db_table.grant_read_data(self.fn_sample_get_project.function)

        self.fn_sample_update_project = LambdaIntegation(self, 'PutMethodsExample',
                                                         func_name=f'{prefix_name}-update-project',
                                                         description='Change project with the specified project_id',
                                                         source_dir='lambda_code/put_methods/update_project',
                                                         layers=[self.fn_sample_layer.lambda_layer],
                                                         handler='handler.update_project',
                                                         runtime="python3.9",
                                                         func_environment={
                                                             'DATABASE': self.db_table.table_name
                                                         })
        self.db_table.grant_read_write_data(self.fn_sample_update_project.function)

        self.fn_sample_delete_project = LambdaIntegation(self, 'DeleteMethodsExample',
                                                         func_name=f'{prefix_name}-delete-project',
                                                         description='Delete project with a certain project_id',
                                                         source_dir='lambda_code/delete_methods/delete_project',
                                                         layers=[self.fn_sample_layer.lambda_layer],
                                                         handler='handler.delete_project',
                                                         runtime="python3.9",
                                                         func_environment={
                                                             'DATABASE': self.db_table.table_name
                                                         })
        self.db_table.grant_read_write_data(self.fn_sample_delete_project.function)

        # Add resources that will be used to access your API methods ==> Example ==> 
        self.projects = self.backed_api.version.add_resource('projects')
        self.project_id = self.projects.add_resource("{project_id}")

        # Map your request body parameters and path parameters using the Velocity Template language ==> Example ==> 

        parameter_mapping = "#set($allParams = $input.params())\n" \
                            "{\n\"body\":$input.json('$'),\n" \
                            "\"params\":{\n" \
                            "#foreach($type in $allParams.keySet())\n" \
                            "#set($params = $allParams.get($type))\n" \
                            "\"$type\":{\n" \
                            "#foreach($paramName in $params.keySet())\n" \
                            "\"$paramName\":\"$util.escapeJavaScript($params.get($paramName))\"\n" \
                            "#if($foreach.hasNext),#end\n" \
                            "#end\n" \
                            "}\n" \
                            "#if($foreach.hasNext),#end\n" \
                            "#end\n}\n}"

        # Make models that describe your request body. Assigned to a particular method's 'request models' property ==> Example ==>
        update_project_api_model = self.backed_api.rest_api.add_model("ProjectUpdateModel",
                                                                      content_type='application/json',
                                                                      model_name="ProjectUpdate",
                                                                      schema=apigw.JsonSchema(
                                                                          schema=apigw.JsonSchemaVersion.DRAFT4,
                                                                          type=apigw.JsonSchemaType.OBJECT,
                                                                          properties={
                                                                              "project_name": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.STRING),
                                                                              "description": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.STRING),
                                                                              "internal": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.BOOLEAN),
                                                                              "on_project": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.ARRAY)
                                                                              },
                                                                          required=[""]
                                                                      ))   
        
        create_project_api_model = self.backed_api.rest_api.add_model("ProjectPostModel",
                                                                      content_type='application/json',
                                                                      model_name="ProjectCreate",
                                                                      schema=apigw.JsonSchema(
                                                                          schema=apigw.JsonSchemaVersion.DRAFT4,
                                                                          type=apigw.JsonSchemaType.OBJECT,
                                                                          properties={
                                                                              "project_name": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.STRING),
                                                                              "description": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.STRING),
                                                                              "internal": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.BOOLEAN),
                                                                              "on_project": apigw.JsonSchema(
                                                                                  type=apigw.JsonSchemaType.ARRAY)
                                                                          },
                                                                          required=["project_name", "description",
                                                                                    'internal', 'on_project']
                                                                      ))

        # Define  HTTP method/integration requests and responses for your methods  ==> Example ==>
        # Gets a project that has a project_id specified in a path parameter
        self.project_id.add_method(http_method='GET',
                                   integration=apigw.LambdaIntegration(handler=self.fn_sample_get_project.function,
                                                                       proxy=False,
                                                                       integration_responses=[apigw.IntegrationResponse(
                                                                           status_code='200')],
                                                                       request_parameters={
                                                                           "integration.request.header.x-apigw-api-id": "method.request.header.x-apigw-api-id",
                                                                           "integration.request.path.project_id": "method.request.path.project_id"
                                                                       },
                                                                       passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
                                                                       request_templates={
                                                                           "application/json": parameter_mapping}
                                                                       ),
                                   request_parameters={"method.request.header.x-apigw-api-id": True,
                                                       "method.request.path.project_id": True},
                                   method_responses=[apigw.MethodResponse(status_code='200')])

        # Lists all projects within the database
        self.projects.add_method(http_method='GET',
                                 integration=apigw.LambdaIntegration(handler=self.fn_sample_get_project.function,
                                                                     proxy=False,
                                                                     integration_responses=[apigw.IntegrationResponse(
                                                                         status_code='200')],
                                                                     request_parameters={
                                                                         "integration.request.header.x-apigw-api-id": "method.request.header.x-apigw-api-id"
                                                                     }),
                                 request_parameters={"method.request.header.x-apigw-api-id": True},
                                 method_responses=[apigw.MethodResponse(status_code='200')])

        # Modifies database entry that has a project_id specified in the path parameter, and modifications specified in the request body
        self.project_id.add_method(http_method='PUT',
                                   integration=apigw.LambdaIntegration(handler=self.fn_sample_update_project.function,
                                                                       proxy=False,
                                                                       integration_responses=[apigw.IntegrationResponse(
                                                                           status_code='200')],
                                                                       request_parameters={
                                                                           "integration.request.header.x-apigw-api-id": "method.request.header.x-apigw-api-id",
                                                                       },
                                                                       passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
                                                                       request_templates={
                                                                           "application/json": parameter_mapping}),
                                   request_parameters={"method.request.header.x-apigw-api-id": True, },
                                   request_models={
                                       "application/json": update_project_api_model
                                   },
                                   method_responses=[apigw.MethodResponse(status_code='200')])

        # Deletes a database entry that has the project_id specified in the path parameter
        self.project_id.add_method(http_method='DELETE',
                                   integration=apigw.LambdaIntegration(handler=self.fn_sample_delete_project.function,
                                                                       proxy=False,
                                                                       integration_responses=[apigw.IntegrationResponse(
                                                                           status_code='200')],
                                                                       request_parameters={
                                                                           "integration.request.header.x-apigw-api-id": "method.request.header.x-apigw-api-id",
                                                                           "integration.request.path.project_id": "method.request.path.project_id"
                                                                       },
                                                                       passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
                                                                       request_templates={
                                                                           "application/json": parameter_mapping}),
                                   request_parameters={"method.request.header.x-apigw-api-id": True,
                                                       "method.request.path.project_id": True},
                                   method_responses=[apigw.MethodResponse(status_code='200')])

        self.project_create = self.projects.add_resource("create")

        # Creates a new project with an automatically assigned project_id and other attributes specified in the request body
        self.project_create.add_method(http_method='POST',
                                       integration=apigw.LambdaIntegration(
                                           handler=self.fn_sample_create_project.function,
                                           proxy=False,
                                           integration_responses=[apigw.IntegrationResponse(
                                               status_code='200')],
                                           request_parameters={
                                               "integration.request.header.x-apigw-api-id": "method.request.header.x-apigw-api-id"
                                           }),
                                       request_parameters={"method.request.header.x-apigw-api-id": True},
                                       request_models={
                                           "application/json": create_project_api_model
                                       },
                                       method_responses=[apigw.MethodResponse(status_code='200')])
