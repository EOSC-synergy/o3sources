#!/bin/bash
#SBATCH --job-name=o3sources
#SBATCH --output="parprog_hybrid_%j.out"
#SBATCH --constraint=LSDF
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=10
#SBATCH --time=01:00:00
#SBATCH --mem=30gb
#SBATCH --partition=cpuonly

##############################################################################
# Script that runs the test via a udocker container.
#
# Please, first pull the image and create container!
# udocker pull $DOCKER_IMAGE
# udocker create --name=$UCONTAINER $DOCKER_IMAGE
##############################################################################

# ----------------------------------------------------------------------------
CONTAINER="o3skim_dev"
CONTAINER_STDOUT="$CONTAINER.out"
CONTAINER_STDERR="$CONTAINER.err"

# According to https://wiki.scc.kit.edu/hpc/index.php/ForHLR_-_Hardware_and_Architecture#LSDF_online_storage_2
# we can use $LSDF environment setting
SOURCES_FILE="${LSDF}/kit/imk-asf/projects/O3as/03sources/sources.yaml"
SOURCES_FOLDER="${LSDF}/kit/imk-asf/projects/O3as"
SKIMMED_FOLDER="${LSDF}/kit/imk-asf/projects/O3as/Skimmed-dev"

UDOCKER_OPTIONS="
    --user=application \
    --volume=${SOURCES_FILE}:/app/sources.yaml \
    --volume=${SOURCES_FOLDER}:/app/Sources \
    --volume=${SKIMMED_FOLDER}:/app/Skimmed \
    --env RUN_SKIMMING=True \
    --env RUN_METADATA=True \
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
echo "=> Account name: $SLURM_JOB_ACCOUNT"
echo "=> With: Processes per node  == ${SLURM_JOB_CPUS_PER_NODE}"
echo "=>       Nodes dedicated     == ${SLURM_JOB_NUM_NODES}"
echo "=>       Memory per node     == ${SLURM_MEM_PER_NODE}"
echo "=>       Processes dedicated == ${SLURM_NPROCS}"
echo "=>       CPUs per task       == ${SLURM_CPUS_PER_TASK}"
echo "=>       Tasks available     == ${SLURM_NTASKS}"
echo "========================================================================"

#echo "Setting up F3 execmode"
#udocker setup --execmode=F3 $UCONTAINER  # Setup another execmode, if needed
EXECUTABLE="udocker run ${UDOCKER_OPTIONS} ${CONTAINER} ${CONTAINER_OPTIONS}"

echo $EXECUTABLE
exec $EXECUTABLE \
    1>>${CONTAINER_STDOUT} \
    2>>${CONTAINER_STDERR}
echo "Done with the script."
