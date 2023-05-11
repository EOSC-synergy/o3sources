#!/bin/bash
#SBATCH --job-name=o3sources
#SBATCH --output="parprog_hybrid_%j.out"
#SBATCH --constraint=LSDF
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=10:00:00
#SBATCH --mem=30gb
#SBATCH --partition=cpuonly

##############################################################################
# Script that runs the test via a udocker container.
#
# Please, first pull the image and create container!
# udocker pull $DOCKER_IMAGE
# udocker create --name=$UCONTAINER $DOCKER_IMAGE
##############################################################################

echo "========================================================================"
echo "=> Account name: $SLURM_JOB_ACCOUNT"
echo "=> Running on: $HOSTNAME"
echo "=> With: Processes per node  == ${SLURM_JOB_CPUS_PER_NODE}"
echo "=>       Nodes dedicated     == ${SLURM_JOB_NUM_NODES}"
echo "=>       Memory per node     == ${SLURM_MEM_PER_NODE}"
echo "=>       Processes dedicated == ${SLURM_NPROCS}"
echo "=>       CPUs per task       == ${SLURM_CPUS_PER_TASK}"
echo "=>       Tasks available     == ${SLURM_NTASKS}"


##### SCRIPT VARIABLES #######################################################
SOURCES_FILE="${PWD}/o3as/03sources/sources.csv"
SOURCES_FOLDER="${PWD}/o3as"
SKIMMED_FOLDER="${PWD}/o3as/Skimmed-dev"

UDOCKER_OPTIONS="
    --user=application \
    --volume=${SOURCES_FILE}:/app/sources.csv \
    --volume=${SOURCES_FOLDER}:/app/Sources \
    --volume=${SKIMMED_FOLDER}:/app/Skimmed \
"

CONTAINER_OPTIONS="
    --sources_file=sources.csv
    --sources=Sources \
    --output=Skimmed \
    --verbosity=INFO \
"


##### SKIM JOB - CFCHECKS ####################################################
CONTAINER="cfchecks"
CONTAINER_STDOUT="$CONTAINER.out"
CONTAINER_STDERR="$CONTAINER.err"

#echo "Setting up F3 execmode"
#udocker setup --execmode=F3 $UCONTAINER  # Setup another execmode, if needed
EXECUTABLE="udocker run ${UDOCKER_OPTIONS} ${CONTAINER} ${CONTAINER_OPTIONS}"

echo "========================================================================"
echo "=> udocker container: $CONTAINER"
echo $EXECUTABLE
$EXECUTABLE \
    1>>${CONTAINER_STDOUT} \
    2>>${CONTAINER_STDERR}
echo "Checks job ended."


##### SKIM JOB - TCO3 ########################################################
CONTAINER="tco3_zm"
CONTAINER_STDOUT="$CONTAINER.out"
CONTAINER_STDERR="$CONTAINER.err"

#echo "Setting up F3 execmode"
#udocker setup --execmode=F3 $UCONTAINER  # Setup another execmode, if needed
EXECUTABLE="udocker run ${UDOCKER_OPTIONS} ${CONTAINER} ${CONTAINER_OPTIONS}"

echo "========================================================================"
echo "=> udocker container: $CONTAINER"
echo $EXECUTABLE
$EXECUTABLE \
    1>>${CONTAINER_STDOUT} \
    2>>${CONTAINER_STDERR}
echo "Skim job tco3 ended."


##### SKIM JOB - VMRO3 #######################################################
CONTAINER="vmro3_zm"
CONTAINER_STDOUT="$CONTAINER.out"
CONTAINER_STDERR="$CONTAINER.err"

#echo "Setting up F3 execmode"
#udocker setup --execmode=F3 $UCONTAINER  # Setup another execmode, if needed
EXECUTABLE="udocker run ${UDOCKER_OPTIONS} ${CONTAINER} ${CONTAINER_OPTIONS}"

echo "========================================================================"
echo "=> udocker container: $CONTAINER"
echo $EXECUTABLE
$EXECUTABLE \
    1>>${CONTAINER_STDOUT} \
    2>>${CONTAINER_STDERR}
echo "Skim job vmro3 ended."
