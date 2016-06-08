#!/bin/bash

INSTALL_DIR=$1
SOURCE_TEMPLATE=$2
P_GROUP_NAME=$3


source $INSTALL_DIR/user-env.sh


## If the processor group already exists, do nothing
P_GROUP_ID=`curl -X GET http://$host/nifi-api/controller/search-results?q=$P_GROUP_NAME 2>/dev/null | jq '.searchResultsDTO.processGroupResults[0].id'`

[[ $P_GROUP_ID != "null" ]] && echo "Process Group $P_GROUP_NAME already exists" &&exit 0


## Import the template if the process group does not exist

TEMPLATE_ID=`curl -X POST http://$host/nifi-api/controller/templates -F template=@"$SOURCE_TEMPLATE" 2>/dev/null | grep -oPm1 "(?<=<id>)[^<]+"`

### Instanciate the template
REVISION=`curl -H "Content-Type: application/json" http://$host/nifi-api/controller/revision 2>/dev/null| jq '.revision.version'`
echo $REVISION

P_GROUP_ID=`curl -X POST -H "Content-Type: application/x-www-form-urlencoded" http://$host/nifi-api/controller/process-groups/root/template-instance -d "version=$REVISION&clientId=demotweet&templateId=$TEMPLATE_ID&originX=0&originY=0&process-group-id=root" 2>/dev/null | jq '.contents.processGroups[0].id'` 
echo "Created process group $P_GROUP_ID"


