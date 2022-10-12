from dotenv import load_dotenv
from aws_cdk import (
    aws_lambda as _lambda,
    RemovalPolicy
)
from constructs import Construct

load_dotenv()


class LambdaLayer(Construct):
    def __init__(self, scope: Construct, construct_id: str, layer_name: str, source_dir: str, runtime: str,
                 description: str):
        super().__init__(scope, construct_id)
        '''
        Add custom layer to your lambda function
        :param layer_name: Used for defining layer name
        :param source_dir: Specify layer directory
        :param runtime: Should be same as lambda function runtime
        :param description: Describe dependencies in layer
        '''
        self.lambda_layer = _lambda.LayerVersion(self, id=construct_id,
                                                 code=_lambda.Code.from_asset(source_dir),
                                                 compatible_runtimes=[_lambda.Runtime(runtime)],
                                                 description=description,
                                                 layer_version_name=layer_name,
                                                 removal_policy=RemovalPolicy.DESTROY
                                                 )
