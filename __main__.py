"""An AWS Python Pulumi program"""
import pulumi
from pulumi_aws import s3
from pulumi_aws import ec2

'''
Define o uso da vpc padrão.
Outra forma de usar:
defaultvpc = ec2.DefaultVpc(resource_name="vpc-0d9362297b223acff")
'''
defaultvpc = ec2.DefaultVpc("default", tags={
    "Name": "Default VPC",
})

'''
Usa a subnet padrao.
'''
default_az1 = ec2.DefaultSubnet("defaultAz1",
    availability_zone="us-east-1d",
    tags={
        "Name": "Default subnet for us-east-1d",
    })


'''Define o SG usando a vpc padrão'''
SG = ec2.SecurityGroup('sg-freetier',
    vpc_id=defaultvpc.id,
    description='Enable HTTP access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0'] }
    ])

'''Retorna a ami do ubuntu'''
ubuntu = ec2.get_ami(most_recent=True,
    filters=[
        ec2.GetAmiFilterArgs(
            name="name",
            values=["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"],
        ),
        ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
    ],
    owners=["099720109477"])

'''Pela documentação não tem como gerar um par de chaves igual no terraform.
Precisa passar a chave publica e para acessar a máquina tem que usar a sua
chave privada
'''
keypair = ec2.KeyPair("deployer2", public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDOtZrYbdbSghIugB5sNGgwChoIUkj7wtc0kYD0naGS9JVmQZMtka6q4XuPNjb2aO7A9pG+7kvQ7etYlMsUFE7gog7mibpdME04KX2uIIGspKfd2jDbf/4eQwzSZ7bwAkDWS3qoWH9OkIPfak9Pj3XNxZppVur+bnqOwl0ovstzI9vq+dpxuz+FHcj67wW2QVLA8A+Y3rHUdU3pqlRAavVCorx+gJnH6/52IeCRSt52ON0Lwzj2wvwEBg1+soAWf+XLx3eu9yWpdDzvlK65aj00ug9/MCgh/7QuFAutRaQmXr6piEAWcYQSusds3jNTw+uyJNRT2j/zo3ZxczZoO1kiHsVm1xuhoTptqXBU98yzjh9D5uUrQ6nz9DAFspXyFsQPiHdR8Kdk4xsHZ/7iz+EuHQOp/Y+SMfhRHL0YzgUCzmWp6HeU+wGdypNADeMuV08zrPNlUtNb7M19bOg+tKT0iJZWvvXOy+NU00atCvU6K0L8HWq61EYwBEgI4tTuLaE= mtuser@CP5626")

web = ec2.Instance("machine",
    ami=ubuntu.id,
    key_name=keypair.id,
    instance_type="t3.micro",
    vpc_security_group_ids=[SG.id],
    subnet_id = default_az1.id,
    tags={
        "Name": "machineinicial",
    })


'''Output pulumi'''
pulumi.export('keypair', keypair.key_pair_id)
pulumi.export('vpcid', defaultvpc.id)
