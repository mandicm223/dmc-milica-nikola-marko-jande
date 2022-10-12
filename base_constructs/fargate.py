from constructs import Construct
from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2
)


class ApiUiFargate(Construct):
    def __init__(self, scope: Construct, construct_id: str, service_name: str, security_group, cluster, alb_listener,
                 container_image, provider: str, cpu: int = 1024, memory: int = 2048):
        super().__init__(scope, construct_id)

        self.fargate_task = ecs.FargateTaskDefinition(self, 'ApplicationServiceTaskDefinition', family=service_name,
                                                      memory_limit_mib=memory, cpu=cpu,
                                                      runtime_platform=ecs.RuntimePlatform(
                                                          cpu_architecture=ecs.CpuArchitecture.X86_64,
                                                          operating_system_family=ecs.OperatingSystemFamily.LINUX
                                                      ))

        self.fargate_task.add_container('SwaggerUIContainer', image=container_image, memory_limit_mib=memory,
                                        container_name="swagger_ui",
                                        logging=ecs.AwsLogDriver(stream_prefix="swagger_ui-stream"),
                                        port_mappings=[ecs.PortMapping(container_port=80)])

        self.fargate_service = ecs.FargateService(self, id=construct_id, service_name=service_name, cluster=cluster,
                                                  task_definition=self.fargate_task,
                                                  capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                                                      capacity_provider=provider,
                                                      base=1,
                                                      weight=1)],
                                                  vpc_subnets=ec2.SubnetSelection(
                                                      subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                                                  security_groups=[security_group])

        self.fargate_service_target = ecs.EcsTarget(container_name='swagger_ui', container_port=80,
                                                     new_target_group_id=f'{service_name}-tg',
                                                     listener=ecs.ListenerConfig.application_listener(alb_listener))

        self.fargate_service.register_load_balancer_targets(self.fargate_service_target)
