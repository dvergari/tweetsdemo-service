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

    Execute('echo Scriptdir is: ' + params.service_scriptsdir)

    Execute('echo installation directory is: ' + params.tweet_installdir)
    Execute('echo ambari host: ' + params.ambari_server_host)
    Execute('echo namenode host: ' + params.namenode_host)
    Execute('echo nimbus host: ' + params.nimbus_host)
    Execute('echo hive host: ' + params.hive_metastore_host)
    Execute('echo hbase host: ' + params.hbase_master_host)
    Execute('echo kafka broker: ' + params.kafka_broker_host)

    Directory(params.tweet_installdir, mode=0755, owner='root', group='root', recursive=True)

    Execute('echo Copying nifi flow to ' + params.nifi_dir + '/conf')
    Execute('cp -f ' + params.service_scriptsdir + '../resources/flow.xml.gz /opt/HDF-1.2.0.0/conf/')
    self.configure(env)
   
  def configure(self, env):
    import params
    user_env=InlineTemplate(params.user_env)
    File(params.tweet_installdir + '/user-env.sh', content=user_env, owner='root',group='root')
    nifi_env=InlineTemplate(params.nifi_env)


  def stop(self, env):
    Execute ('echo stop')

  def start(self, env):
    import params
    config_twitter_script = os.path.join(params.service_scriptsdir,'setup_twitter.sh')
    Execute ('chmod +x ' + config_twitter_script)
    Execute (config_twitter_script + ' ' + params.tweet_installdir + ' GetTwitter ' + params.consumer_key + ' ' + params.consumer_secret + ' ' + params.access_token + ' ' + params.access_secret)

  def status(self, env):
    Execute ('echo status')


if __name__ == "__main__":
  Master().execute() 
