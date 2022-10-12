from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    CfnOutput)


class VPC(Construct):
    def __init__(self, scope: Construct, construct_id: str, vpc_cidr: str, vpc_name: str,
                 subnets_mask: int, api_endpoint: bool = False, nat_gw: int = 0):
        super().__init__(scope, construct_id)

        self.public_subnet = ec2.SubnetConfiguration(name='public', subnet_type=ec2.SubnetType.PUBLIC,
                                                     cidr_mask=subnets_mask)

        self.private_subnet_configuration = ec2.SubnetConfiguration(name='private',
                                                                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                                                                    cidr_mask=subnets_mask)

        self.isolated_subnet_configuration = ec2.SubnetConfiguration(name='isolated',
                                                                     subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                                                     cidr_mask=subnets_mask)

        if nat_gw > 0:
            self.app_vpc = ec2.Vpc(self, id=construct_id,
                                   vpc_name=vpc_name,
                                   nat_gateways=nat_gw,
                                   cidr=vpc_cidr,
                                   subnet_configuration=[self.public_subnet, self.private_subnet_configuration]
                                   )
        else:
            self.app_vpc = ec2.Vpc(self, id=construct_id,
                                   vpc_name=vpc_name,
                                   nat_gateways=0,
                                   cidr=vpc_cidr,
                                   subnet_configuration=[self.public_subnet, self.isolated_subnet_configuration]
                                   )

        self.output_vpc = CfnOutput(self, 'OutputVPCId', export_name=vpc_name, value=self.app_vpc.vpc_id)

        if api_endpoint is True:
            self.vpc_endpoint_api = ec2.InterfaceVpcEndpoint(self, 'APIGatewayEndpoint', vpc=self.app_vpc,
                                                             service=ec2.InterfaceVpcEndpointAwsService.APIGATEWAY
                                                             )

            self.output_api_endpoint = CfnOutput(self, 'OutputAPIEndpointId',
                                                 export_name=f'{vpc_name}-api-endpoint',
                                                 value=self.vpc_endpoint_api.vpc_endpoint_id)