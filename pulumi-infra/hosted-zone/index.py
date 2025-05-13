import pulumi
import pulumi_aws as aws

domain_name = "pykesys.com"

zone = aws.route53.Zone("pykesys-zone", name=domain_name)

pulumi.export("zone_id", zone.zone_id)
pulumi.export("name_servers", zone.name_servers)
