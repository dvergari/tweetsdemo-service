"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys, os, pwd
from resource_management import *
from resource_management.libraries.functions import check_process_status
from subprocess import call

class Master(Script):
  def install(self, env):
    self.install_packages(env)
    import params
    import status_params

    Execute('echo Scriptdir is: ' + params.service_scriptsdir)

    Execute('echo installation directory is: ' + params.tweet_installdir)
    Execute('echo ambari host: ' + params.ambari_server_host)
    Execute('echo namenode host: ' + params.namenode_host)
    Execute('echo nimbus host: ' + params.nimbus_host)
    Execute('echo hive host: ' + params.hive_metastore_host)
    Execute('echo hbase host: ' + params.hbase_master_host)
    Execute('echo kafka broker: ' + params.kafka_broker_host)


    Directory(params.tweet_installdir, mode=0755, owner='root', group='root', recursive=True)
    Directory(status_params.tweet_piddir, mode=0755, owner='root', group='root', recursive=True)

    Execute('echo Copying script to ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'setup_nifi.sh ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'setup_twitter.sh ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'twitter_dashboard_v5.xml ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'banana_default.json ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'kiwi_default.json ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'twitterAll_configsets.tgz ' + params.tweet_installdir)
    Execute('cp -f ' + params.service_scriptsdir + 'twittersMap_configsets.tgz ' + params.tweet_installdir)

    Execute('tar -xf ' + params.tweet_installdir + '/twitterAll_configsets.tgz -C /opt/lucidworks-hdpsearch/solr/server/solr/configsets/')
    Execute('tar -xf ' + params.tweet_installdir + '/twittersMap_configsets.tgz -C /opt/lucidworks-hdpsearch/solr/server/solr/configsets/')

    Execute('/opt/lucidworks-hdpsearch/solr/bin/solr create -c twitterAll -d /opt/lucidworks-hdpsearch/solr/server/solr/configsets/data_driven_schema_configs_twitterAll/conf -n twitterAll -s 1 -rf 1')
    Execute('/opt/lucidworks-hdpsearch/solr/bin/solr create -c twittersMap -d /opt/lucidworks-hdpsearch/solr/server/solr/configsets/data_driven_schema_configs_twittersMap/conf -n twittersMap -s 1 -rf 1')

    Execute('cp -pR /opt/lucidworks-hdpsearch/solr/server/solr-webapp/webapp/banana /opt/lucidworks-hdpsearch/solr/server/solr-webapp/webapp/kiwi')
    Execute('cp ' + params.tweet_installdir + '/banana_default.json  /opt/lucidworks-hdpsearch/solr/server/solr-webapp/webapp/banana/app/dashboards/default.json')
    Execute('cp ' + params.tweet_installdir + '/kiwi_default.json /opt/lucidworks-hdpsearch/solr/server/solr-webapp/webapp/kiwi/app/dashboards/default.json')

    self.configure(env)
   
  def configure(self, env):
    import params
    import status_params
    env.set_params(params)
    env.set_params(status_params)
    user_env=InlineTemplate(status_params.user_env)
    File(params.tweet_installdir + '/user-env.sh', content=user_env, owner='root',group='root')
    tweet_env=InlineTemplate(params.tweet_env)
    File(params.tweet_installdir + '/tweet-env.sh', content=tweet_env, owner='root',group='root')


  def stop(self, env):
    import params
    import status_params
    import requests
    self.configure(env)
    f = open(status_params.tweet_pidfile,"r")
    p_group_id = f.read()
    f.close()
    host = params.nifi_master_host + ':' + str(params.nifi_port)
    version = requests.get('http://' + host + '/nifi-api/controller/revision').json()["revision"]["version"]
    req = 'http://' + host + '/nifi-api/controller/process-groups/root/process-group-references/' + p_group_id.strip()                
    r = requests.put(req, data={'running':'false', 'version':version, 'clientId':'demotweet'})
    Execute('rm ' + status_params.tweet_pidfile, ignore_failures=True)

  def start(self, env):
    import params
    import status_params
    self.configure(env)
    config_nifi_script = os.path.join(params.tweet_installdir,'setup_nifi.sh')
    nifi_template_xml = os.path.join(params.tweet_installdir,'twitter_dashboard_v5.xml')
    Execute ('pip install requests')
    if not os.path.exists(status_params.tweet_piddir):
        os.makedirs(status_params.tweet_piddir)
    #To change. Really bad!!!
    Execute ('echo Wait 30 seconds to let NiFi starts')
    Execute ('sleep 30')
    Execute ('chmod +x ' + config_nifi_script)
    Execute (config_nifi_script + ' ' + params.tweet_installdir + ' ' + nifi_template_xml + ' twitter_dashboard')
    config_twitter_script = os.path.join(params.tweet_installdir,'setup_twitter.sh')
    Execute ('chmod +x ' + config_twitter_script)
    Execute (config_twitter_script + ' ' + params.tweet_installdir + ' GetTwitter ')

  def status(self, env):
    import status_params
    self.check_flow_running(status_params.tweet_pidfile, "sandbox.hortonworks.com", "9090")




  def check_flow_running(self, pid_file, host, port):
    import requests
    if not pid_file or not os.path.isfile(pid_file):
      raise ComponentIsNotRunning()
    try:
      f = open(pid_file,"r")
      p_group_id = f.read()
      f.close()
      req = 'http://' + host + ':' + port + '/nifi-api/controller/process-groups/root/process-group-references/' + p_group_id.strip()
      r = requests.get(req)
      if r.status_code != requests.codes.ok:
        raise ComponentIsNotRunning()
      if r.json()["processGroup"]["runningCount"] < 26:
        raise ComponentIsNotRunning()
    except Exception, e:
      raise ComponentIsNotRunning()
    
if __name__ == "__main__":
  Master().execute() 
