#!/bin/bash

export INSTALL_DIR=$1
export PROCESSOR=$2


source $INSTALL_DIR/user-env.sh
source $INSTALL_DIR/tweet-env.sh

REVISION=`curl -H "Content-Type: application/json" http://$host/nifi-api/controller/revision 2>/dev/null| jq '.revision.version'`


PROCESSOR_ID=`curl http://${host}/nifi-api/controller/search-results?q=${PROCESSOR} 2>/dev/null | jq '.searchResultsDTO.processorResults[0].id' | tr -d '"'` 
P_GROUP_ID=`curl http://${host}/nifi-api/controller/search-results?q=${PROCESSOR}  2>/dev/null | jq '.searchResultsDTO.processorResults[0].groupId' | tr -d '"'`

echo "PROCESSOR_ID $PROCESSOR_ID"
echo "P_GROUP_ID $P_GROUP_ID"

JSON="{\"revision\": 
{\"clientId\": \"demotweet\",\"version\":$REVISION}, 
\"processor\": 
{\"id\": \"$PROCESSOR_ID\", 
\"config\": 
{\"properties\": 
{\"Consumer Key\": \"$CONSUMER_KEY\",
\"Consumer Secret\": \"$CONSUMER_SECRET\",
\"Access Token\": \"$ACCESS_TOKEN\",
\"Access Token Secret\": \"$ACCESS_TOKEN_SECRET\",
\"Terms to Filter On\": \"$FILTER_TERMS\"
}}}}"

echo $JSON

curl -X PUT -H "Content-Type: application/json" http://$host/nifi-api/controller/process-groups/$P_GROUP_ID/processors/$PROCESSOR_ID -d "$JSON" >/dev/null 2&>1

REVISION=`curl -H "Content-Type: application/json" http://$host/nifi-api/controller/revision 2>/dev/null| jq '.revision.version'`

curl -X PUT -H 'Content-Type: application/x-www-form-urlencoded' http://$host/nifi-api/controller/process-groups/root/process-group-references/$P_GROUP_ID -d "running=true&version=$REVISION&clientId=demotweet"
