#!/usr/bin/python
# encoding: utf-8

# (c) 2015, Jose Armesto <jose@armesto.net>
#
# This file is part of Ansible
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = """
---
module: ec2_elasticsearch_curator
short_description: Executes elasticsearch-curator to remove elasticsearch indices older than an specified amount of time.
description:
  - It depends on import elasticsearch, curator, logging and requests_aws4auth
  - Created with AWS ElasticSearch on mind

version_added: "2.1"
author: "Jose Armesto (@fiunchinho)"
options:
  host:
    description:
      - ElasticSearch host.
    required: true
  port:
    description:
      - Port of the ElasticSearch host
    default: 80
  region:
    description:
      - The AWS region to use.
    required: true
    aliases: ['aws_region', 'ec2_region']
  aws_access_key:
    description:
      - AWS access key to sign the requests.
    required: true
    aliases: ['aws_access_key', 'ec2_access_key']
  aws_secret_key:
    description:
      - AWS secret key to sign the requests.
    required: true
    aliases: ['aws_secret_key', 'ec2_secret_key']
  older_than:
    description:
      - It'll remove indices older than this value (in time units). For example, 3 days.
    default: 7
  time_unit:
    description:
      - Time unit to use.
    choices: [ "hours", "days", "weeks", "months" ]
    default: "days"
  timestring:
    description:
      - It'll match indices following this pattern.
    default: "%Y.%m.%d"
requirements:
  - "python >= 2.6"
  - boto3
"""

EXAMPLES = '''

- ec2_elasticsearch_curator:
    host: "some.elasticsearch.com"
    port: 9200
    region: "eu-west-1"
    aws_access_key: "AKIAJ5CC6CARRKOX5V7Q"
    aws_secret_key: "cfDKFSXEo1CC6gfhfhCARRKOX5V7Q"
    older_than: 30
    time_unit: "days"
    timestring: "%Y.%d.%m"
'''
try:
    import elasticsearch
    import curator
    import logging
    from requests_aws4auth import AWS4Auth

    logging.basicConfig()

except ImportError:
    module.fail_json(msg='requests_aws4auth, logging, elasticsearch and elasticsearch-curator are required for this module, install via pip or your package manager')

def get_elasticsearch_client(module):
    host = module.params.get('host')
    port = module.params.get('port')
    region = module.params.get('region')
    aws_access_key = module.params.get('aws_access_key')
    aws_secret_key = module.params.get('aws_secret_key')

    awsauth = AWS4Auth(aws_access_key, aws_secret_key, region, 'es')

    return elasticsearch.Elasticsearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=awsauth,
            use_ssl=False,
            verify_certs=True,
            connection_class=elasticsearch.RequestsHttpConnection
    )

def filter_indices(module, client):
    prefix = module.params.get('prefix')
    older_than = module.params.get('older_than')
    time_unit = module.params.get('time_unit')
    timestring = module.params.get('timestring')

    indices = curator.get_indices(client)

    _filter = curator.build_filter(kindOf='prefix', value=prefix)
    indices = curator.apply_filter(indices, **_filter)

    _filter = curator.build_filter(kindOf='older_than', value=older_than, time_unit=time_unit, timestring=timestring)
    return curator.apply_filter(indices, **_filter)

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
            host = dict(required=True),
            port = dict(default=80),
            prefix = dict(default="logstash"),
            older_than = dict(default=7),
            time_unit = dict(default="days", choices=["hours", "days", "weeks", "months"]),
            timestring = dict(default="%Y.%m.%d"),
    ))

    module = AnsibleModule(
            argument_spec=argument_spec,
    )

    try:
        client = get_elasticsearch_client(module)
        indices = filter_indices(module, client)

        if indices:
            # curator.delete_indices(client, indices)
            module.exit_json(changed=True, msg="The following indices have been removed: " + ", ".join(indices))
        else:
            module.exit_json(msg="No indices matching the filters were found. No indices removed")
    except (StandardError), e:
        module.fail_json(msg=str(e))


# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()