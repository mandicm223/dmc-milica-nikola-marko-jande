import os
from dotenv import load_dotenv
from aws_cdk import Stack
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_certificatemanager as certificatemanager)
from constructs import Construct
from base_constructs.ecs import ECS
from base_constructs.route53 import Route53
from base_constructs.fargate import ApiUiFargate
from base_constructs.alb import AppLoadBalancer

load_dotenv()

environment = os.getenv('ENVIRONMENT')
app_name = os.getenv('APP_NAME')
ecs_provider = os.getenv('ECS_PROVIDER')
api_version = os.getenv('API_VERSION')


class CdkFrontend(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        prefix_name = f'{environment.lower()}-{app_name.lower()}'

        if 'DOMAIN_NAME' in os.environ and 'ACM_ARN' not in os.environ:
            domain_name = os.getenv('DOMAIN_NAME')
            if domain_name:
                # Import hosted zone from registered domain
                self.hosted_zone = Route53(self, 'ApplicationHostedZone', domain_name=domain_name)

                # Creates application SSL certificate from Route53
                self.certificate = self.hosted_zone.create_acm_certificate('ApplicationACM',
                                                                           domain_name=f"*.{domain_name}")

        if 'ACM_ARN' in os.environ:
            if os.getenv('ACM_ARN'):
                # Import ACM certificate in CDK from certificate arn
                self.certificate = certificatemanager.Certificate.from_certificate_arn(self, "ApplicationACM",
                                                                                       os.getenv('ACM_ARN'))

        # Creates frontend application load balancer
        self.app_load_balancer = AppLoadBalancer(self, "AppLoadBalancer", load_balancer_name=f'{prefix_name}-alb',
                                                 vpc=vpc, cert=self.certificate)

        # Creates application ecs cluster
        self.ecs = ECS(self, "ApplicationECSCluster", cluster_name=f'{prefix_name}-ecs', vpc=vpc)

        self.ecs.add_capacity_provider_strategy(provider=ecs_provider)

        self.fargate_service_security_group = ec2.SecurityGroup(self, 'ApplicationUISecurityGroup', vpc=vpc,
                                                                allow_all_outbound=True,
                                                                security_group_name=f'{prefix_name}-sg-api-ui'
                                                                )

        self.fargate_service_security_group.add_ingress_rule(ec2.Peer.ipv4(vpc.vpc_cidr_block), ec2.Port.tcp(80))

        self.app_container_image = ecs.ContainerImage.from_ecr_repository(
            ecr.Repository.from_repository_name(self, 'ApplicationECR', repository_name='swagger_ui'),
            tag=self.node.try_get_context('swagger_ui_image_tag'))

        # Creates application Fargate Service for API UI
        self.app_fargate = ApiUiFargate(self, "ApplicationFargateService", service_name=f'{prefix_name}-api-ui',
                                        cluster=self.ecs.cluster, security_group=self.fargate_service_security_group,
                                        provider=ecs_provider,
                                        cpu=512, memory=1024, container_image=self.app_container_image,
                                        alb_listener=self.app_load_balancer.https_listener)

        self.app_load_balancer.create_api_target_group('APITargetGroup', target_group_name=f'{prefix_name}-tg-api',
                                                       path=f'/{environment.lower()}/api/{api_version.lower()}/*',
                                                       vpc=vpc)

        if 'API_DOMAIN_NAME' in os.environ and 'DOMAIN_NAME' in os.environ:
            if os.getenv('API_DOMAIN_NAME') and os.getenv('DOMAIN_NAME'):
                # Creates Alias Record for ALB on Route53
                self.hosted_zone.create_alb_record('ApplicationRecord', target=self.app_load_balancer.app_alb,
                                                   record_name=os.getenv('API_DOMAIN_NAME'))
