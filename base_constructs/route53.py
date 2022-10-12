from constructs import Construct
from aws_cdk import (
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    Duration
)

class Route53(Construct):

    def __init__(self, scope: Construct, construct_id: str, domain_name: str):
        super().__init__(scope, construct_id)

        ### Import existing hosted zone ###
        self.hosted_zone = route53.HostedZone.from_lookup(self, construct_id, domain_name=domain_name)

    def create_alb_record(self, construct_id: str, record_name: str, target):
        route53.RecordSet(self, construct_id, record_type=route53.RecordType.A,
                          target=route53.RecordTarget.from_alias(route53_targets.LoadBalancerTarget(target)), zone=self.hosted_zone,
                          record_name=record_name,
                          ttl=Duration.minutes(5))

    def create_acm_certificate(self, construct_id: str, domain_name: str):
        return acm.Certificate(self, id=construct_id, domain_name=domain_name,
                               validation=acm.CertificateValidation.from_dns(self.hosted_zone))
