import os
from dotenv import load_dotenv
from aws_cdk import (
    aws_lambda as _lambda,
    aws_logs as logs,
    Duration, RemovalPolicy
)
from constructs import Construct

load_dotenv()

environment = os.getenv('ENVIRONMENT')
app_name = os.getenv('APP_NAME')
prefix_name = environment.lower() + '-' + app_name.lower()

class LambdaIntegation(Construct):
    def __init__(self, scope: Construct, construct_id: str, func_name: str, source_dir: str, runtime: str,
                 func_environment, handler: str, layers: list, description: str = ''):
        super().__init__(scope, construct_id)

        self.function = _lambda.Function(self, id=construct_id,
                                         function_name=func_name,
                                         runtime=_lambda.Runtime(runtime),
                                         architecture=_lambda.Architecture.X86_64,
                                         handler=handler,
                                         layers=layers,
                                         description=description,
                                         code=_lambda.Code.from_asset(source_dir),
                                         timeout=Duration.seconds(60),
                                         environment=func_environment,
                                         tracing=_lambda.Tracing.ACTIVE)

        self.function_log_group = logs.LogGroup(self, 'LogsForWritingData',
                                                log_group_name=f"/aws/lambda/{func_name}",
                                                retention=logs.RetentionDays.ONE_MONTH,
                                                removal_policy=RemovalPolicy.DESTROY
                                                )

    def add_policy(self, policy):
        self.function.add_to_role_policy(policy)
