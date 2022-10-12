import os
from dotenv import load_dotenv
from constructs import Construct
from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elbv2_targets,
    aws_ec2 as ec2)

load_dotenv()


class AppLoadBalancer(Construct):
    def __init__(self, scope: Construct, construct_id: str, vpc, load_balancer_name: str, cert, open_alb: bool = True):
        super().__init__(scope, construct_id)

        if 'IP_WHITELIST' in os.environ:
            if os.getenv('IP_WHITELIST'):
                open_alb = False

        self.alb_security_group = ec2.SecurityGroup(self, "AppLoadBalancerSecurityGroup",
                                                    security_group_name=f'{load_balancer_name}-security-group',
                                                    allow_all_outbound=True,
                                                    vpc=vpc)

        self.app_alb = elbv2.ApplicationLoadBalancer(self, id=construct_id, load_balancer_name=load_balancer_name,
                                                     vpc=vpc,
                                                     internet_facing=True, security_group=self.alb_security_group)

        self.app_alb.add_redirect(source_port=80, target_port=443, source_protocol=elbv2.ApplicationProtocol.HTTP,
                                  target_protocol=elbv2.ApplicationProtocol.HTTPS, open=open_alb)

        self.https_listener = self.app_alb.add_listener('HTTPSListener', certificates=[cert], port=443,
                                                        protocol=elbv2.ApplicationProtocol.HTTPS,
                                                        open=open_alb)

        if open_alb is False:
            ips = os.getenv('IP_WHITELIST').split(';')
            for ip in ips:
                self.alb_security_group.add_ingress_rule(peer=ec2.Peer.ipv4(ip), connection=ec2.Port.tcp(443))

    def create_api_target_group(self, construct_id: str, target_group_name: str, path: str, vpc):

        targets = self.node.try_get_context('api_endpoint_ips')
        api_targets = []
        for target in targets:
            api_targets.append(elbv2_targets.IpTarget(target))

        self.api_target_group = elbv2.ApplicationTargetGroup(self, id=construct_id,
                                                             target_group_name=target_group_name,
                                                             protocol=elbv2.ApplicationProtocol.HTTPS,
                                                             vpc=vpc,
                                                             health_check=elbv2.HealthCheck(
                                                                 healthy_http_codes='403'),
                                                             targets=api_targets
                                                             )

        self.api_listener_rule = elbv2.ApplicationListenerRule(self, f'{construct_id}ListenerRule',
                                                               listener=self.https_listener,
                                                               conditions=[
                                                                   elbv2.ListenerCondition.path_patterns([path])],
                                                               priority=2, target_groups=[self.api_target_group])
