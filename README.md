# Cloud Partnerships 
## AWS Serverless POC ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![AWS CDK](https://i.imgur.com/CPynmzS.png)

## Table of content

- [AWS serverless project](#CDK-serverless-POC)
  - [Description](##Description)
  - [Installation and setup](##Installation-and-setup)
      - [AWS CDK installation guide](###AWS-CDK-installation-guide)
      - [Initial setup](###Initial-setup)
  - [Project structure](##Project-structure)
      - [Base constructs](###Base-constructs)
          - [What are constructs?](####What-are-constructs)
          - [Project custom constructs](####Project-custom-constructs)
            - [Vpc](#####Vpc)
            - [Api Gateway](#####Api-Gateway)
            - [Function Layer](#####Function-Layer)
            - [Functions](#####Functions)
            - [Route53](#####Route53)
            - [Application Load Balancer](#####Application-Load-Balancer)
            - [Ecs Service](#####Ecs-Service)
            - [Fargate Service](#####Fargate-Service)
      - [Stacks](###Stacks)
          - [What are stacks?](####What-are-stacks?)
          - [Project stacks](####Project-stacks)
            - [Networking stack](#####Networking-stack)
            - [Backend stack](#####Backend-stack)
            - [Frontend stack](#####Frontend-stack)
  - [Deployment](##Deployment)
  - [Project diagram](##Project-diagram)

## Description
A template for a serverless AWS project that incorporates multiple  services from the AWS catalog to provide a pain-free setup experience for a functional REST API.

Usage of [AWS Cloud Development Kit](https://aws.amazon.com/cdk/) (CDK) allows for fast and repeatable infrastructure provisioning, while also simplifying the process of project customization in accordance with different business requirements.

This proof of concept offers a fully functional back-end, front-end and networking stacks that can be deployed on the AWS cloud platform by following the guide provided in the [Setup and installation section](##Setup-and-installation). Amongst other features the project includes the following:

- [AWS Virtual Private Cloud (VPC)](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html) to ensure security compliance
- Private REST API built using the [API Gateway](https://aws.amazon.com/api-gateway/) service with example HTTP methods accessible through a custom domain
- AWS managed [DynamoDB](https://aws.amazon.com/dynamodb/) NoSQL database for data storage
- [Swagger API](https://swagger.io/specification/v2/) documentation that runs using the [AWS Fargate ECS provider](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)

## Installation and setup

### AWS CDK installation guide
In case you don't have cdk installed already, you can do it following the next link. This link introduce you with *AWS Cloud Development Kit* in simple and easy to follow manner.
[Working with the AWS CDK in Python](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)

### Initial setup
When opening the project for the first time, make sure you are in the root directory of the project, then install the necessary dependencies by executing the following command:
```commandline
pip install -r requirements.txt
```
Then proceed to customize relevant environmental variables to suit your needs in the **.env** file, also located in the root directory of the project:
```dotenv
AWS_ACCOUNT=112233445566
AWS_REGION=eu-west-1
```
- Change the **AWS_ACCOUNT** value to the [account id](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html) of your AWS account.
- Change the **AWS_REGION** value to the desired [AWS Region](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/). Your infrastructure will be provisioned in the specified region.
```dotenv
ENVIRONMENT=dev
APP_NAME=poc
```
- Change the **ENVIRONMENT** value to your desired development environment name.
- Change the **APP_NAME** value to your desired application name.
---
*These 2 variables will be used for aws resource names throughout the project.*
*It is strongly recommended to follow the next guidelines when setting values for previuosly mentioned environment variables.*
*APP_NAME* variable should only contain ***uppercase alphabetical characters***, ***lowercase alphabetical characters***, ***dashes*** or ***underscores*** in order to set a right form of application name.
*ENVIRONMENT* variable should only contain ***uppercase alphabetical characters*** or ***lowercase alphabetical characters*** in order to set a right form of environment name. 

---
```dotenv 
REPOSITORY_NAME=poc-serverless
VPC_CIDR=10.10.16.0/24
SUBNET_CIDR=27
NAT_GATEWAYS=1
```
- Leave the default value for **REPOSITORY_NAME** variable since it is the name of a CodeCommit repository.
- Change the **VPC_CIDR** value to the desired [cidr block range](https://docs.aws.amazon.com/vpc/latest/userguide/how-it-works.html#vpc-ip-addressing) that your VPC will use for resource address assignment.
- Change the **SUBNET_CIDR** value to value appropriate for chosen network mask.
- It is recommended to leave a default number of nat gateways, unless there is a specific need to have more than one. 
  With one nat gateway deployed, you will have cost-effective and well-operating application with all functionalities nedeed.
    (Sensible default values for these 2 variables are provided by default)
```dotenv
ECS_PROVIDER=FARGATE_SPOT
DOMAIN_NAME=levi9serverlesspoc.com
API_DOMAIN_NAME=api.levi9serverlesspoc.com
API_VERSION=v1
API_DESCRIPTION="POC Serverless Rest API"
```
- Change the **ECS_PROVIDER** value to choose a desired capacity provider for the containerized Swagger API documentation (FARGATE/FARGATE_SPOT). Compare the difference [ECS Fargate capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html)
- Change the **DOMAIN_NAME** variable to reflect your domain name (second-level domain and top-level domain) registered on Route53, or third-party domain, if you intend to use one.
(*Example: amazon.com, levi9.com*) 
- Add **ACM_ARN** variable and set its [ARN](https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html) value to an arn of your ACM certificate. You can create one manually before deployment phase, in the *AWS Certificate Manager* console with recommended DNS validation in the account where application will be deployed, or import third-party certificate. Public SSL/TLS certificate provisioned through AWS Certificate Manager protects previously registered domain on Route53. If you don't specify the arn, the new certificate will be automatically generated during the infrastructure provisioning phase.
(*Example: arn:aws:acm:AWS_REGION:AWS_ACCOUNT:certificate/certificate_id*)
- Add **IP_WHITELIST** variable and set its value in form of an ip address list for application load balancer security group. If you want to allow access to load balancer from any ipv4 address, than skip setting this environment variable.
(*Example: 192.168.10.10/32;192.168.10.11/32;*)
- Change the **API_DOMAIN_NAME** value to a sub-domain name of a domain of the above specified domain.
(*Example: api.amazon.com, api.levi9.com*)
- Change the **API_VERSION** value to reflect the current version number of your API.
- Change the **API_DESCRIPTION** value to one that accurately describes your project.
## Project structure
This section aims to describe the general shape of the project, its parts and interactions between them.
### Base-constructs
#### What are constructs?
[Constructs](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html) in AWS CDK represent the building blocks that can be used to assemble [stacks](###Stacks). Depending on their level they represent 1 or more AWS resources to be deployed. Certain properties for each construct are configurable, but higher level constructs may abstract away certain properties and use sensible default values.

Base constructs in this particular project are assemblages of constructs offered by AWS CDK and various logic that is there to ensure sucessful and quick deployment of the application.
#### Project custom constructs
This part of the construct section will go through base constructs that are combined in the stack mentioned below to group and abstract AWS resources.
Variables marked as specified are options which values you can alter in stack where explained construct belongs to.
Each construct is described in enough detail for successful customization of stacks by the client, but any major alterations are not recommended, as they may require significant technical support and help from Levi9 experts.
##### Vpc
- Vpc custom construct defines the subnet configuration, public and private routing tables, public and private network access control list, a NAT gateway and an internet gateway. With function for calculating vpc subnet cidr bits you can provide public and private subnets for all the availabillity zones in your region. App vpc is created with attributes specified in the .env file such as vpc cidr block, number of nat gateways to deploy and the subnet cidr block. Private interface vpc endpoint is deployed in the previously created vpc and later attached to the rest api.
##### Api Gateway
- Private REST api with lambda intergations is deployed with the specified name, id and description. Your api gateway will be created with a properly configured [IAM](https://aws.amazon.com/iam/) policy, resources and a version number of your choice. In order to track the activity of your api, you will have a [CloudWatch](https://aws.amazon.com/cloudwatch/) log group deployed in this part of the project.
##### Function Layer
- Custom lambda layer is added to your lambda function with a specified layer name, source layer directory, and a runtime, which should be the same as lambda function runtime. You can use the description property to describe dependencies in the layer.
##### Functions
- Lambda functions are deployed with a specified function name, runtime, handler, layers, description, source directory, and a dynamodb table name as function environment variable. Deployment is done with predefined attributes which are active tracing, type of architecture and timeout.
##### Route53
- Hosted zone from used domain is imported with the 'from_lookup' method. Certificate is created with specified id and domain name. Load balancer A type record is created with specified construct id and record name with load balancer as target and predefined time to live parameter.
##### Application Load Balancer
- Security group is deployed with inbound rules in accordance with list of ip addresses mentioned earlier. Internet-facing application load balancer with https listener, listener rule and redirection is deployed with specified id, name and vpc created and deployed previously. Another resource deployed in this part of the project is an api target group with ipv4 addresses of network interfaces as targets, which belong to previously created and deployed vpc endpoint from the networking stack.
##### Ecs Service
- Elastic container service cluster is deployed with specified cluster name and capacity provider which represents default capacity provider strategy for this cluster.
##### Fargate Service
- Fargate service security group is deployed in the previously created vpc with inbound rules for tcp port 80 open only for the vpc network range. Container attached to fargate task hosting the custom swagger ui is created with image stored in the specified, existing elastic container registry ([ECR](https://aws.amazon.com/ecr/)) and tag name from the cdk.json file. Fargate service is deployed with specified service name, provider, cpu and memory limit.
### Stacks
#### What are stacks?
[Stack](https://docs.aws.amazon.com/cdk/v2/guide/stacks.html) is a logical grouping of constructs that forms a unit of deployment. They are there to integrate services that work together and often share different resources between themselves.
#### Project stacks
This part of the stacks section will go through stacks created in the project and deployed with aws CD service CodePipeline.
##### Networking stack
Networking stack deployes vpc custom construct used in this serverless application. More about aws vpc service you can find here: [vpc](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html).
##### Backend stack
Backend stack deploys the rest api, lambda functions with a custom function layer and  a dynamodb table with specified partition key name and several predefined attributes. Api gateway with lambda integration is created with get, post, put and delete http methods and api model with given content type, model name and schema. More about these aws services can be found here: [api gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html), [lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html), [dynamodb database](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html).
##### Frontend stack
Frontend stack deploys route53, load balancer, ecs and fargate custom constructs. Stack has a certificate check implemented - in case your have a pre-existing ACM certificate or a third-party certificate, existing certificate can be imported by specifying the ACM_ARN value in the .env file. In case metioned resource does not exist, creation is initiated by calling the appropriate method from the Route53 class. More about these aws services can be found here: [route53](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html), [application load balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html), [ecs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html), [fargate](https://docs.aws.amazon.com/AmazonECS/latest/userguide/what-is-fargate.html).
## Deployment
Once your code is delivered to CodeCommit repo, with every code update CodePipeline will be triggered with update of the pipeline stack and pull your modified code from mentioned repository. By triggering the pipeline, you will have an automated way of deploying stacks mentioned in *Stacks* section, described in enough detail to understand the core princip and idea befind this serveless project.
## Project diagram
![Click here for the project diagram](https://i.imgur.com/ycqVhm0.png)

















 
