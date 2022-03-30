#!/bin/bash
##############################################################################
# Script that runs the test via a udocker container.
#
# Please, first pull the image and create container!
# udocker pull $DOCKER_IMAGE
# udocker create --name=$UCONTAINER $DOCKER_IMAGE
##############################################################################

# ----------------------------------------------------------------------------
CONTAINER="o3sources:testing"
CONTAINER_STDOUT="$CONTAINER.out"
CONTAINER_STDERR="$CONTAINER.err"

# According to https://wiki.scc.kit.edu/hpc/index.php/ForHLR_-_Hardware_and_Architecture#LSDF_online_storage_2
# we can use $LSDF environment setting
SOURCES_FILE="$PWD/test_datafiles/sources.yaml"
SOURCES_FOLDER="$PWD/test_datafiles"
SKIMMED_FOLDER="$PWD/Skimmed"

DOCKER_OPTIONS="
    --user=application \
    --volume=${SOURCES_FILE}:/app/sources.yaml \
    --volume=${SOURCES_FOLDER}:/app/Sources \
    --volume=${SKIMMED_FOLDER}:/app/Skimmed \
    --env RUN_SKIMMING=True \
    --env RUN_METADATA=True \
    --env RUN_CFCHECKS=True \
"

CONTAINER_OPTIONS="
    --verbosity=DEBUG \
    --sources=Sources \
    --output=Skimmed \
"

##### RUN THE JOB ############################################################
echo"========================================================================"
echo "=> udocker container: $CONTAINER"
echo "=> Running on: $HOSTNAME"
echo "========================================================================"
EXECUTABLE="docker run --rm ${DOCKER_OPTIONS} ${CONTAINER} ${CONTAINER_OPTIONS}"

echo $EXECUTABLE
exec $EXECUTABLE \
    1>>${CONTAINER_STDOUT} \
    2>>${CONTAINER_STDERR}
echo "Done with the script."
