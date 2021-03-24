# o3sources

Sources file versioning repository. <br>
Branches and versions:
 
 - **master**: Last & official version of source.yaml file
 - **CCMI**: Only models from CCMI source


# Produce sources.yaml file from .csv (Google sheet)
To simplify maintenance of sources.yaml, a python script is created 
to generated from other typical table format (such csv).

This script collects the following columns to group them as the key
fields of the sources file:

- **source**: Sources the model belongs to (ie. CCMI-1).
- **model**: Model name for the data to skim (ei. ACCESS-CCM-refC2).
- **variable**: Variable to be skimmed (ei. tco3_zm).
- **name**: Variable name where to find the data on the original dataset.
- **paths**: Regex with the NetCDF files with the original dataset.
- **coordinates**: Array with variable coordinates map (ei. [time, lat, lon]).

The rest of columns are added as metadata at variable level.

Usage example:
```sh
$ ./sources.py -v INFO sources.csv 
2021-02-08 12:00:18,044  INFO     Reading document
2021-02-08 12:00:18,045  INFO     Grouping document sources
2021-02-08 12:00:18,046  INFO     Saving file to sources.yaml
2021-02-08 12:00:18,082  INFO     End of program
```

To get more information about usage use the `--help` command:
```sh
$ ./sources.py --help
```


# Run data skimming from sources.yaml file
This repository includes an script in charge of performing skimming over the 
models database. It comes in container format with the required tools 
installed so it can be deployed easily everywhere.

### 📝 Table of Contents
- [Build using docker](#build)
- [Run using udocker](#deployment)
- [Run with SLURM & MPI](#slurm)

### Prerequisites
To use the container, you need the following systems and container technologies:
- __Build machine__ with [docker](https://docs.docker.com/engine/install/) 
- __Runtime machine__ with [udocker](https://indigo-dc.gitbook.io/udocker/installation_manual)

> Note udocker cannot be used to build containers, only to run them. 


## Built using docker <a name = "build"></a>
Download the repository at the __Build machine__ using git.
```sh
$ git clone git@git.scc.kit.edu:synergy.o3as/o3sources.git
Cloning into 'o3sources'...
...
```
Build the docker image at the __Build machine__ using docker.
```sh
$ docker build --tag o3sources .
...
Successfully built 69587025a70a
Successfully tagged o3sources:latest
```
If the build process succeeded, you can list the image on the docker image list:
```sh
$ docker images
REPOSITORY                         TAG                 IMAGE ID            CREATED              SIZE
o3sources                          latest              69587025a70a        xx seconds ago      557MB
...
```

## Run using udocker <a name = "deployment"></a>
To deploy the the application using __udocker__ at the __Runtime machine__ you need:
 - Configuration file with a data structure description at the input path in [YAML](https://yaml.org/) format.
 - Mount the `/app/Data/sources.yaml` file with the configuration file.
 - Mount the `/app/Data` folder with the models data folder relative to the configuration file.

Once the requirement are completed, pull the image from the image registry.
For example, to pull it from the synergy-imk official registry use:
```sh
$ udocker pull o3as/o3sources
...
Downloading layer: sha256:a3ed95c....
...
```

Once the repository is added and the image downloaded, create the local container: 
```sh
$ udocker create --name=o3sources o3as/o3sources
fa42a912-b0d4-3bfb-987f-1c243863802d
```

Finally, run the container. Note the described _Data_, and _sources.yaml_ have
to be provided. Also it is needed to specify the user _application_ should run
inside the container:
```sh
$ udocker run \
  --user=application \
  --volume=${SOURCES_FILE}:/app/Data/sources.yaml \
  --volume=${DATA}:/app/Data \
  o3sources
...
executing: ompi_omp_program
...
2021-03-24 11:31:03,203 main ---- INFO     Reading source files sources.yaml
...
```

The service produces 2 output folders:
 - ${DATA}/Standard: With the standardized models.
 - ${DATA}/Skimmed: With the skimmed models.

For the main function description and commands help you can call:
```sh  
$ udocker run --user=application o3sources --help
...
```

## Running with SLURM and MPI <a name = "slurm"></a>
You can run the skimming process on SLURM and MPI environment. To do so, you
can edit the file ´job_ompi_omp.sh` with your configuration and call:

```sh
$ sbatch -p normal job_ompi_omp.sh
Submitted batch job .....
```

Note that to run the script you need to have udocker installed, configured and
a o3sources container available.

