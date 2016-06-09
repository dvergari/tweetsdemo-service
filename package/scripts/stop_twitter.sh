#!/bin/bash

export INSTALL_DIR=$1

source $INSTALL_DIR/user-env.sh

REVISION=`curl -H "Content-Type: application/json" http://$host/nifi-api/controller/revision 2>/dev/null| jq '.revision.version'`

P_GROUP_ID=`cat ${tweet_piddir}/twitter.group.pid`

curl -X PUT -H 'Content-Type: application/x-www-form-urlencoded' http://$host/nifi-api/controller/process-groups/root/process-group-references/$P_GROUP_ID -d "running=stop&version=$REVISION&clientId=demotweet"
