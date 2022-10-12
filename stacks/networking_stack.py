import os
from dotenv import load_dotenv
from aws_cdk import Stack
from constructs import Construct
from base_constructs.vpc import VPC

load_dotenv()

environment = os.getenv('ENVIRONMENT')
app_name = os.getenv('APP_NAME')
vpc_cidr = os.getenv('VPC_CIDR')
subnet_cidr = os.getenv('SUBNET_CIDR')
nat_gateways = os.getenv('NAT_GATEWAYS')


class CdkNetworking(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        prefix_name = f'{environment.lower()}-{app_name.lower()}'

        self.vpc = VPC(self, 'ApplicationVPC', vpc_name=f'{prefix_name}-vpc', vpc_cidr=vpc_cidr,
                       nat_gw=int(nat_gateways),
                       subnets_mask=int(subnet_cidr), api_endpoint=True)
