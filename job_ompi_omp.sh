#!/bin/bash
#SBATCH --job-name=o3sources
#SBATCH --output="parprog_hybrid_%j.out"
#SBATCH --constraint=LSDF
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=10
#SBATCH --time=01:00:00
#SBATCH --mem=30gb
#SBATCH --export=ALL,MPI_MODULE=mpi/openmpi/3.1

# Use when a defined module environment related to OpenMPI is wished
module load ${MPI_MODULE}
export MPIRUN_OPTIONS="--bind-to core --map-by socket:PE=${SLURM_CPUS_PER_TASK} -report-bindings"
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export NUM_CORES=${SLURM_NTASKS}*${SLURM_CPUS_PER_TASK}


##########
# Script that runs the test via a udocker container.
#
# Please, first pull the image and create container!
# udocker pull $DOCKER_IMAGE
# udocker create --name=$UCONTAINER $DOCKER_IMAGE
##########

# ------------------------
UDOCKER_DIR="$PROJECT/.udocker" # Location of udocker and containers
CONTAINER="o3sources"
CONTAINER_STDOUT="$CONTAINER.out"
CONTAINER_STDERR="$CONTAINER.err"

# According to https://wiki.scc.kit.edu/hpc/index.php/ForHLR_-_Hardware_and_Architecture#LSDF_online_storage_2
# we can use $LSDF environment setting
SOURCES_FILE="${LSDF}/kit/imk-asf/projects/O3as/03sources/sources.yaml"
MODELS_FOLDER="${LSDF}/kit/imk-asf/projects/O3as"

UDOCKER_OPTIONS="
    --user=application \
    --volume=${SOURCES_FILE}:/app/Data/sources.yaml \
    --volume=${MODELS_FOLDER}:/app/Data \
    --env RUN_STANDARD=True \
    --env RUN_SKIMMING=True \
    --env RUN_METADATA=True"

CONTAINER_OPTIONS="
    --verbosity=DEBUG"

##### RUN THE JOB #####
echo "==========================================="
echo "=> udocker container: $CONTAINER"
echo "=> Running on: $HOSTNAME"
echo "=> With: Cores     == ${NUM_CORES}"
echo "         MPI-tasks == ${SLURM_NTASKS}"
echo "=>       Threads   == ${OMP_NUM_THREADS}"
echo "==========================================="

#echo "Setting up F3 execmode"
#udocker setup --execmode=F3 $UCONTAINER  # Setup another execmode, if needed

EXECUTABLE="udocker run ${UDOCKER_OPTIONS} ${CONTAINER} ${CONTAINER_OPTIONS}"

startexe="mpirun -n ${SLURM_NTASKS} ${MPIRUN_OPTIONS} ${EXECUTABLE}"
echo $startexe
exec $startexe \
1>> ${CONTAINER_STDOUT} \
2>> ${CONTAINER_STDERR}
echo "Done with the script."
