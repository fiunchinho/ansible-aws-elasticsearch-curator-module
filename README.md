# Ansible AWS ElasticSearch Curator module
Ansible module that executes ElasticSearch curator to remove old indices. It does not close indices, since that's not accessible in AWS ElasticSearch.

## Curator
This repository has two different branches to give support to Curator versions both higher and lower than v4.0.0.
If you have an older ElasticSearch version and you need Curator version lower than 4.0.0 use the 1.x releases of this module. Otherwise, use the 2.x releases.

## Usage
The following playbook will, when executed, remove indices older than 30 days.

    ---

    - hosts: localhost
      tasks:
        - name: "Create ElasticSearch cluster"
          ec2_elasticsearch_curator:
            host: "some.elasticsearch.com"
            port: 9200
            region: "eu-west-1"
            aws_access_key: "AKIAJ5CC6CARRKOX5V7Q"
            aws_secret_key: "cfDKFSXEo1CC6gfhfhCARRKOX5V7Q"
            prefix: "logstash"
            older_than: 30
            time_unit: "days"
            timestring: "%Y.%d.%m"

Execute it like

```bash
$ virtualenv curator
$ source curator/bin/activate
$ pip install -r requirements.txt
$ curator/bin/ansible-playbook playbook.yml --extra-vars "ec2_access_key=AKIAI********* ec2_secret_key=zJ************** elasticsearch_host=elastic.search.host.com elasticsearch_port=80 older_than=30"
```