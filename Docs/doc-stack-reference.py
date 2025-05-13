# Update gitlab.py and cm.py to include EC2 instance creation and bind DNS to its IP
dynamic_ip_code = {
    "pulumi-infra/gitlab-stack/gitlab.py": """\
import pulumi
import pulumi_aws as aws

# Reference hosted-zone stack
hosted_zone = pulumi.StackReference("hosted-zone")
zone_id = hosted_zone.get_output("zone_id")

# Create security group
sec_group = aws.ec2.SecurityGroup("gitlab-sg",
    description="GitLab SG",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 443, "to_port": 443, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}]
)

# Use Amazon Linux 2 AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["137112412989"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}]
)

# Key pair must exist or be created outside this script
instance = aws.ec2.Instance("gitlab-instance",
    instance_type="t3.micro",
    ami=ami.id,
    vpc_security_group_ids=[sec_group.id],
    associate_public_ip_address=True,
    tags={"Name": "GitLabServer"}
)

# DNS record
gitlab_record = aws.route53.Record("gitlab-record",
    name="gitlab.pykesys.com",
    type="A",
    ttl=300,
    zone_id=zone_id,
    records=[instance.public_ip]
)

pulumi.export("gitlab_dns", gitlab_record.fqdn)
pulumi.export("gitlab_ip", instance.public_ip)
""",
    "pulumi-infra/cm-stack/cm.py": """\
import pulumi
import pulumi_aws as aws

# Reference hosted-zone stack
hosted_zone = pulumi.StackReference("hosted-zone")
zone_id = hosted_zone.get_output("zone_id")

# Create security group
sec_group = aws.ec2.SecurityGroup("cm-sg",
    description="CM SG",
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 443, "to_port": 443, "cidr_blocks": ["0.0.0.0/0"]},
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}]
)

# Use Amazon Linux 2 AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["137112412989"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}]
)

instance = aws.ec2.Instance("cm-instance",
    instance_type="t3.micro",
    ami=ami.id,
    vpc_security_group_ids=[sec_group.id],
    associate_public_ip_address=True,
    tags={"Name": "CMServer"}
)

cm_record = aws.route53.Record("cm-record",
    name="cm.pykesys.com",
    type="A",
    ttl=300,
    zone_id=zone_id,
    records=[instance.public_ip]
)

pulumi.export("cm_dns", cm_record.fqdn)
pulumi.export("cm_ip", instance.public_ip)
"""
}

# Write updated files
for path, content in dynamic_ip_code.items():
    full_path = os.path.join("/mnt/data", path)
    with open(full_path, "w") as f:
        f.write(content)

# Repackage the entire folder
repackaged_zip = "/mnt/data/pulumi-infra-scaffold-dynamic-ip.zip"
with ZipFile(repackaged_zip, 'w') as zipf:
    for root, _, files in os.walk("/mnt/data/pulumi-infra"):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, "/mnt/data")
            zipf.write(file_path, arcname=arcname)

repackaged_zip
:wq

