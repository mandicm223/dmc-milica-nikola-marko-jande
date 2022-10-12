#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from aws_cdk import (
    Environment,
    App
)
from stacks.networking_stack import CdkNetworking
from stacks.backend_stack import CdkBackend
from stacks.frontend_stack import CdkFrontend

load_dotenv()

app = App()

networking_stack = CdkNetworking(app,
                                 '{0}-{1}-stack-networking'.format(os.getenv('ENVIRONMENT'), os.getenv('APP_NAME')),
                                 termination_protection=True,
                                 description='Networking - VPC, NAT, API Endpoint',
                                 env=Environment(account=os.getenv('AWS_ACCOUNT'),
                                                 region=os.getenv('AWS_REGION'))
                                 )
backend_stack = CdkBackend(app,
                           '{0}-{1}-stack-backend'.format(os.getenv('ENVIRONMENT'), os.getenv('APP_NAME')),
                           termination_protection=True,
                           endpoint_id=networking_stack.vpc.vpc_endpoint_api,
                           description='Backend - RESTAPI, LAMBDAS, DYNAMODB',
                           env=Environment(account=os.getenv('AWS_ACCOUNT'),
                                           region=os.getenv('AWS_REGION'))
                           )
frontend_stack = CdkFrontend(app,
                             '{0}-{1}-stack-frontend'.format(os.getenv('ENVIRONMENT'), os.getenv('APP_NAME')),
                             termination_protection=True,
                             vpc=networking_stack.vpc.app_vpc,
                             description='Frontend Resources - ECS, TaskDefinition, ALB',
                             env=Environment(account=os.getenv('AWS_ACCOUNT'),
                                             region=os.getenv('AWS_REGION')))

app.synth()

