import os
from zipfile import ZipFile

# Define folder structure and file content
repo_structure = {
    "pulumi-infra/hosted-zone/Pulumi.yaml": """\
name: hosted-zone
runtime: python
description: Hosted zone for pykesys.com
""",
    "pulumi-infra/hosted-zone/index.py": """\
import pulumi
import pulumi_aws as aws

domain_name = "pykesys.com"

zone = aws.route53.Zone("pykesys-zone", name=domain_name)

pulumi.export("zone_id", zone.zone_id)
pulumi.export("name_servers", zone.name_servers)
""",
    "pulumi-infra/gitlab-stack/Pulumi.yaml": """\
name: gitlab-stack
runtime: python
description: GitLab deployment using existing Route 53 zone
""",
    "pulumi-infra/gitlab-stack/gitlab.py": "# Placeholder for GitLab stack code",
    "pulumi-infra/cm-stack/Pulumi.yaml": """\
name: cm-stack
runtime: python
description: Chef/Ansible/Artifactory deployment using existing Route 53 zone
""",
    "pulumi-infra/cm-stack/cm.py": "# Placeholder for CM stack code"
}

# Create zip file
zip_path = "/mnt/data/pulumi-infra-scaffold.zip"
with ZipFile(zip_path, 'w') as zipf:
    for filepath, content in repo_structure.items():
        full_path = os.path.join("/mnt/data", filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        zipf.write(full_path, arcname=filepath)

zip_path

