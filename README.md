# Ansible AWS ElasticSearch Curator module
Ansible module that executes ElasticSearch curator to remove old indices. It does not close indices, since that's not accessible in AWS ElasticSearch.

## Examples
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