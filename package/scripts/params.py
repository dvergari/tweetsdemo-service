#!/usr/bin/env python
from resource_management import *
import os


config = Script.get_config()

service_scriptsdir = os.path.realpath(__file__).split('/scripts')[0] + '/scripts/'

nifi_dir = config['configurations']['tweet-env']['nifi_dir']
tweet_piddir = config['configurations']['tweet-env']['tweet_piddir']


### Twitter configuration ###
consumer_key = config['configurations']['tweet-env']['consumer_key']
consumer_secret = config['configurations']['tweet-env']['consumer_secret']
access_token = config['configurations']['tweet-env']['access_token']
access_secret = config['configurations']['tweet-env']['access_secret']


### Cluster configuration ###
master_configs = config['clusterHostInfo']
ambari_server_host = str(master_configs['ambari_server_host'][0])
namenode_host =  str(master_configs['namenode_host'][0])
namenode_port = get_port_from_url(config['configurations']['core-site']['fs.defaultFS']) #8020
nimbus_host = str(master_configs['nimbus_hosts'][0])
hive_metastore_host = str(master_configs['hive_metastore_host'][0])
hive_metastore_port = get_port_from_url(config['configurations']['hive-site']['hive.metastore.uris']) #"9083"
supervisor_hosts = str(', '.join(master_configs['supervisor_hosts']))
hbase_master_host = str(master_configs['hbase_master_hosts'][0])
kafka_broker_host = str(master_configs['kafka_broker_hosts'][0])
if 'port' in config['configurations']['kafka-broker']:
  kafka_port = str(config['configurations']['kafka-broker']['port'])
else:
  kafka_port = get_port_from_url(config['configurations']['kafka-broker']['listeners'])


