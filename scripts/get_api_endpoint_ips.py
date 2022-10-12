#!/usr/bin/env python
import os
import json
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError
from logger import log

load_dotenv()

ec2 = client('ec2', region_name=os.getenv('AWS_REGION'))
cf = client('cloudformation', region_name=os.getenv('AWS_REGION'))
environment = os.getenv('ENVIRONMENT')
app_name = os.getenv('APP_NAME')

prefix_name = f'{environment.lower()}-{app_name.lower()}'


def get_api_endpoint_id_from_stack_output():
    """Getting API endpoint ID from stack output"""
    try:
        log.info(f'Getting api vpc endpoint ID from stack {prefix_name}-stack-networking output')
        response = cf.describe_stacks(
            StackName=f'{prefix_name}-stack-networking')
        for stack in response['Stacks']:
            for output in stack['Outputs']:
                if output['ExportName'] == f'{prefix_name}-vpc-api-endpoint':
                    return output['OutputValue']
    except ClientError as e:
        log.error(f"Error:{e}")
        raise SystemExit(1)


def update_cdk_json(ip_addrs):
    """Adding API endpoint network interfaces IP-s in cdk.json"""
    log.info('Writing date into cdk.json')
    with open("cdk.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["context"]['api_endpoint_ips'] = sorted(ip_addrs)

    with open("cdk.json", "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)


def get_api_vpc_endpoints_ip():
    """Getting API endpoint network interfaces IP-s"""
    log.info(f'Getting API Endpoint network interfaces IP-s')
    ip_addrs = []
    try:
        response = ec2.describe_vpc_endpoints(VpcEndpointIds=[get_api_endpoint_id_from_stack_output()])
        for vpce in response['VpcEndpoints']:
            try:
                response = ec2.describe_network_interfaces(NetworkInterfaceIds=vpce['NetworkInterfaceIds'])
                for interface in response['NetworkInterfaces']:
                    ip_addrs.append(interface['PrivateIpAddress'])
            except ClientError as e:
                log.error(f'Error:{e}')
                raise SystemExit(1)
    except ClientError as e:
        log.error(f"Error:{e}")
        raise SystemExit(1)

    log.info(f"API Endpoint network interfaces IP-s: {'; '.join(ip_addrs)}")
    return ip_addrs


if __name__ == '__main__':
    api_endpoint_ips = get_api_vpc_endpoints_ip()
    update_cdk_json(api_endpoint_ips)
