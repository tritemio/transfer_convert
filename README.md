# transfer_convert

A collection of scripts for automating conversion to Photon-HDF5,
archival and analysis of smFRET measurements using multiprocessing (each file
is processed in a different CPU).

A brief description of each script follows.

## batch_convert.py

Convert all files in a specified folder in batch.
If the `--monitor` argument is passed, monitors a given folder.
When a new YAML file appears in the same folder with the same name as
a data file, it starts these processing steps:

- copy the data to a temp folder
- convert data to Photon-HDF5 using the metadata from the YAML file
- copy all files to and archival folder
- optionally run smFRET analysis

Data files can be processed in parallel.

Type `./batch_convert.py -h` for more info on how to use the script.

## batch_analyze.py

Analyze all the Photon-HDF5 files in a given folder using a default notebook
or any other specified notebook. Multiple files can be processed in parallel.
For optimal performances it is suggested to do not exceed the number of CPUs.

Type `./batch_analysis.py -h` for more info on how to use the script.

## analize.py

Analyze a single Photon-HDF5 file using a the specified notebook.

Type `./analyze.py -h` for more info on how to use the script.


## transfer.py

Module used for processing a single file (copy, conversion, analysis).
The script `monitor.py` build a multiprocessing pool and calls functions
defined in `transfer.py` to process several files in parallel.

# Installation

Download the repository and run the scripts directly from the repo folder
(no installation).

## Dependencies

- python 3.6 (older versions may work)
- jupyter notebook 5+
- jupyter nbconvert 5+
- [pyyaml](http://pyyaml.org/)
- [tqdm](https://github.com/tqdm/tqdm) (progress bar)
- [FRETBursts](http://tritemio.github.io/FRETBursts/) 0.6.3+
- [phconvert](https://photon-hdf5.github.io/phconvert/) 0.7.3+
- [niconverter](https://github.com/tritemio/niconverter/tree/master)

See also [conda_environment_linux.yml](https://github.com/tritemio/transfer_convert/blob/master/conda_environment_linux.yml).

# Cite

If you use this code for a publication please cite as:

> Multispot single-molecule FRET: High-throughput analysis of freely diffusing molecules <br>
> Ingargiola et al., PLOS ONE (2016), doi:[10.1371/journal.pone.0175766](https://doi.org/10.1371/journal.pone.0175766)

----
Copyright (C) 2017 The Regents of the University of California, Antonino Ingargiola and contributors.

*This work was supported by NIH grants R01 GM069709 and R01 GM095904.*



