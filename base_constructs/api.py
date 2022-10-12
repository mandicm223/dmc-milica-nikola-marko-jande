from constructs import Construct
import os
from dotenv import load_dotenv
from aws_cdk import (
    aws_apigateway as apigw,
    aws_iam as iam,
    RemovalPolicy, CfnOutput,
    aws_logs as logs)

load_dotenv()

environment = os.getenv('ENVIRONMENT')
aws_account = os.getenv('AWS_ACCOUNT')
aws_region = os.getenv('AWS_REGION')
api_version = os.getenv('API_VERSION')


class RestAPI(Construct):
    def __init__(self, scope: Construct, construct_id: str, api_name: str, api_endpoint_id: str,
                 description: str = 'Private Rest API'):
        """
        :param scope:-
        :param id:-
        :param api_name: Api name used for api path Allowed values [a-zA-Z0-9._-],and an optional trailing '+'
        :param api_endpoint_id
        """
        super().__init__(scope, construct_id)

        self.rest_api_policy = iam.PolicyDocument(statements=[iam.PolicyStatement(actions=["execute-api:Invoke"],
                                                                                  principals=[iam.AnyPrincipal()],
                                                                                  resources=[
                                                                                        'arn:aws:execute-api:{0}:{1}:*/{2}/*'.format(aws_region, aws_account, environment.lower())
                                                                                  ],
                                                                                  effect=iam.Effect.ALLOW,
                                                                                  )])

        self.log_group_api = logs.LogGroup(self, f'{construct_id}LogGroup', log_group_name=f"/aws/api/{api_name}",
                                           retention=logs.RetentionDays.ONE_MONTH,
                                           removal_policy=RemovalPolicy.DESTROY)

        self.rest_api = apigw.RestApi(self, id=construct_id, rest_api_name=api_name, policy=self.rest_api_policy,
                                      description=description,
                                      cloud_watch_role=True,
                                      deploy_options=apigw.StageOptions(
                                          logging_level=apigw.MethodLoggingLevel.INFO,
                                          access_log_destination=apigw.LogGroupLogDestination(self.log_group_api),
                                          access_log_format=apigw.AccessLogFormat.json_with_standard_fields(
                                              caller=False,
                                              http_method=True,
                                              ip=True,
                                              protocol=True,
                                              request_time=True,
                                              resource_path=True,
                                              response_length=True,
                                              status=True,
                                              user=True
                                          ),
                                          tracing_enabled=True,
                                          data_trace_enabled=True,
                                          stage_name=environment
                                      ),
                                      endpoint_configuration=apigw.EndpointConfiguration(
                                          vpc_endpoints=[api_endpoint_id],
                                          types=[apigw.EndpointType.PRIVATE]))

        self.root_api = self.rest_api.root.add_resource("api")
        self.version = self.root_api.add_resource(str(api_version.lower()))

        self.output_rest_api_id = CfnOutput(self, 'OutputAPIRESTId', export_name=self.rest_api.rest_api_name,
                                            value=self.rest_api.rest_api_id)
