#!/bin/bash
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=10
#SBATCH --time=01:00:00
#SBATCH --mem=30gb
#SBATCH --export=ALL,MPI_MODULE=mpi/openmpi/3.1,EXECUTABLE=./ompi_omp_program
#SBATCH --output="parprog_hybrid_%j.out"

# Use when a defined module environment related to OpenMPI is wished
module load ${MPI_MODULE}
export MPIRUN_OPTIONS="--bind-to core --map-by socket:PE=${SLURM_CPUS_PER_TASK} -report-bindings"
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}
export NUM_CORES=${SLURM_NTASKS}*${SLURM_CPUS_PER_TASK}
echo "${EXECUTABLE} running on ${NUM_CORES} cores with ${SLURM_NTASKS} MPI-tasks and ${OMP_NUM_THREADS} threads"
startexe="mpirun -n ${SLURM_NTASKS} ${MPIRUN_OPTIONS} ${EXECUTABLE}"
echo $startexe
exec $startexe
