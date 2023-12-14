# o3sources

Sources file versioning repository. <br>
Branches and versions:
 
 - **master**: Last & official version of source.csv file
 - **<>**: Specific release version


# Produce sources.csv file
To simplify maintenance of `sources.csv`, a the file is just a soft link
to the file `Data sources - Sources.csv`. This is the `standard` name
when downloading from sources such excel/sheets. The soft link is a simple
way to reference the file without spaces, which generate conflicts in
scripts.


# Run data skimming from sources file
This repository includes scripts in charge of performing checks and skimming
over the models database. They come as container format so can be executed
easily everywhere.

Additionally `Dockerfile` generates a container with all skimming tools
installed for additional purposes.


### 📝 Table of Contents
- [Build using docker](#build)
- [Run using udocker](#deployment)
- [Run with SLURM](#slurm)

### Prerequisites
To use the container, you need the following systems and container technologies:
- __Build machine__ with [docker](https://docs.docker.com/engine/install/) 
- __Runtime machine__ with [udocker](https://indigo-dc.gitbook.io/udocker/installation_manual)

> Note udocker cannot be used to build containers, only to run them. 


## Built using docker <a name = "build"></a>
Download the repository at the __Build machine__ using git.
```sh
$ git clone git@codebase.helmholtz.cloud:m-team/o3as/o3sources.git
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
Then you can use this container to execute the provided scripts or generate
images for each one, for example:
```sh
$ docker build --tag cfchecks --file Dockerfile.cfchecks .
...
Successfully built ...
Successfully tagged cfchecks:latest
```
```sh
$ docker build --tag tco3_zm --file Dockerfile.tco3_zm .
...
Successfully built ...
Successfully tagged tco3_zm:latest
```

You can build an image that executes each individual script by using targets:
 - `docker build --target o3sources -t o3sources:latest .`
 - `docker build --target cfchecks -t cfchecks:latest .`
 - `docker build --target tco3_zm -t tco3_zm:latest .`
 - `docker build --target vmro3_zm -t vmro3_zm:latest .`


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
> You can apply the same procedure for `cfchecks` and `tco3_zm` images.

Finally, run a container. Note the described _Data_, and _sources.yaml_ have
to be provided. Also it is needed to specify the user _application_ should run
inside the container:
```sh
$ udocker run \
  --user=application \
  --volume=${SOURCES_FILE}:/app/sources.csv \
  --volume=${SOURCES_FOLDER}:/app/Sources \
  --volume=${SKIMMED_FOLDER}:/app/Skimmed \
  o3as/tco3_zm:latest
...
2021-03-24 11:31:03,203 main ---- INFO     Reading source files sources.csv
...
```

For the script function description and commands help you can call:
```sh  
$ udocker run --user=application o3as/tco3_zm:latest --help
...
```

## Running with SLURM <a name = "slurm"></a>
You can run the skimming process on SLURM environment. To do so, you
can edit the file ´job_ompi_omp.sh` with your configuration and call:

```sh
$ sbatch -p <your_partition> job_ompi_omp.sh
Submitted batch job .....
```

> Note that to run the script you need to have udocker installed, configured and
> o3as/cfchecks, o3as/tco3_zm containers available.

