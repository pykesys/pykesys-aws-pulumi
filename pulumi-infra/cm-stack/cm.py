import pulumi
import pulumi_aws as aws

# Reference hosted-zone stack
hosted_zone = pulumi.StackReference("hosted-zone")
zone_id = hosted_zone.get_output("zone_id")

# SSH key pair
key_pair = aws.ec2.KeyPair("cm-keypair",
    public_key=open("~/.ssh/id_rsa.pub").read().strip()
)

# Security Group
sec_group = aws.ec2.SecurityGroup("cm-sg",
    description="CM SG",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 443, "to_port": 443, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}]
)

# AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["137112412989"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}]
)

# EC2 Instance
instance = aws.ec2.Instance("cm-instance",
    instance_type="t3.micro",
    ami=ami.id,
    vpc_security_group_ids=[sec_group.id],
    associate_public_ip_address=True,
    key_name=key_pair.key_name,
    tags={"Name": "CMServer"}
)

# DNS Record
cm_record = aws.route53.Record("cm-record",
    name="cm.pykesys.com",
    type="A",
    ttl=300,
    zone_id=zone_id,
    records=[instance.public_ip]
)

pulumi.export("cm_dns", cm_record.fqdn)
pulumi.export("cm_ip", instance.public_ip)
