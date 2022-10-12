from constructs import Construct
from aws_cdk import (
    aws_ecs as ecs
)


class ECS(Construct):
    def __init__(self, scope: Construct, construct_id: str, cluster_name: str, **kwargs):
        super().__init__(scope, construct_id)

        self.cluster = ecs.Cluster(self, id=construct_id, cluster_name=cluster_name, container_insights=True, **kwargs)

    def add_capacity_provider_strategy(self, provider:str):
        self.cluster.node.default_child.capacity_providers = ['FARGATE', 'FARGATE_SPOT']

        self.cluster.node.default_child.default_capacity_provider_strategy = [
            ecs.CfnCluster.CapacityProviderStrategyItemProperty(
                capacity_provider=provider)]

