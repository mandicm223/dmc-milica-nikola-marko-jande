from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    Fn)


class Vpc(Construct):
    def __init__(self, scope: Construct, construct_id: str, name: str, vpc_cidr: str, nat_gw: bool = False,
                 api_endpoint: bool = False):
        super().__init__(scope, construct_id)

        """Creates VPC with 3 Public and 3 Private Subnet-s, 
        Internet Gateway, DHCP, Public and Private route table, NACLs"""

        def __calculate_vpc_subnet_cidr_bits(cidr):
            mask = (cidr.split("/"))[1]
            if mask <= '20':
                return '9'
            if mask == '21':
                return '8'
            if mask == '22':
                return '7'
            if mask == '23':
                return '6'
            if mask == '24':
                return '5'

        self.app_vpc = ec2.CfnVPC(self, id=construct_id, cidr_block=vpc_cidr, enable_dns_hostnames=True,
                                  enable_dns_support=True,
                                  tags=([{'key': 'Name', 'value': f'{name}-vpc'}]))

        cidr_bits = __calculate_vpc_subnet_cidr_bits(vpc_cidr)

        self.subnet_public1 = ec2.CfnSubnet(self, 'SubnetPublic1',
                                            availability_zone=Fn.select(0, Fn.get_azs()),
                                            cidr_block=Fn.select(0,
                                                                 Fn.cidr(self.app_vpc.attr_cidr_block, 6, cidr_bits)),
                                            vpc_id=self.app_vpc.ref,
                                            map_public_ip_on_launch=False,
                                            tags=(
                                                [{'key': 'Name', 'value': f'{name}-subnet-public1'}]))

        self.subnet_public2 = ec2.CfnSubnet(self, 'SubnetPublic2',
                                            availability_zone=Fn.select(1, Fn.get_azs()),
                                            cidr_block=Fn.select(1,
                                                                 Fn.cidr(self.app_vpc.attr_cidr_block, 6, cidr_bits)),
                                            vpc_id=self.app_vpc.ref,
                                            map_public_ip_on_launch=False,
                                            tags=(
                                                [{'key': 'Name', 'value': f'{name}-subnet-public2'}]))

        self.subnet_public3 = ec2.CfnSubnet(self, "SubnetPublic3",
                                            availability_zone=Fn.select(2, Fn.get_azs()),
                                            cidr_block=Fn.select(2,
                                                                 Fn.cidr(self.app_vpc.attr_cidr_block, 6, cidr_bits)),
                                            vpc_id=self.app_vpc.ref,
                                            map_public_ip_on_launch=False,
                                            tags=(
                                                [{'key': 'Name', 'value': f'{name}-subnet-public3'}]))

        self.subnet_private1 = ec2.CfnSubnet(self, "SubnetPrivate1",
                                             availability_zone=Fn.select(0, Fn.get_azs()),
                                             cidr_block=Fn.select(3,
                                                                  Fn.cidr(self.app_vpc.attr_cidr_block, 6, cidr_bits)),
                                             vpc_id=self.app_vpc.ref,
                                             map_public_ip_on_launch=False,
                                             tags=(
                                                 [{'key': 'Name', 'value': f'{name}-subnet-private1'}]))

        self.subnet_private2 = ec2.CfnSubnet(self, "SubnetPrivate2",
                                             availability_zone=Fn.select(1, Fn.get_azs()),
                                             cidr_block=Fn.select(4,
                                                                  Fn.cidr(self.app_vpc.attr_cidr_block, 6, cidr_bits)),
                                             vpc_id=self.app_vpc.ref,
                                             map_public_ip_on_launch=False,
                                             tags=(
                                                 [{'key': 'Name', 'value': f'{name}-subnet-private2'}]))

        self.subnet_private3 = ec2.CfnSubnet(self, "SubnetPrivate3",
                                             availability_zone=Fn.select(2, Fn.get_azs()),
                                             cidr_block=Fn.select(5,
                                                                  Fn.cidr(self.app_vpc.attr_cidr_block, 6, cidr_bits)),
                                             vpc_id=self.app_vpc.ref,
                                             map_public_ip_on_launch=False,
                                             tags=(
                                                 [{'key': 'Name', 'value': f'{name}-subnet-private3'}]))

        self.internet_gateway = ec2.CfnInternetGateway(self, "InternetGateway",
                                                       tags=(
                                                           [{'key': 'Name',
                                                             'value': f'{name}-internet-gateway'}]))

        self.attachment_internet_gateway = ec2.CfnVPCGatewayAttachment(self, "VPCGatewayAttachment",
                                                                       vpc_id=self.app_vpc.ref,
                                                                       internet_gateway_id=self.internet_gateway.ref)

        self.dhcp = ec2.CfnDHCPOptions(self, "DHCP", domain_name='eu-west-1.compute.internal',
                                       domain_name_servers=['AmazonProvidedDNS'],
                                       tags=([{'key': 'Name', 'value': f'{name}-dhcp'}]))

        self.acl_public = ec2.CfnNetworkAcl(self, 'ACLPublic',
                                            vpc_id=self.app_vpc.ref,
                                            tags=([{'key': 'Name', 'value': f'{name}-acl-public-subnets'}]))

        self.acl_private = ec2.CfnNetworkAcl(self, 'ACLPrivate',
                                             vpc_id=self.app_vpc.ref,
                                             tags=([{'key': 'Name', 'value': f'{name}--acl-private-subnets'}]))

        self.acl_public_entry_in = ec2.CfnNetworkAclEntry(self, 'ACLPublicEntryIn', cidr_block='0.0.0.0/0',
                                                          egress=True,
                                                          protocol=-1,
                                                          rule_action='allow',
                                                          rule_number=100,
                                                          network_acl_id=self.acl_public.ref)

        self.acl_public_entry_out = ec2.CfnNetworkAclEntry(self, 'ACLPublicEntryOut', cidr_block='0.0.0.0/0',
                                                           protocol=-1,
                                                           rule_action='allow',
                                                           rule_number=100,
                                                           network_acl_id=self.acl_public.ref)

        self.acl_private_entry_in = ec2.CfnNetworkAclEntry(self, 'ACLPrivateEntryIn', cidr_block='0.0.0.0/0',
                                                           egress=True,
                                                           protocol=-1,
                                                           rule_action='allow',
                                                           rule_number=100,
                                                           network_acl_id=self.acl_private.ref)

        self.acl_private_entry_out = ec2.CfnNetworkAclEntry(self, 'ACLPrivateEntryOut', cidr_block='0.0.0.0/0',
                                                            protocol=-1,
                                                            rule_action='allow',
                                                            rule_number=100,
                                                            network_acl_id=self.acl_private.ref)

        self.acl_association_subnet_public1 = ec2.CfnSubnetNetworkAclAssociation(self, 'PublicSubnet1AclAssociation',
                                                                                 subnet_id=self.subnet_public1.ref,
                                                                                 network_acl_id=self.acl_public.ref)

        self.acl_association_subnet_public2 = ec2.CfnSubnetNetworkAclAssociation(self, 'PublicSubnet2AclAssociation',
                                                                                 subnet_id=self.subnet_public2.ref,
                                                                                 network_acl_id=self.acl_public.ref)

        self.acl_association_subnet_public3 = ec2.CfnSubnetNetworkAclAssociation(self, 'PublicSubnet3AclAssociation',
                                                                                 subnet_id=self.subnet_public3.ref,
                                                                                 network_acl_id=self.acl_public.ref)

        self.acl_association_subnet_private1 = ec2.CfnSubnetNetworkAclAssociation(self, 'PrivateSubnet1AclAssociation',
                                                                                  subnet_id=self.subnet_private1.ref,
                                                                                  network_acl_id=self.acl_private.ref)

        self.acl_association_subnet_private2 = ec2.CfnSubnetNetworkAclAssociation(self, 'PrivateSubnet2AclAssociation',
                                                                                  subnet_id=self.subnet_private2.ref,
                                                                                  network_acl_id=self.acl_private.ref)

        self.acl_association_subnet_private3 = ec2.CfnSubnetNetworkAclAssociation(self, 'PrivateSubnet3AclAssociation',
                                                                                  subnet_id=self.subnet_private3.ref,
                                                                                  network_acl_id=self.acl_private.ref)

        self.public_route_table = ec2.CfnRouteTable(self, "PublicRouteTable", vpc_id=self.app_vpc.ref,
                                                    tags=([{'key': 'Name',
                                                            'value': f'{name}-route-table-public-subnets'}]))

        self.subnet_public1_route_table_association = ec2.CfnSubnetRouteTableAssociation(self,
                                                                                         "SubnetPublic1RouteAssociation",
                                                                                         route_table_id=self.public_route_table.ref,
                                                                                         subnet_id=self.subnet_public1.ref)

        self.subnet_public2_route_table_association = ec2.CfnSubnetRouteTableAssociation(self,
                                                                                         "SubnetPublic2RouteAssociation",
                                                                                         route_table_id=self.public_route_table.ref,
                                                                                         subnet_id=self.subnet_public2.ref)

        self.subnet_public3_route_table_association = ec2.CfnSubnetRouteTableAssociation(self,
                                                                                         "SubnetPublic3RouteAssociation",
                                                                                         route_table_id=self.public_route_table.ref,
                                                                                         subnet_id=self.subnet_public3.ref)

        self.private_route_table = ec2.CfnRouteTable(self, "PrivateRouteTable", vpc_id=self.app_vpc.ref,
                                                     tags=([{'key': 'Name',
                                                             'value': f'{name}-route-table-private-subnets'}]))

        self.subnet_private1_route_table_association = ec2.CfnSubnetRouteTableAssociation(self,
                                                                                          "SubnetPrivate1RouteAssociation",
                                                                                          route_table_id=self.private_route_table.ref,
                                                                                          subnet_id=self.subnet_private1.ref)

        self.subnet_private2_route_table_association = ec2.CfnSubnetRouteTableAssociation(self,
                                                                                          "SubnetPrivate2RouteAssociation",
                                                                                          route_table_id=self.private_route_table.ref,
                                                                                          subnet_id=self.subnet_private2.ref)

        self.subnet_private3_route_table_association = ec2.CfnSubnetRouteTableAssociation(self,
                                                                                          "SubnetPrivate3RouteAssociation",
                                                                                          route_table_id=self.private_route_table.ref,
                                                                                          subnet_id=self.subnet_private3.ref)

        self.public_route = ec2.CfnRoute(self, 'PublicRoute', route_table_id=self.public_route_table.ref,
                                         destination_cidr_block='0.0.0.0/0', gateway_id=self.internet_gateway.ref)

        if nat_gw is True:
            self.elastic_ip = ec2.CfnEIP(self, 'EIP',
                                         domain='vpc')

            self.nat_gateway = ec2.CfnNatGateway(self, 'NAT',
                                                 allocation_id=self.elastic_ip.attr_allocation_id,
                                                 subnet_id=self.subnet_public1.ref,
                                                 tags=([{'key': 'Name', 'value': f'{name}-gw-nat'}]))

            self.nat_gateway.add_depends_on(self.internet_gateway)

            self.private_route = ec2.CfnRoute(self, 'PrivateRoute',
                                              route_table_id=self.private_route_table.ref,
                                              destination_cidr_block='0.0.0.0/0',
                                              nat_gateway_id=self.nat_gateway.ref)
