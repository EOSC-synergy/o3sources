# o3sources

Sources file versioning repository. <br>
Branches and versions:
 
 - **master**: Last & official version of source.yaml file
 - **CCMI**: Only models from CCMI source

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

