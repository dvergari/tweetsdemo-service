#!/usr/bin/env python

from resource_management import *

config = Script.get_config()

tweet_piddir = config['configurations']['user-env']['tweet_piddir']
tweet_pidfile = format("{tweet_piddir}/twitter.group.pid")
user_env = config['configurations']['user-env']['content']
